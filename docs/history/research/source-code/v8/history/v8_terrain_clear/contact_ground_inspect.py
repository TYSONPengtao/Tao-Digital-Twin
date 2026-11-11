import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');d=np.load(O/'02_Data/V8_Clearance_PHOTO_BOUNDARY_GROUND_RECOVERY.npz');t=d['vertices'][d['faces']];mn=t.min(1);mx=t.max(1);hit=(mn[:,0]<.20)&(mx[:,0]>-.20)&(mn[:,1]<1.92)&(mx[:,1]>.96);q=t[hit];n=np.cross(q[:,1]-q[:,0],q[:,2]-q[:,0]);n/=np.linalg.norm(n,axis=1)[:,None];print('tri',len(q),'zcentroid',np.percentile(q[:,:,2].mean(1),[0,10,25,50,75,90,100]),'up',np.sum(abs(n[:,2])>.65));print('upz',np.percentile(q[abs(n[:,2])>.65,:,2],[0,25,50,75,100]));
