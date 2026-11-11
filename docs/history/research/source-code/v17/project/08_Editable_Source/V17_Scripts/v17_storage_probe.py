import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
B=Path(r'E:/jz/JIA/Rebuild_V17');S=json.loads((B/'08_Editable_Source/Architecture_Scene_V17.json').read_text(encoding='utf8'));ex.SCENE=S;I=json.loads((B/'02_Data/Native_Readback_Index_V17.json').read_text(encoding='utf8'));ii={r['name']:r for r in I}
for e in S['elements']:
 n=e['name']
 if 'STORAGE' not in n:continue
 d=np.load(B/'02_Data'/ii[n]['file']);v=d['vertices'];print('NODE',n,'BOUNDS',np.round([v.min(0),v.max(0)],3).tolist(),'PARTS',len(e.get('parts',[])))
 if any(k in n for k in ['TILE_ROOF','ROOF_PLANE','MASONRY','BEARING','BALUSTRADE']) and 'ROWS' not in n:
  print('META',json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False))
  if len(e['parts'])<24:
   for j,p in enumerate(e['parts']):print('PART',j,p['material'],json.dumps(p['geometry'],ensure_ascii=False)[:900])
