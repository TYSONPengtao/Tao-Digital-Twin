import sys,json
from pathlib import Path
W=Path(__file__).parent.parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
B=Path('E:/jz/JIA/Rebuild_V19')
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'));ex.SCENE=S
rows=[]
for e in S['elements']:
 n=e['name']
 if any(k in n for k in ['KITCHEN','STORAGE','SCREENWALL']):
  bounds=[]
  for i,p in enumerate(e.get('parts',[])):
   v,_=ex.world_part(p,e)
   bounds.append({'part':i,'type':p['geometry']['type'],'material':p['material'],'min':v.min(0).round(5).tolist(),'max':v.max(0).round(5).tolist()})
  rows.append({'name':n,'meta':{k:v for k,v in e.items() if k!='parts'},'bounds':bounds})
(Path(__file__).parent/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:
 print(r['name'],len(r['bounds']))
 if any(k in r['name'] for k in ['MASONRY','GUARD','SCREENWALL']): print(json.dumps(r,ensure_ascii=False)[:15000])
