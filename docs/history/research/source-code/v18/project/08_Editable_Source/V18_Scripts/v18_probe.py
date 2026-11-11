import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
B=Path(r'E:/jz/JIA/Rebuild_V17');I=json.loads((B/'02_Data/Native_Readback_Index_V17.json').read_text(encoding='utf8'))
for r in I:
 n=r['name']
 if any(t in n for t in ['STORAGE','DRAIN','TOE','SOIL','STONE_BASE']):
  d=np.load(B/'02_Data'/r['file']);v=d['vertices'];print(n,r['materials'],r['native_objects'],len(d['faces']),v.min(0).round(4).tolist(),v.max(0).round(4).tolist(),flush=True)
  if 'OUTER_STORAGE' in n or 'PLINTH' in n:print(json.dumps(r['element'],ensure_ascii=False),flush=True)
print('REFERENCE EXTERIOR FRAMES')
for d in ['07_Reference/INSV','07_Reference/INSV_Storage']:
 for p in (B/d).glob('*'):print(str(p))
