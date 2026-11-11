from pathlib import Path
import json,sys
W=Path(__file__).parents[1];sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
Q=json.loads((W/'v20/Door_Mutation.json').read_text(encoding='utf8'))
for e in Q['replace']:
 if not e['name'].startswith('SITE_SW_METAL'):continue
 print(e['name'],'PIVOT',e['pivot_world_m'],'PARTS',len(e['parts']))
 for i,p in enumerate(e['parts']):
  v,_=ex.world_part(p,e);print(i,p['material'],np.round([v.min(0),v.max(0)],5).tolist(),'span',np.round(v.max(0)-v.min(0),5).tolist())
