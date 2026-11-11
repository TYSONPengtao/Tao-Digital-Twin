from pathlib import Path
import sys,json
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
from v24_16_common import solid
D=W/'v26_5/Final';I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};a=np.load(D/I['V26_3_House_Connected_Walls_And_Stairs']['file']);m=solid(a['v'],a['f'],'actual source house');out=[]
for fl,lo,hi in [(1,1.2,1.6),(2,4.95,5.35)]:
 for y in [8.6,8.9,9.05,9.3,9.49]:
  for x in [5.19,5.21,5.25,5.299,5.301,5.31,5.4]:
   h=[h for h in m.ray_cast([x,y,hi],[x,y,lo])if h.normal[2]>.99];z=max((h.position[2]for h in h),default=None);out.append({'floor':fl,'x':x,'y':y,'top_z':z})
  print('FLOOR',fl,'Y',y,[r for r in out[-7:]],flush=True)
(Path(__file__).parent/'V26_5_actual_last_tread_profiles.json').write_text(json.dumps(out,indent=2),'utf8')
