import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1')]
import numpy as np
O=Path(r'E:/jz/JIA/Rebuild_V14');I=json.loads((O/'02_Data/Native_Readback_Index_V14.json').read_text(encoding='utf8'))
for row in I:
 n=row['name'];d=np.load(O/'02_Data'/row['file']);v=d['vertices'];b=np.array([v.min(0),v.max(0)])
 if n.startswith('SITE_PERIMETER') and np.all(b[1]>[18,-16.4,.8]) and np.all(b[0]<[19.4,-9.2,4.5]):print('STORE_OBSTACLE',n,b.tolist())
 if ('WALL' in n or 'PARTITION' in n or 'LAUNDRY' in n or 'F3' in n) and np.all(b[1]>[2.0,6.1,7.8]) and np.all(b[0]<[9,7.3,9.3]):print('HALL',n,b.tolist())
 for label,a,dir,L in [('exit',[3.0,6.8,8.4],[1,0,0],1.5),('study',[8.45,5.5,8.4],[0,1,0],1.8),('camera',[8.55,6.82,8.9],[-1,0,0],5.0)]:
  a=np.array(a);di=np.array(dir);seg=np.array([a,a+di*L]);
  if not(np.all(b[1]>=seg.min(0)) and np.all(b[0]<=seg.max(0))):continue
  t=v[d['faces']];u=t[:,1]-t[:,0];vv=t[:,2]-t[:,0];hh=np.cross(np.tile(di,(len(t),1)),vv);det=np.einsum('ij,ij->i',u,hh);keep=abs(det)>1e-10;inv=np.zeros(len(t));inv[keep]=1/det[keep];s=a-t[:,0];p=np.einsum('ij,ij->i',s,hh)*inv;q=np.cross(s,u);r=q@di*inv;dist=np.einsum('ij,ij->i',vv,q)*inv;hit=keep&(p>=0)&(r>=0)&(p+r<=1)&(dist>.001)&(dist<L)
  if hit.any():print('HIT',label,n,np.round(np.sort(dist[hit])[:8],4).tolist())
