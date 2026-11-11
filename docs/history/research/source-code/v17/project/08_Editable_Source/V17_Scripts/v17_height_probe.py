import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]
import numpy as np
B=Path(r'E:/jz/JIA/Rebuild_V16');I=json.loads((B/'02_Data/Native_Readback_Index_V16.json').read_text(encoding='utf8'));tt=[]
for r in I:
 if not r['name'].startswith('SITE_V14_ORIGINAL_EXTERIOR'):continue
 d=np.load(B/'02_Data'/r['file']);t=d['vertices'][d['faces']];c=t.mean(1);no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);g=(c[:,0]>12)&(c[:,0]<23)&(c[:,1]>-18)&(c[:,1]<1)&(c[:,2]<-1.7)&(c[:,2]>-5)&(abs(no[:,2])>.65*np.linalg.norm(no,axis=1));tt.extend(t[g])
t=np.array(tt);c=t.mean(1);np.savez_compressed(W/'v17/Local_Original_Ground.npz',triangles=t)
for x,y in [(14,-8),(14,-4),(16,-8),(16,-5),(19,-9),(19,-5),(20,-8),(20,-6),(18,-3),(14,-3),(18,-9.65),(21,-10),(21,-16),(16,-16.6)]:
 dist=np.linalg.norm(c[:,:2]-[x,y],axis=1);z=c[dist<.55,2];print('GROUND',x,y,'nearest_m',round(dist.min(),3),'n',len(z),'quantile',np.round(np.quantile(z,[.1,.25,.5,.75,.9]),3).tolist() if len(z) else [])
print('GROUND_TRIANGLES',len(t),'XYZ_RANGE',t.min((0,1)).tolist(),t.max((0,1)).tolist())
