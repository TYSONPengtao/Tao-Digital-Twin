import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'))
for r in I:
 if r['element'].get('layer')=='60_SITE' or 'ROOF_MAIN_JOINED' in r['name']:
  d=np.load(O/'02_Data'/r['file']);v=d['vertices'];print(r['name'],np.round(v.min(0),3).tolist(),np.round(v.max(0),3).tolist(),r['triangles'])
