import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,shapely
from shapely.geometry import Polygon,mapping
from shapely.ops import unary_union
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');h=json.loads((O/'02_Data/Hole_Polygon.json').read_text());H=Polygon(h['local']['outer'],h['local']['holes']);I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));coverage=[]
for r in I:
 d=np.load(O/'02_Data'/r['file']);xy=d['vertices'][d['faces'],:2];ar=abs(np.cross(xy[:,1]-xy[:,0],xy[:,2]-xy[:,0]))/2;coverage.append(shapely.union_all(shapely.polygons(xy[ar>1e-10])))
res=H.difference(unary_union(coverage));parts=list(res.geoms) if hasattr(res,'geoms') else [res]
parts=sorted(parts,key=lambda p:-p.area)
report={'total_m2':res.area,'geometry':mapping(res),'parts':[{'area_m2':p.area,'bbox':p.bounds,'outer':list(p.exterior.coords),'holes':[list(q.coords) for q in p.interiors]} for p in parts if p.area>1e-12]}
(W/'v8_coverage_residual.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'area':res.area,'pieces':len(parts),'significant':[{'area':p.area,'bbox':p.bounds} for p in parts if p.area>1e-9]},indent=2),flush=True)
