import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np
B=Path('E:/jz/JIA/Rebuild_V21');I=json.loads((B/'02_Data/Native_Readback_Index_V21.json').read_text(encoding='utf8'))
for r in I:
 n=r['name']
 if any(x in n for x in ['COURTYARD','FRONT','FACADE','PORCH','GATE_REFERENCE','ARCH_BEAM','CANOPY_FRONT','ROOF_MAIN','ROOF_CENTRAL']):
  d=np.load(B/'02_Data'/r['file']);v=d['vertices'];print(n, np.round([v.min(0),v.max(0)],4).tolist(),r['materials'])
