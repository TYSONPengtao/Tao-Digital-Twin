import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import numpy as np,shapely
from shapely.ops import unary_union
from shapely.geometry import Polygon
O=Path(r'E:/jz/JIA/Rebuild_V15');I=json.loads((O/'02_Data/Native_Readback_Index_V15.json').read_text(encoding='utf8'));idx={r['name']:r for r in I}
def top(n):
 d=np.load(O/'02_Data'/idx[n]['file']);t=d['vertices'][d['faces']];up=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,2]>1e-8;return t[up]
walk=unary_union([Polygon(q[:,:2]) for q in top('SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT')]).buffer(0);rows=[]
for n in idx:
 if not n.startswith(('SITE_V12_REBUILT_EARTH','SITE_V12_REBUILT_ROAD','SITE_V12_REBUILT_COURT')):continue
 t=top(n);area=float(shapely.area(shapely.intersection(shapely.polygons(t[:,:,:2]),walk)).sum());rows.append({'node':n,'positive_xy_overlap_m2':area});assert area<1e-4,(n,area)
(O/'06_Report/V15_No_Duplicate_Road_Surface_QA.json').write_text(json.dumps({'status':'PASS_NO_OLD_GROUND_OVER_NEW_ROAD','maximum_overlap_area_m2':max(r['positive_xy_overlap_m2'] for r in rows),'checks':rows,'method':'Actual native readback triangles; old ground has been boolean-cut from the new pavement footprint, preserving the tree-pit hole'},ensure_ascii=False,indent=2),encoding='utf8');print('NO DUPLICATE SURFACE PASS',max(r['positive_xy_overlap_m2'] for r in rows),flush=True)
