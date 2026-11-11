from pathlib import Path
import json,struct,sys
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
from PIL import Image
idx=json.loads((W/'v25/Export_Index.json').read_text('utf8'));mats={m['key']:m for m in json.loads((W/'v25/Material_Index.json').read_text('utf8'))};c=next(c for c in json.loads((W/'v25/Camera_Index.json').read_text('utf8')) if c['name']=='V24_35_02_Kitchen_East_Close');loc=np.array(c['location']);dire=np.array(c['direction']);up=np.array(c['up']);right=np.cross(dire,up);meshes=[]
for x in idx:
 if x['layer_path'][0].startswith('90'):continue
 bb=np.array(x['bounds']);near=np.array([22.9,-9.1,-1]);far=np.array([23.1,-8.9,4]);rr=np.array([-1,.4,-.4]);r1=(bb[0]-loc)/rr;r2=(bb[1]-loc)/rr
 if np.minimum(r1,r2).max()>np.maximum(r1,r2).min():continue
 data=Path(x['file']).read_bytes();ver,nv,nf=struct.unpack_from('<III',data,4);v=np.frombuffer(data,'<f8',nv*3,16).reshape(-1,3);uv=np.frombuffer(data,'<f4',nv*2,16+nv*24+nv*12).reshape(-1,2);f=np.frombuffer(data,'<i4',nf*3,16+nv*44).reshape(-1,3);meshes.append((x,v,uv,f))
for py in [740,750,760,770,780,790]:
 px=1050;entry=next(r for r in json.loads((W/'v25/Native_Rays.json').read_text())['rays'] if r['py']==py);loc=np.array(entry['to']);ray=np.array(entry['from'])-loc;ray/=np.linalg.norm(ray);hits=[]
 for x,v,uv,f in meshes:
  tri=v[f];a=tri[:,1]-tri[:,0];b=tri[:,2]-tri[:,0];p=np.cross(np.broadcast_to(ray,b.shape),b);det=np.einsum('ij,ij->i',a,p);valid=abs(det)>1e-12;inv=np.divide(1,det,out=np.zeros_like(det),where=valid);s=loc-tri[:,0];u=np.einsum('ij,ij->i',s,p)*inv;q=np.cross(s,a);vv=np.einsum('j,ij->i',ray,q)*inv;t=np.einsum('ij,ij->i',b,q)*inv;valid&=(u>=0)&(vv>=0)&(u+vv<=1)&(t>0)
  for fi in np.flatnonzero(valid):
   texuv=(1-u[fi]-vv[fi])*uv[f[fi,0]]+u[fi]*uv[f[fi,1]]+vv[fi]*uv[f[fi,2]];hits.append({'name':x['name'],'material':x['material'],'distance':float(t[fi]),'uv':texuv.tolist(),'face':int(fi),'vertices':tri[fi].tolist(),'front':bool(np.dot(np.cross(a[fi],b[fi]),ray)<0)})
 print(py,json.dumps(sorted(hits,key=lambda h:h['distance'])[:5],ensure_ascii=False),flush=True)
