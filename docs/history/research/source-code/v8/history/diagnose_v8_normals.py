import sys
from pathlib import Path
W=Path(__file__).parent
sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid')
A=rh.File3dm.Read(str(O/'01_Source/Pure_Site_UNMODIFIED.3dm'))
B=rh.File3dm.Read(str(O/'01_Source/Pure_Site_WORKING_V8.3dm'))
for i,(a,b) in enumerate(zip(A.Objects,B.Objects)):
 d=np.load(O/'02_Data'/f'Base_{i}.npz')
 n=np.array([[q.X,q.Y,q.Z] for q in b.Geometry.Normals]);t=d['normals'].astype(np.float32).astype(float)
 s=np.array([[q.X,q.Y,q.Z] for q in a.Geometry.Normals])
 diff=np.abs(n-t)
 print(i,a.Attributes.Id==b.Attributes.Id,n.shape,t.shape,'max',diff.max(),'nonexact',np.count_nonzero(diff),'sourceprefix',np.array_equal(n[:len(s)],s),flush=True)
 ix=np.unravel_index(diff.argmax(),diff.shape)[0]
 print('worst',ix,'read',n[ix].tolist(),'expected',t[ix].tolist(),'raw',d['normals'][ix].tolist(),flush=True)
