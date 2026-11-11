import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1')]
import numpy as np
O=Path(r'E:/jz/JIA/Rebuild_V15');I=json.loads((O/'02_Data/Native_Readback_Index_V15.json').read_text(encoding='utf8'));points=[[7.4,-13.4],[6.6,-13.4],[4.0,-13.4],[2.0,-13.4],[19.0,-9.5]];rows={str(p):[] for p in points}
for rr in I:
 d=np.load(O/'02_Data'/rr['file']);v=d['vertices'];bb=np.array([v.min(0),v.max(0)]);t=v[d['faces']]
 for pt in points:
  if not(np.all(bb[0,:2]<=pt) and np.all(bb[1,:2]>=pt)):continue
  a=t[:,0,:2];dd=t[:,1,:2]-a;b=t[:,2,:2]-a;q=np.array(pt)-a;det=dd[:,0]*b[:,1]-dd[:,1]*b[:,0];safe=abs(det)>1e-10;u=np.divide(q[:,0]*b[:,1]-q[:,1]*b[:,0],det,out=np.zeros(len(t)),where=safe);w=np.divide(dd[:,0]*q[:,1]-dd[:,1]*q[:,0],det,out=np.zeros(len(t)),where=safe);keep=safe&(u>=-1e-8)&(w>=-1e-8)&(u+w<=1+1e-8)
  for k in np.where(keep)[0]:
   z=float(t[k,0,2]+u[k]*(t[k,1,2]-t[k,0,2])+w[k]*(t[k,2,2]-t[k,0,2]));uv=d['uv'][d['faces'][k]];uv0=uv[0]+u[k]*(uv[1]-uv[0])+w[k]*(uv[2]-uv[0]);rows[str(pt)].append({'node':rr['name'],'z':z,'normal_z_sign':float(np.sign(det[k])),'mat':rr['materials'][int(d['material_ids'][k])],'uv':uv0.tolist(),'triangle':t[k].tolist()})
for pt in points:rows[str(pt)]=sorted(rows[str(pt)],key=lambda q:-q['z'])[:6]
(W/'v15/Black_Probe.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows,indent=2),flush=True)
