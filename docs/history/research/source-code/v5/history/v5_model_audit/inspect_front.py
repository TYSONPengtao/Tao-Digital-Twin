import sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['geomlibs','np1','libs']]
from shapely.geometry import Polygon,box
from shapely.affinity import rotate,translate
s=json.loads(Path(r'E:\jz\JIA\Rebuild_V4\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
q=box(4.101,1.94,8.899,2.26)
for e in s['elements']:
 if e['name']!='FACADE_CONTINUOUS_F1':continue
 for p in e['parts']:
  g=p['geometry']
  if g['z']<1<g['z']+g['height']:
   i=Polygon(g['outer'],g['holes']).intersection(q)
   if i.area>1e-9:print(i.wkt,i.area)
