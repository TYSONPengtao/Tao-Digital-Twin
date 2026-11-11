import json,sys,ast
from pathlib import Path
W=Path(__file__).parents[1];sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex,manifold3d as mf
B=Path('E:/jz/JIA/Rebuild_V19');S=json.loads((B/'08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'));ex.SCENE=S
E={e['name']:e for e in S['elements']};q=json.loads((W/'v20/Door_Mutation.json').read_text(encoding='utf8'))
for n in ['DOOR_FRONT_CENTER_F2__FIXED']:
 for i,p in enumerate(E[n]['parts']):
  v,f=ex.world_part(p,E[n]);b=np.array([v.min(0),v.max(0)])
  if b[0,2]>5.8:print(n,i,'HEADER',b.tolist())
for e in q['replace']:
 if e['name'] not in ['DOOR_FRONT_CENTER_F2__SLIDE_1','DOOR_FRONT_CENTER_F2__SLIDE_2']:continue
 v=np.concatenate([ex.world_part(p,e)[0] for p in e['parts']]);print(e['name'],'BBOX',[v.min(0).tolist(),v.max(0).tolist()],'PIVOT',e['pivot_world_m'])
