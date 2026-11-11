"""Regenerate V9 changed roof nodes only; inherit current V8 base, ground, rim and UV intact."""
import sys,json,math,ast,shutil,copy,collections
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W),str(W/'v6_reality_inventory')]
import numpy as np,mapbox_earcut
from shapely.geometry import Polygon,LineString,Point
from nearest_photo_projection import PhotoProjector
import export_v5 as ex
O=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid');V6=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid')
S=json.loads((O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));ex.SCENE=S;ex.MATS=S['materials']
incremental=True
change=json.loads((O/'02_Data'/'V9_Changed_Nodes.json').read_text());changed=set(change['changed']);removed=set(change['removed'])
if not incremental:
 for folder in ['01_Source','03_Textures']:shutil.copytree(V6/folder,O/folder,dirs_exist_ok=True)
 for p in (V6/'02_Data').iterdir():
  if p.is_file() and p.name!='Patch_Index.json':shutil.copy2(p,O/'02_Data'/p.name)
C=json.loads((O/'02_Data/Coordinate.json').read_text());a=math.radians(C['rotation_deg']);c=math.cos(a);s=math.sin(a);T=np.eye(4);T[:3,:3]=[[c,-s,0],[s,c,0],[0,0,1]];T[:3,3]=C['origin']
hp=json.loads((O/'02_Data/Hole_Polygon.json').read_text());
from shapely.ops import unary_union
scope=json.loads((O/'02_Data/V9_Allowed_Repair_Scope.json').read_text(encoding='utf-8'))
H=unary_union([Polygon(p['outer'],p.get('holes',[])) for p in scope['polygons']])
tree=ast.parse((W/'build_v6_patch.py').read_text(encoding='utf-8'));fun=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['polys','polygon_tris','clip_half','clipped','split']];exec(compile(ast.Module(fun,type_ignores=[]),'<clip_helpers>','exec'))
I=[r for r in json.loads(((O if incremental else V6)/'02_Data/Patch_Index.json').read_text(encoding='utf-8')) if r['name'] not in changed|removed]
print('Inherited',len(I),'unchanged patch nodes; loading photo projector',flush=True)
P=PhotoProjector.from_objs(sorted(Path(r'E:\jz\JIA\Productions\Production_OBJ (2)\Data').rglob('*.obj')),np.linalg.inv(T));sub={k:PhotoProjector(P.triangles[P.material_ids==k],P.uv[P.material_ids==k],P.material_ids[P.material_ids==k],P.materials) for k in P.materials}
M=json.loads((O/'02_Data/Materials.json').read_text(encoding='utf-8'));M.update(S['materials'])
for m in M.values():
 if m.get('texture') and str(V6) in m['texture']:m['texture']=m['texture'].replace(str(V6),str(O))
