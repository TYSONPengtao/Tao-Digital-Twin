import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np
from v24_16_common import solid
D=W/'v24_33';ix={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};out={}
for n in ix:
 if not any(t in n for t in ['BEFORE_WOOD','TIMBER_FRAMES','STORAGE_STONE_GUARD','COURTYARD_WEST','White_Courtyard','SLAB_JOINED_F3','SLOPED_FINISH']):continue
 a=np.load(D/ix[n]['file']);v,inv=np.unique(np.round(a['v'],5),axis=0,return_inverse=True);f=inv[a['f']];par=np.arange(len(v))
 def find(i):
  while par[i]!=i:par[i]=par[par[i]];i=par[i]
  return i
 for q in f:
  ra=find(q[0])
  for j in q[1:]:par[find(j)]=ra
 groups={}
 for i in np.unique(f):groups.setdefault(int(find(i)),[]).append(int(i))
 rows=[]
 for k,g in enumerate(groups.values()):
  ids=np.array(g);p=v[ids];rows.append({'i':k,'min':p.min(0).tolist(),'max':p.max(0).tolist(),'verts':len(ids)})
 out[n]=rows
 print(n,'COMPONENTS',len(rows),flush=True)
 for r in rows:
  if len(rows)<30 or 'TIMBER_FRAMES' in n or 'BEFORE_WOOD_06' in n:print(r,flush=True)
(D/'Components.json').write_text(json.dumps(out,indent=2),encoding='utf8')
