import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]
import numpy as np
O=Path(r'E:/jz/JIA/Rebuild_V16');d=np.load(O/'02_Data/Native_Readback/NATIVE_SITE_V16_GRADED_INTERIOR_SOIL.npz');t=d['vertices'][d['faces']];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);up=n[:,2]>1e-8;t=t[up];n=n[up];grade=np.linalg.norm(n[:,:2],axis=1)/n[:,2]
for i in np.argsort(grade)[-10:]:print('STEEP',float(grade[i]),t[i].tolist())
print('COUNTS',(grade>.2).sum(),(grade>.3).sum(),(grade>1).sum(),'of',len(grade))
