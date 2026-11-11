import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]
import numpy as np,manifold3d as mf
O=Path(r'E:/jz/JIA/Rebuild_V17');I=json.loads((O/'02_Data/Native_Readback_Index_V17.json').read_text(encoding='utf8'))
for n in ['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY','SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD']:
 r=next(r for r in I if r['name']==n);d=np.load(O/'02_Data'/r['file']);v=d['vertices'];f=d['faces'];vv,inv=np.unique(np.round(v,8),axis=0,return_inverse=True);a=mf.Manifold(mf.Mesh64(vv.astype(np.float64),inv[f].astype(np.uint64)));print('NODE',n,a.status())
 for j,q in enumerate(a.decompose()):print('COMPONENT',j,'VOLUME',q.volume(),'BOUNDS',q.bounding_box())
