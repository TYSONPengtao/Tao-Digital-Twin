import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'))
for r in I:
 if r['name'] in ['SITE_SHED_1_ROOF','SITE_SHED_2_ROOF','SITE_SHED_3_ROOF','SITE_WEST_PERGOLA_ROOF','ROOF_MAIN_JOINED','SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
  d=np.load(O/'02_Data'/r['file']);v=d['vertices'];from scipy.spatial import ConvexHull
  hull=ConvexHull(v[:,:2]);print(r['name'],np.round(v[hull.vertices][:,:2],3).tolist())
