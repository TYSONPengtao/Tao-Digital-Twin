import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs']]
import numpy as np,rhino3dm as rh
O=Path(r'E:/jz/JIA/Rebuild_V16');D=W/'v16';P=O/'04_Rhino/Architecture_Complete_V16_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));I=json.loads((O/'02_Data/Native_Readback_Index_V16.json').read_text(encoding='utf8'));ii={r['name']:r for r in I};AQ=json.loads((O/'06_Report/V16_Assembly_QA.json').read_text(encoding='utf8'));S=json.loads((O/'08_Editable_Source/Architecture_Scene_V16.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']};C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);seg=json.loads((D/'Drain_Segments.json').read_text(encoding='utf8'));aa=np.array([r['outer_a'] for r in seg]);bb=np.array([r['outer_b'] for r in seg]);du=bb-aa;ll=(du*du).sum(1);zz=np.array([[r['za'],r['zb']] for r in seg]);report=[]
def gh(g):return hashlib.sha256(json.dumps(g.Encode(),sort_keys=True).encode()).hexdigest()
for n,r in ii.items():
 if not n.startswith('SITE_V14_ORIGINAL_EXTERIOR'):continue
 d=np.load(O/'02_Data'/r['file']);v=d['vertices'].copy();f=d['faces'].copy();uv=d['uv'].copy();changed=0
 for k in range(0,len(v),4096):
  p=v[k:k+4096];s=np.clip(((p[:,None,:2]-aa)*du).sum(2)/ll,0,1);dist=np.linalg.norm(aa+du*s[:,:,None]-p[:,None,:2],axis=2);idx=np.argmin(dist,axis=1);rows=np.arange(len(p));expected=zz[idx,0]+s[rows,idx]*(zz[idx,1]-zz[idx,0]);error=abs(p[:,2]-expected);ok=(dist[rows,idx]<1e-6)&(error<.7);changed+=int((ok&(error>1e-7)).sum());p[ok,2]=expected[ok]
 if not changed:continue
 t=v[f];good=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-11;removed=int((~good).sum());f=f[good];used=np.unique(f);remap=np.full(len(v),-1,np.int32);remap[used]=np.arange(len(used));v=v[used];uv=uv[used];f=remap[f]
 mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True
 for p,u in zip(v@R.T+origin,uv):mm.Vertices.AddPoint3d(*map(float,p));mm.TextureCoordinates.__add__(*map(float,u))
 for tri in f:mm.Faces.AddFace(*map(int,tri))
 mm.Normals.ComputeNormals();mm.Normals.UnitizeNormals();assert mm.IsValid
 old=next(ob for ob in F.Objects if ob.Attributes.Name==n+'__1');at=old.Attributes;F.Objects.Delete(at.Id);ident=F.Objects.Add(mm,at)
 for rec in AQ['created']:
  if rec['node']==n:rec['id']=str(ident);rec['geometry_hash']=gh(mm)
 nv=(np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R;nu=np.array([[p.X,p.Y] for p in mm.TextureCoordinates]);nn=np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R;np.savez_compressed(O/'02_Data'/r['file'],vertices=nv,faces=f,uv=nu,normals=nn,material_ids=np.zeros(len(f),np.int32));r['triangles']=len(f);E[n]['parts']=[{'geometry':{'type':'mesh','vertices':v.tolist(),'faces':f.tolist(),'uv':uv.tolist()},'material':r['materials'][0]}];E[n]['v16_boundary_stitch']='Road cut vertices including steep scan-bank facets stitched to exact gutter outside edge; UV preserved';report.append({'node':n,'stitched_edge_vertices':changed,'collapsed_degenerate_scan_faces_removed':removed});print('STITCHED',report[-1],flush=True)
md=json.loads((O/'02_Data/Native_Render_Materials.json').read_text(encoding='utf8'))
for n,m in S['materials'].items():
 if n in md:m['native_bitmap']=md[n]['native_bitmap'];m['native_bump']=md[n]['native_bump']
sp=O/'08_Editable_Source/Architecture_Scene_V16.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V16_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();assert F.Write(str(P),8)
for n in ['Native_Readback_Index_V16.json','Modeled_Index_V16.json']:(O/'02_Data'/n).write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf8')
(O/'06_Report/V16_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/V16_Stitched_Edge_QA.json').write_text(json.dumps({'status':'STITCHED_AWAITING_FRESH_CONTACT_CHECK','nodes':report},indent=2),encoding='utf8');print('BOUNDARY STITCH SAVED',flush=True)
