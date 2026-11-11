"""Read original as-built 3dm, preserve coordinates/UV, export local inspection cache."""
import sys,json,hashlib,time
from pathlib import Path
W=Path(__file__).parent
sys.path[:0]=[str(W/'np1'),str(W/'libs'),str(W/'geomlibs')]
import numpy as np,rhino3dm as rh
O=W/'v24_10';O.mkdir(exist_ok=True)
src=Path('E:/jz/实景三维场景模型.3dm')
co=json.loads(Path('E:/jz/JIA/Rebuild_V23/02_Data/Coordinate.json').read_text())
L=np.array(co['local_to_survey']);C=np.linalg.inv(L)
m=rh.File3dm.Read(str(src)); assert m
V=[];F=[];UV=[];MI=[];offset=0
for o in m.Objects:
 g=o.Geometry
 if not isinstance(g,rh.Mesh):continue
 vs=np.array([[p.X,p.Y,p.Z]for p in g.Vertices],float)
 vs=vs@C[:3,:3].T+C[:3,3]
 fs=[]
 for a,b,c,d in g.Faces:
  fs.append([a,b,c])
  if d!=c:fs.append([a,c,d])
 if len(g.TextureCoordinates)==len(vs):uv=np.array([[p.X,p.Y]for p in g.TextureCoordinates],np.float32)
 else:uv=np.zeros((len(vs),2),np.float32)
 V.append(vs.astype(np.float32));F.append(np.array(fs,np.int32)+offset);UV.append(uv);MI.extend([o.Attributes.MaterialIndex]*len(fs));offset+=len(vs)
v=np.concatenate(V);f=np.concatenate(F);uv=np.concatenate(UV);mi=np.array(MI,np.int16)
np.savez_compressed(O/'AsBuilt_All_LOCAL.npz',v=v,f=f,uv=uv,mi=mi)
t=v[f];b0=t.min(1);b1=t.max(1)
sel=(b1[:,0]>10)&(b0[:,0]<24)&(b1[:,1]>-20)&(b0[:,1]<-7)&(b1[:,2]>-7)&(b0[:,2]<7)
ff=f[sel];ids,inv=np.unique(ff,return_inverse=True)
np.savez_compressed(O/'AsBuilt_Storage_LOCAL.npz',v=v[ids],f=inv.reshape(-1,3),uv=uv[ids],mi=mi[sel])
mats=[]
for i,mat in enumerate(m.Materials):
 tx=mat.GetBitmapTexture();mats.append({'index':i,'name':mat.Name,'file':tx.FileName if tx else None})
report={'source':str(src),'source_sha256':hashlib.file_digest(src.open('rb'),'sha256').hexdigest(),'unit':str(m.Settings.ModelUnitSystem),'mesh_count':len(V),'vertices':len(v),'triangles':len(f),'local_to_survey':L.tolist(),'source_to_LOCAL':C.tolist(),'local_bounds':[v.min(0).tolist(),v.max(0).tolist()],'storage_crop_vertices':len(ids),'storage_crop_faces':int(sel.sum()),'materials':mats,'coordinate_basis':'Inherited registered JIA ENU metres; no scale fit or change to original 3dm'}
(O/'AsBuilt_Reference.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='materials'},ensure_ascii=False),flush=True)
