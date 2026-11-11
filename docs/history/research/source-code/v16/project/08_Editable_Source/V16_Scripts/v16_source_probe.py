import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]
import numpy as np
for root,ver in [('Rebuild_V15','V15'),('Rebuild_V16','V16')]:
 O=Path(r'E:/jz/JIA')/root;I=json.loads((O/f'02_Data/Native_Readback_Index_{ver}.json').read_text(encoding='utf8'))
 for r in I:
  if r['name'].startswith(('SITE_V14_ORIGINAL_EXTERIOR','SITE_V16_')):
   d=np.load(O/'02_Data'/r['file']);v=d['vertices'];print(ver,r['name'],v.min(0).tolist(),v.max(0).tolist())
   if np.max(v[:,2])>25:print('HIGH POINTS',v[np.argsort(v[:,2])[-5:]].tolist())
