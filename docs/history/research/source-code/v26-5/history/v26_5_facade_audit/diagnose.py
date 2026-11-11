import sys,json
from pathlib import Path
W=Path(__file__).resolve().parent.parent
sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import shape,LineString
from v24_16_common import solid
FD=W/'v26_4/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
r=J['V26_3_House_Connected_Walls_And_Stairs'];a=np.load(FD/r['file']);m=solid(a['v'],a['f']);out=[]
for axis,u in [(0,3.),(0,5.),(0,8.),(1,5.),(1,11.8)]:
 rows=[]
 for z in [3.,3.05,3.15,3.25,3.30,3.319,3.321,3.33,3.35,3.40,3.42,3.449,3.451,3.46,3.5,3.6,3.7,6.91,6.93,7.,7.049,7.051]:
  p0=[12.5,u,z]if axis==0 else[u,9.3,z];p1=[13.5,u,z]if axis==0 else[u,10.3,z]
  hs=m.ray_cast(p0,p1)
  rows.append([z,[[round(float(c),5)for c in h.position] for h in hs]])
 out.append({'axis':axis,'along':u,'rays':rows})
print(json.dumps(out,indent=1))
print('LAYER PROFILES AT EAST Y5 AND REAR X5')
p=json.loads((W/'v26_4/Exact_House_Parts.json').read_text('utf8'))
for row in p['layers']:
 if 2.9<sum(row['z_m'])/2<3.8 or 6.8<sum(row['z_m'])/2<7.2:
  P=shape(row['outline']);E=P.intersection(LineString([(12.5,5),(13.5,5)]));N=P.intersection(LineString([(5,9.3),(5,10.3)]));print(row['z_m'],E.wkt,N.wkt)
(W/'v26_5_facade_audit/Rays.json').write_text(json.dumps(out,indent=2),'utf8')
