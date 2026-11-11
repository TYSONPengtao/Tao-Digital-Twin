import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
Q=json.loads((W/'v14/Building_Mutation.json').read_text(encoding='utf8'));e=next(e for e in Q['replace'] if e['name'].endswith('PLASTER_STEPPED_RELIEF'))
for i in [144,146]:
 g=e['parts'][i]['geometry'];v=np.array(g['vertices']);f=np.array(g['faces']);m=rh.Mesh();m.Vertices.UseDoublePrecisionVertices=True
 for p in v:m.Vertices.AddPoint3d(*p)
 for ff in f:m.Faces.AddFace(*map(int,ff))
 m.Normals.ComputeNormals();print(i,len(v),len(f),m.IsValidWithLog,m.IsClosed,'zeroareas',np.sort(np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1))[:5].tolist(),flush=True)
