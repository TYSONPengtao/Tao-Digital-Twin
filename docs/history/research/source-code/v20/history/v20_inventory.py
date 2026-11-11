import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
B=Path('E:/jz/JIA/Rebuild_V19');D=W/'v20';D.mkdir(exist_ok=True)
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'))
I=json.loads((B/'02_Data/Native_Readback_Index_V19.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']}
rows=[]
for r in I:
 n=r['name'];d=np.load(B/'02_Data'/r['file']);v=d['vertices'];e=E.get(n,{})
 rows.append({'name':n,'bounds':[v.min(0).round(6).tolist(),v.max(0).round(6).tolist()],'materials':r['materials'],'triangles':len(d['faces']),'element':{k:v for k,v in e.items() if k!='parts'}})
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:
 if any(t in r['name'].upper() for t in ['DOOR','GATE','PAVILION','PARTITION','STORAGE','KITCHEN','ENTRANCE']):print(json.dumps(r,ensure_ascii=False),flush=True)
