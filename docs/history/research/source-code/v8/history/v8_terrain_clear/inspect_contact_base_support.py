import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
from scipy.spatial import cKDTree
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');C=json.loads((O/'02_Data/Coordinate.json').read_text());R=np.array(C['local_to_survey'])[:3,:3];org=np.array(C['origin']);targets=np.array([[13.69,-8.91],[13.7,-7.0],[13.7,-6],[13.7,-4.4]])
for i in [0,3,4]:
 d=np.load(O/'02_Data'/f'Base_{i}.npz');v=(d['vertices']-org)@R;f=d['faces'];t=v[f[:,:3]];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-20)
 for h in [.1,.5,1.4]:
  sel=(abs(n[:,2])>.7)&(t[:,:,2].max(1)<h)&(np.ptp(t[:,:,2],axis=1)<.22);p=np.unique(t[sel].reshape(-1,3),axis=0);tree=cKDTree(p[:,:2]);ds,ix=tree.query(targets);print('base',i,'ceiling',h, 'dist',ds,'xyz',p[ix])
