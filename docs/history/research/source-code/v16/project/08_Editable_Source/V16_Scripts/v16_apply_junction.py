import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
O=Path(r'E:/jz/JIA/Rebuild_V16');D=W/'v16';P=O/'04_Rhino/Architecture_Complete_V16_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));I=json.loads((O/'02_Data/Native_Readback_Index_V16.json').read_text(encoding='utf8'));ii={r['name']:r for r in I};Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'));AQ=json.loads((O/'06_Report/V16_Assembly_QA.json').read_text(encoding='utf8'));S=json.loads((O/'08_Editable_Source/Architecture_Scene_V16.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']};ex.SCENE=S;C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);seg=json.loads((D/'Drain_Segments.json').read_text(encoding='utf8'));aa=np.array([r['outer_a'] for r in seg]);bb=np.array([r['outer_b'] for r in seg]);du=bb-aa;ll=(du*du).sum(1);zz=np.array([[r['za'],r['zb']] for r in seg]);records=[]
for e in Q['replace']+Q['add']:
 n=e['name']
 if n=='SITE_V16_GRADED_INTERIOR_SOIL':continue
 source='native_source_file' in e;old=next(ob for ob in F.Objects if ob.Attributes.Name==n+'__1');at=old.Attributes;mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True
 if source:
  d=np.load(D/e['native_source_file']);v=d['vertices'].copy();ff=d['faces'].copy();uv=d['uv'].copy()
  for k in range(0,len(v),4096):
   p=v[k:k+4096];s=np.clip(((p[:,None,:2]-aa)*du).sum(2)/ll,0,1);dist=np.linalg.norm(aa+du*s[:,:,None]-p[:,None,:2],axis=2);ix=np.argmin(dist,axis=1);rr=np.arange(len(p));road=zz[ix,0]+s[rr,ix]*(zz[ix,1]-zz[ix,0]);ok=(dist[rr,ix]<1e-6)&(abs(p[:,2]-road)<.7);p[ok,2]=road[ok]
  t=v[ff];ff=ff[np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-11];used=np.unique(ff);remap=np.full(len(v),-1,np.int32);remap[used]=np.arange(len(used));v=v[used];uv=uv[used];ff=remap[ff]
  for p,u in zip(v@R.T+origin,uv):mm.Vertices.AddPoint3d(*map(float,p));mm.TextureCoordinates.__add__(*map(float,u))
  for tri in ff:mm.Faces.AddFace(*map(int,tri))
  e['parts']=[{'geometry':{'type':'mesh','vertices':v.tolist(),'faces':ff.tolist(),'uv':uv.tolist()},'material':ii[n]['materials'][0]}]
 else:
  v,fs,_,_=ex.solid_data(e['parts'][0]['geometry']);ff=[]
  for f in fs:ff.extend([[f[k] for k in tt] for tt in ex.triangulate(v[f])] if len(f)>3 else [f])
  ff=np.array(ff,np.int32);assert v[:,0].min()>-28 and v[:,0].max()<25 and v[:,1].min()>-21 and v[:,1].max()<14,(n,v.min(0),v.max(0))
  for k,tri in enumerate(ff):
   q=v[tri];no=np.cross(q[1]-q[0],q[2]-q[0]);axes=[j for j in range(3) if j!=int(np.argmax(abs(no)))];uv0=q[:,axes]
   for p,u in zip(q@R.T+origin,uv0):mm.Vertices.AddPoint3d(*map(float,p));mm.TextureCoordinates.__add__(*map(float,u))
   mm.Faces.AddFace(k*3,k*3+1,k*3+2)
 mm.Normals.ComputeNormals();mm.Normals.UnitizeNormals();assert mm.IsValid
 if not source:assert mm.IsClosed
 F.Objects.Delete(at.Id);ident=F.Objects.Add(mm,at)
 for rec in AQ['created']:
  if rec['node']==n:rec['id']=str(ident);rec['geometry_hash']=hashlib.sha256(json.dumps(mm.Encode(),sort_keys=True).encode()).hexdigest()
 nv=(np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R;nf=np.array([f[:3] for f in mm.Faces],np.int32);nu=np.array([[p.X,p.Y] for p in mm.TextureCoordinates]);nn=np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R;r=ii[n];r['triangles']=len(nf);r['element']={k:v for k,v in e.items() if k!='parts'};np.savez_compressed(O/'02_Data'/r['file'],vertices=nv,faces=nf,uv=nu,normals=nn,material_ids=np.zeros(len(nf),np.int32));E[n].update(e);records.append({'node':n,'triangles':len(nf),'bounds':[nv.min(0).tolist(),nv.max(0).tolist()]});print('CORRECTED JUNCTION',records[-1],flush=True)
sp=O/'08_Editable_Source/Architecture_Scene_V16.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V16_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();assert F.Write(str(P),8)
for nm in ['Native_Readback_Index_V16.json','Modeled_Index_V16.json']:(O/'02_Data'/nm).write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf8')
(O/'06_Report/V16_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/V16_Junction_Extent_QA.json').write_text(json.dumps({'status':'AWAITING_FINAL_NATIVE_READBACK','miter_limit':2,'modeled_junction_bounded_to_site':True,'original_scan_inside_modeled_interior_removed':True,'meshes':records},indent=2),encoding='utf8');print('JUNCTION CORRECTION SAVED',flush=True)
