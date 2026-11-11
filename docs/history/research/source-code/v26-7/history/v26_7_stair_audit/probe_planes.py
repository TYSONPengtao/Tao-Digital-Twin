from pathlib import Path
import sys,json
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p)for p in['np1','geomlibs','libs']]+[str(W)];import numpy as np
from v24_16_common import solid
D=W/'v26_6/Final';I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';a=np.load(D/I[HN]['file']);H=solid(a['v'],a['f'],HN);out=[]
for z in[.5,1.4,2.8,3.1,3.319,3.34,3.4,3.449,3.46,4.0,4.9,6.1,6.7,6.919,6.94,7.02,7.06,8.,9.5,10.0]:
 for face,axis,sgn,stations,bound,origin,end in [('west',0,1,[7.6,7.8,8.5,9.2,9.5],(3.6,4.3),4.6,3.5),('east',0,-1,[7.6,7.8,8.5,9.2,9.5],(8.6,9.4),8.4,9.5),('north',1,-1,[4.25,4.5,5.5,6.5,7.5,8.5,8.85],(9.4,10.1),9.2,10.2),('south',1,1,[4.25,4.5,5.5,6.5,7.5,8.5,8.85],(7.0,7.7),7.8,6.9)]:
  for u in stations:
   p=[origin,u,z]if axis==0 else[u,origin,z];q=[end,u,z]if axis==0 else[u,end,z];hits=[h for h in H.ray_cast(p,q)if h.normal[axis]*sgn>.99 and bound[0]<h.position[axis]<bound[1]]
   out.append({'face':face,'z':z,'u':u,'plane':float(hits[0].position[axis])if hits else None})
 print('Z',z,{face:sorted(set(round(r['plane'],6)for r in out if r['z']==z and r['face']==face and r['plane']is not None))for face in['west','east','north','south']},flush=True)
(Path(__file__).parent/'Native_Stair_Wall_Plane_Probe.json').write_text(json.dumps(out,indent=2),'utf8')
