"""Add inferred source-rim transition faces strictly on the hole side.
Source mesh, material, UV and texture pixels are never changed.
"""
import sys,json,math,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W/'v6_reality_inventory')]
import numpy as np,shapely,mapbox_earcut
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import nearest_points
from nearest_photo_projection import PhotoProjector,closest_on_triangles
O=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid');C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf-8'));a=math.radians(C['rotation_deg']);c=math.cos(a);s=math.sin(a);R=np.array([[c,-s,0],[s,c,0],[0,0,1]]);origin=np.array(C['origin'])
h=json.loads((O/'02_Data/Hole_Polygon.json').read_text(encoding='utf-8'));H=Polygon(h['local']['outer'],h['local']['holes'])
tree=ast.parse((W/'build_v6_patch.py').read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['polys','polygon_tris','clip_half','clipped']],type_ignores=[]),'<clip helpers>','exec'))
I=[r for r in json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8')) if r['name']!='PHOTO_RIM_TRANSITION']
tt=[]
for row in I:
 if row['name'].startswith('PHOTO_BOUNDARY_'):
  d=np.load(O/'02_Data'/row['file']);tt.append(d['vertices'][d['faces']])
t=np.concatenate(tt);P=PhotoProjector(t,np.tile(np.array([[0,0],[1,0],[0,1]])[None,:,:],(len(t),1,1)),np.zeros(len(t),np.int32),{})
B=json.loads((O/'02_Data/Base_Index.json').read_text(encoding='utf-8'));M=json.loads((O/'02_Data/Materials.json').read_text(encoding='utf-8'))
tri=[];uv=[];mat=[];edge_count=0;dist_before=[];inside_core=H.buffer(-.04)
for bi,b in enumerate(B):
 d=np.load(O/'02_Data'/f'Base_{bi}.npz');v=(d['vertices']-origin)@R;f=d['faces'];vu=d['uv']
 fs=[f[:,[0,1]],f[:,[1,2]],f[f[:,2]==f[:,3]][:,[2,0]],f[f[:,2]!=f[:,3]][:,[2,3]],f[f[:,2]!=f[:,3]][:,[3,0]]]
 fi=[np.arange(len(f)),np.arange(len(f)),np.flatnonzero(f[:,2]==f[:,3]),np.flatnonzero(f[:,2]!=f[:,3]),np.flatnonzero(f[:,2]!=f[:,3])]
 edges=np.sort(np.concatenate(fs),axis=1);face_ids=np.concatenate(fi);ue,first,counts=np.unique(edges,axis=0,return_index=True,return_counts=True);ed=ue[counts==1];faceid=face_ids[first[counts==1]]
 pts=v[ed];near=shapely.distance(shapely.points(pts[:,:,:2].mean(axis=1)),H.exterior)<=1e-5
 ed=ed[near];faceid=faceid[near];pts=pts[near]
 segments=[];segment_face=[]
 for j,edge in enumerate(pts):
  count=max(1,int(math.ceil(np.linalg.norm(edge[1]-edge[0])/.05)))
  pp=edge[0]+np.linspace(0,1,count+1)[:,None]*(edge[1]-edge[0])
  for k in range(count):
   seg=pp[k:k+2]
   if shapely.distance(Point(seg[:,:2].mean(axis=0)),H.exterior)<=1e-5:
    segments.append(seg);segment_face.append(faceid[j])
 if not segments:continue
 pts=np.array(segments);mid=pts.mean(axis=1)
 qq=P.query(np.concatenate([pts.reshape(-1,3),mid]),max_distance=10,k=128,batch_size=512)
 dd=np.maximum(qq['distance'][:len(pts)*2].reshape(-1,2).max(axis=1),qq['distance'][len(pts)*2:])
 chosen=np.flatnonzero(dd>.005)
 for j in chosen:
  A,Bp=pts[j];targetxy=np.array([nearest_points(inside_core,Point(p[:2]))[0].coords[0] for p in [A,Bp]])
  guess=np.column_stack([targetxy,pts[j,:,2]])
  near=P.query(guess,max_distance=10,k=128)
  targets=[]
  for k in range(2):
   targettri=P.triangles[P.original_triangle_ids==near['source_triangle'][k]][:1]
   q0,_,_=closest_on_triangles(guess[k:k+1],targettri)
   # Force the transition onto the hole side instead of producing an almost
   # vertical, numerically ambiguous face exactly along the projection rim.
   targets.append(np.array([targetxy[k,0],targetxy[k,1],q0[0,2]]))
  Ap,Bpp=targets
  face=f[segment_face[j],:3];sv=v[face];su=vu[face];e1=sv[1]-sv[0];e2=sv[2]-sv[0];basis=np.stack([e1,e2],axis=1)
  # Linear UV extension from the adjoining original source facet. These new
  # transition pixels are inferred; no source atlas is rewritten or retouched.
  for t0 in [np.array([A,Bp,Bpp]),np.array([A,Bpp,Ap])]:
   if np.linalg.norm(np.cross(t0[1]-t0[0],t0[2]-t0[0]))<1e-10:continue
   for tc in clipped(t0,H):
    if np.linalg.norm(np.cross(tc[1]-tc[0],tc[2]-tc[0]))<1e-10:continue
    coeff=np.linalg.lstsq(basis,(tc-sv[0]).T,rcond=None)[0].T
    uv0=su[0]+coeff[:,0,None]*(su[1]-su[0])+coeff[:,1,None]*(su[2]-su[0])
    tri.append(tc);uv.append(uv0);mat.append('BASE_PHOTO_'+str(bi))
  edge_count+=1;dist_before.append(float(dd[j]))
 key='BASE_PHOTO_'+str(bi);M[key]={'color':[255,255,255],'roughness':1,'texture':b['texture'],'source_texture':b['source_texture'],'base_material_index':b['material_index'],'role':'Existing unchanged base photo material reused only on inferred hole-side transition faces'}
if tri:
 ms=list(dict.fromkeys(mat));verts=np.array(tri).reshape(-1,3);fn='Patch_Rim_Transition.npz'
 np.savez_compressed(O/'02_Data'/fn,vertices=verts,faces=np.arange(len(verts),dtype=np.int32).reshape(-1,3),uv=np.array(uv).reshape(-1,2),material_ids=np.array([ms.index(m) for m in mat],np.int32))
 el={'name':'PHOTO_RIM_TRANSITION','layer':'60_SITE','family':'SITE_MODEL','confidence':'MEDIUM','status':'INFERRED_TRANSITION','source':'New faces connect original cut rim to recovered old photo surface on hole side; source arrays/materials/photos unchanged; UV linearly extended from source facet'}
 I.append(dict(index=len(I),file=fn,name=el['name'],element=el,materials=ms,triangles=len(tri),vertices=len(verts),role='INFERRED_HOLE_SIDE_RIM_TRANSITION',photo_triangles=len(tri)))
for key in list(M):
 if key.startswith('BASE_PHOTO_') and key not in mat:del M[key]
outside=shapely.union_all(shapely.polygons(np.array(tri)[:,:,:2])).difference(H).area if tri else 0
assert outside<1e-7
(O/'02_Data/Patch_Index.json').write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf-8');(O/'02_Data/Materials.json').write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding='utf-8')
report={'source_modified':False,'rim_edges_with_added_transition':edge_count,'new_triangles':len(tri),'largest_original_endpoint_gap_m':max(dist_before) if dist_before else 0,'new_projection_outside_hole_m2':outside,'geometry_status':'Inferred transition between measured source rim and recovered photo mesh. Independent objects, no source welding.','uv_status':'Linear extension of original adjoining face UV; original photograph bits unchanged, patch pixels are not newly surveyed'}
(O/'06_Report/Rim_Transition_Repair.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
qa=json.loads((O/'06_Report/Patch_Clip_And_Photo_QA.json').read_text(encoding='utf-8'));qa['counts'].update(patch_nodes=len(I),patch_triangles=sum(r['triangles'] for r in I),photo_projected_triangles=sum(r.get('photo_triangles',0) for r in I));qa['rim_transition']=report;(O/'06_Report/Patch_Clip_And_Photo_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
