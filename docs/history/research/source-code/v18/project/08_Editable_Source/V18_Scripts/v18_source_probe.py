import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V17/08_Editable_Source/Architecture_Scene_V17.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
for n in ['SITE_V14_OUTER_STORAGE_STEEL_BEARING_FRAME','SITE_V14_OUTER_STORAGE_METAL_ROOF','SITE_V14_OUTER_STORAGE_METAL_SEAMS','SITE_V17_OUTER_STORAGE_PLINTH_CAP_RETURN','SITE_V17_KITCHEN_STORAGE_CONTINUOUS_STONE_BASE']:
 e=E[n];print(n,json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False),flush=True)
 for j,p in enumerate(e['parts']):
  v,fs,_,_=ex.solid_data(p['geometry']);v=np.array(v);print(j,p['geometry']['type'],v.min(0).round(4),v.max(0).round(4),flush=True)
  if 'STEEL' in n:print(json.dumps(p['geometry']))
