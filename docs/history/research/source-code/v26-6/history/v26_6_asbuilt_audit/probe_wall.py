from pathlib import Path
import sys,json
W=Path(__file__).resolve().parent.parent;sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
from v24_16_common import solid
FD=W/'v26_5/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};a=np.load(FD/J['V26_3_House_Connected_Walls_And_Stairs']['file']);m=solid(a['v'],a['f']);out={'rays':[]}
for x in [.1,.19,.21,.25,.5,1.,1.5,2.1,2.199,2.201,2.3,2.6,3.,3.6,3.7]:
 for z in [7.10,8.0,8.8,9.4,9.74,9.80,9.94,9.96,10.00,10.03]:
  hs=m.ray_cast([x,6.9,z],[x,7.7,z]);out['rays'].append({'x':x,'z':z,'hits':[h.position for h in hs]})
print('NATIVE_THROUGH_WALL_AT_Z8',[(r['x'],r['hits'])for r in out['rays']if r['z']==8.])
print('NATIVE_THROUGH_HEAD_AT_X1',[(r['z'],r['hits'])for r in out['rays']if r['x']==1.])
core=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components'];out['relevant_cores']=[r for r in core if r['name'].startswith(('KZ_','BEAM_'))and np.array(r['bounds_m'])[1,2]>7.05 and np.array(r['bounds_m'])[0,0]<3.9 and np.array(r['bounds_m'])[1,1]>7.1 and np.array(r['bounds_m'])[0,1]<7.5]
print('CORES',json.dumps(out['relevant_cores'],indent=1))
(W/'v26_6_asbuilt_audit/Native_F3_Terrace_Crosswall_Probe.json').write_text(json.dumps(out,indent=2),'utf8')