report=[]
for e in S['elements']:
 if e['name'] not in changed or e['name'].startswith('CONSTRUCTION_'):continue
 if e['layer'] in ['99_HELPER','90_UNCERTAIN'] or e['confidence']=='LOW':continue
 tri=[];base=[];eligible=[]
 for part in ex.expand_parts(e):
  v,faces=ex.world_part(part,e)
  if v is None:continue
  # The source gate atlas includes bright red door paint beside gray eaves.
  # Nearest-surface transfer is unsuitable for the new small gray ornaments.
  # Preserve their photograph-observed finish rather than sampling adjacent paint.
  photo=part['material'] not in ['M_Glass_Clear','M_Glass_Frosted','M_Ceramic_Warm','M_Wall_Exterior','M_Stone','M_Wall_Interior','M_Timber_Dark_Eave'] and not e['name'].startswith('SITE_GATEHOUSE_') and e['layer'] not in ['11_WALL_INT','30_DOOR','31_WINDOW','40_STAIR','70_EQUIPMENT']
  for face in faces:
   ids=ex.triangulate(v[face]) if len(face)>3 else [[0,1,2]]
   for ids0 in ids:
    t=v[[face[k] for k in ids0]]
    if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))<1e-10:continue
    for tt in clipped(t,H):
     if np.linalg.norm(np.cross(tt[1]-tt[0],tt[2]-tt[0]))<1e-10:continue
     for ttt in (split(tt) if photo else [tt]):tri.append(ttt);base.append(part['material']);eligible.append(photo)
 if not tri:print('outside',e['name'],flush=True);continue
 tri=np.array(tri);norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm/=np.linalg.norm(norm,axis=1)[:,None];uv=np.zeros((len(tri),3,2));names=base[:]
 for j,t in enumerate(tri):uv[j]=t[:,[k for k in range(3) if k!=int(np.argmax(abs(norm[j])))]]
 pp=np.flatnonzero(eligible)
 if len(pp):
  q=P.query(tri[pp].reshape(-1,3),np.repeat(norm[pp],3,axis=0),max_distance=.35,min_normal_dot=.65,k=16)
  match=q['matched'].reshape(-1,3).all(axis=1);mi=q['material_id'].reshape(-1,3);match&=(mi==mi[:,0:1]).all(axis=1);quv=q['uv'].reshape(-1,3,2);match&=np.ptp(np.nan_to_num(quv,nan=1e20),axis=1).max(axis=1)<.12
  for j in np.flatnonzero(match):idx=pp[j];uv[idx]=quv[j];names[idx]='PATCH_PHOTO_'+str(int(mi[j,0]))
 # Small roof tile normals do not follow the scanned roof plane; select one
 # atlas at each centroid then require all vertices within the 0.5m gate.
 if 'TILE' in e['name'] and e['layer']=='50_ROOF':
  sel=np.array([j for j,m in enumerate(names) if m=='M_Roof' and norm[j,2]>-.3],int)
  if len(sel):
   q=P.query(tri[sel].mean(axis=1),max_distance=.5,k=32)
   for mi,projector in sub.items():
    ids=sel[np.flatnonzero(q['matched']&(q['material_id']==mi))]
    if not len(ids):continue
    r=projector.query(tri[ids].reshape(-1,3),max_distance=.5,k=48);quv=r['uv'].reshape(-1,3,2);good=r['matched'].reshape(-1,3).all(axis=1)&(np.ptp(np.nan_to_num(quv,nan=1e20),axis=1).max(axis=1)<.12)
    for j in np.flatnonzero(good):uv[ids[j]]=quv[j];names[ids[j]]='PATCH_PHOTO_'+str(mi)
 ms=list(dict.fromkeys(names));mid=np.array([ms.index(m) for m in names],np.int32);fn='V9_'+e['name']+'.npz'
 vv=tri.reshape(-1,3);ff=np.arange(len(vv),dtype=np.int32).reshape(-1,3)
 np.savez_compressed(O/'02_Data'/fn,vertices=vv,faces=ff,uv=uv.reshape(-1,2),material_ids=mid)
 row=dict(index=len(I),name=e['name'],file=fn,element={k:v for k,v in e.items() if k!='parts'},materials=ms,triangles=len(tri),vertices=len(vv),photo_triangles=sum(m.startswith('PATCH_PHOTO') for m in names),role='V9_LOCAL_EAVE_JOINT_REPAIR')
 I.append(row);report.append({k:row[k] for k in ['name','triangles','photo_triangles']});print(report[-1],flush=True)
# Base index paths also point at the V7 companion textures; image pixels match.
BI=json.loads((O/'02_Data/Base_Index.json').read_text(encoding='utf-8'))
for r in BI:r['texture']=r['texture'].replace(str(V6),str(O))
(O/'02_Data/Base_Index.json').write_text(json.dumps(BI,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'02_Data/Materials.json').write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'02_Data/Patch_Index.json').write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'06_Report'/('Patch_Incremental_Revision_V9.json' if incremental else 'Patch_Revision_V7.json')).write_text(json.dumps(dict(inherited_nodes=len(I)-len(report),regenerated=report,removed=sorted(removed),base_meshes_modified=False,ground_and_rim_data_unchanged=True,total_triangles=sum(r['triangles'] for r in I),total_photo_triangles=sum(r.get('photo_triangles',0) for r in I)),ensure_ascii=False,indent=2),encoding='utf-8')
print('Patch V9 done',len(I),'nodes',sum(r['triangles'] for r in I),'triangles',flush=True)
