import sys,json
from pathlib import Path
W=Path(__file__).parent
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import export_v5 as ex, numpy as np
S=ex.SCENE
for e in S['elements']:
 if any(t in e['name'] for t in ['WALLS_JOINED_F3','ARCH_BEAM','ARC','TILE_ROWS','WALLS_JOINED_F2','F2']) and e['layer'] in ['10_WALL_EXT','11_WALL_INT','31_WINDOW','50_ROOF','51_CANOPY']:
  vs=[ex.world_part(p,e)[0] for p in ex.expand_parts(e)];vs=[v for v in vs if v is not None];v=np.vstack(vs)
  print(e['name'],e['layer'],len(e['parts']),v.min(0).round(3).tolist(),v.max(0).round(3).tolist())
print(list(S['materials']))
for e in S['elements']:
 if any(t in e['name'] for t in ['TILE','CANOPY_CENTER','TERRACE']) and not e['name'].startswith('CONSTRUCTION_'):
  print('DETAIL',e['name'],len(e['parts']),e.get('definition'))
for e in S['elements']:
 if e['name']=='FACADE_CONTINUOUS_F3':
  from shapely.geometry import Polygon,box
  for p in e['parts']:
   g=p['geometry']
   if g['type']=='prism_holes' and Polygon(g['outer'],g['holes']).intersects(box(3.7,1.1,4.1,7.1)):print('WESTSIDE',str(g))
