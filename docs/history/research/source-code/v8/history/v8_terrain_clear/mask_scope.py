import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
from shapely.geometry import Polygon
from shapely.ops import unary_union
D=W/'v8_terrain_clear';p=json.loads((D/'Terrain_Clearance_Polygon.json').read_text(encoding='utf-8'))['clearance'];C=unary_union([Polygon(x['outer'],x['holes']) for x in p]);hp=json.loads(Path(r'E:\jz\JIA\Rebuild_V7_Hybrid\02_Data\Hole_Polygon.json').read_text());H=Polygon(hp['local']['outer'],hp['local']['holes']);print('C outside H',C.difference(H).area,'H U C',H.union(C).area,'Ctypes',C.geom_type,len(p));print('polys',[(x.area,x.bounds) for x in C.geoms])
