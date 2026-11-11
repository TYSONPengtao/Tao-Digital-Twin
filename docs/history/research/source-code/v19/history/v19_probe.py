import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
B=Path(r'E:/jz/JIA/Rebuild_V18');I=json.loads((B/'02_Data/Native_Readback_Index_V18.json').read_text(encoding='utf8'))
for r in I:
 n=r['name']
 if any(s in n for s in ['PERIMETER','COURTYARD_WEST','COURTYARD_EAST','SCREENWALL','GATE','WALL_FINISH','WALL_TOE']):
  d=np.load(B/'02_Data'/r['file']);v=d['vertices'];print(n,r['materials'],r['native_objects'],r['triangles'],v.min(0).round(4).tolist(),v.max(0).round(4).tolist(),flush=True)
  e={k:val for k,val in r['element'].items() if k not in ['v12_parts','v11_clipped_parts']};txt=json.dumps(e,ensure_ascii=False);print(txt[:5500],flush=True)
