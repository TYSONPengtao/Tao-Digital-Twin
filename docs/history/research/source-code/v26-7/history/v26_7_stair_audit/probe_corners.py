from pathlib import Path
import sys,json
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p)for p in['np1','geomlibs','libs']]+[str(W)];import numpy as np
from v24_16_common import solid
D=W/'v26_6/Final';I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';a=np.load(D/I[HN]['file']);H=solid(a['v'],a['f'],HN);out=[]
for z in[.5,2.8,3.4,4.5,6.94,8.5,10.0]:
 for face,axis,sgn,stations,bound,origin,end in [('west',0,1,[7.43,7.45,7.48,7.50,7.52,7.54,7.6,8.5,9.45,9.50,9.52,9.54,9.56,9.58,9.60,9.64,9.67],(3.6,4.3),4.6,3.5),('east',0,-1,[7.43,7.45,7.48,7.50,7.52,7.54,7.6,8.5,9.45,9.50,9.52,9.54,9.56,9.58,9.60,9.64,9.67],(8.6,9.4),8.4,9.5),('north',1,-1,[4.03,4.05,4.08,4.10,4.12,4.15,4.20,4.25,4.5,6.5,7.5,8.5,8.85,8.88,8.90,8.92,8.95,8.97],(9.4,10.1),9.2,10.2),('south',1,1,[4.03,4.05,4.08,4.10,4.12,4.15,4.20,4.25,4.5,6.5,7.5,8.5,8.85,8.88,8.90,8.92,8.95,8.97],(7.0,7.7),7.8,6.9)]:
  for u in stations:
   p=[origin,u,z]if axis==0 else[u,origin,z];q=[end,u,z]if axis==0 else[u,end,z];hits=[h for h in H.ray_cast(p,q)if h.normal[axis]*sgn>.99 and bound[0]<h.position[axis]<bound[1]]
   out.append({'face':face,'z':z,'u':u,'plane':float(hits[0].position[axis])if hits else None})
 print('Z',z,{face:sorted(set(round(r['plane'],6)for r in out if r['z']==z and r['face']==face and r['plane']is not None))for face in['west','east','north','south']},flush=True)
(Path(__file__).parent/'Native_Stair_Corner_Plane_Probe.json').write_text(json.dumps(out,indent=2),'utf8')
