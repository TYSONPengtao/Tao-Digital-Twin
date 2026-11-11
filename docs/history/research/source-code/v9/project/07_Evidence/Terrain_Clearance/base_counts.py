import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,shapely
from shapely.geometry import Polygon
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');C=json.loads((O/'02_Data/Coordinate.json').read_text());R=np.array(C['local_to_survey'])[:3,:3];org=np.array(C['origin']);p=Polygon(json.loads((W/'v8_terrain_clear/Redline_Calibration.json').read_text())['raw_local_polygon'])
for i in range(5):
 d=np.load(O/'02_Data'/f'Base_{i}.npz');v=(d['vertices']-org)@R;f=d['faces'];t=v[f[:,:3]];mn=t[:,:,:2].min(1);mx=t[:,:,:2].max(1);b=p.bounds;idx=np.flatnonzero((mx[:,0]>=b[0])&(mn[:,0]<=b[2])&(mx[:,1]>=b[1])&(mn[:,1]<=b[3]));hits=shapely.intersects(shapely.polygons(t[idx,:,:2]),p);ii=idx[hits];print(i,len(f),len(ii),np.round(v.min(0),2),np.round(v.max(0),2))
