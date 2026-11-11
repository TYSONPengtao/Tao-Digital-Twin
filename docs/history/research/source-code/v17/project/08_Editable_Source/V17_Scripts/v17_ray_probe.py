import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]
import numpy as np
O=Path(r'E:/jz/JIA/Rebuild_V17');I=json.loads((O/'02_Data/Native_Readback_Index_V17.json').read_text(encoding='utf8'));origin=np.array([24,-1.5,7.]);target=np.array([15.2,-8.2,-.5]);forward=target-origin;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward);s=math.tan(math.radians(63)/2)
pixels=[(785,320),(393,458),(524,608),(484,645),(655,580),(833,454)];directions=[];hits=[[] for p in pixels]
for x,y in pixels:
 d=forward+right*((x/1600*2-1)*s)+up*((1-y/1100*2)*(1100/1600)*s);d/=np.linalg.norm(d);directions.append(d)
for r in I:
 dat=np.load(O/'02_Data'/r['file']);v=dat['vertices'];f=dat['faces'];t=v[f];a=t[:,0];e1=t[:,1]-a;e2=t[:,2]-a;ss=origin-a;q=np.cross(ss,e1)
 for j,d in enumerate(directions):
  H=np.cross(np.broadcast_to(d,e2.shape),e2);det=np.einsum('ij,ij->i',e1,H);di=np.zeros(len(det));good=abs(det)>1e-12;di[good]=1/det[good];u=np.einsum('ij,ij->i',ss,H)*di;vv=q@d*di;tt=np.einsum('ij,ij->i',e2,q)*di;g=good&(u>=-1e-7)&(vv>=-1e-7)&(u+vv<=1+1e-7)&(tt>1e-6)
  if g.any():
   k=np.where(g)[0][np.argmin(tt[g])];pt=origin+d*tt[k];normal=np.cross(e1[k],e2[k]);normal/=np.linalg.norm(normal);hits[j].append({'node':r['name'],'material':r['materials'][int(dat['material_ids'][k])],'distance':float(tt[k]),'point':pt.round(5).tolist(),'face_normal_dot_ray':float(normal@d)})
for p,hits0 in zip(pixels,hits):print('PIXEL',p,json.dumps(sorted(hits0,key=lambda r:r['distance'])[:3],ensure_ascii=False))
