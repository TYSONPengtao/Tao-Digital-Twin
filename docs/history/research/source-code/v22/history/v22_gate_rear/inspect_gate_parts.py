import sys,json
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
B=Path('E:/jz/JIA/Rebuild_V21');S=json.loads((B/'08_Editable_Source/Architecture_Scene_V21.json').read_text(encoding='utf8'));ex.SCENE=S
for e in S['elements']:
 if ('GATE_REFERENCE' in e['name'] or 'INNER_GATE__LEAF' in e['name']):
  print('\n',e['name'],e.get('reference_layer_name'),len(e.get('parts',[])))
  for p in e.get('parts',[]):
   v,f=ex.world_part(p,e);v=np.array(v)
   if len(e['parts'])<12:print(p.get('reference_object_name'),p['material'],np.round(v.min(0),4).tolist(),np.round(v.max(0),4).tolist())
  v=np.vstack([ex.world_part(p,e)[0] for p in e.get('parts',[])]);print('TOTAL',v.min(0),v.max(0))
