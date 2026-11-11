import sys,json
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
B=Path('E:/jz/JIA/Rebuild_V19');S=json.loads((B/'08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'));ex.SCENE=S
for e in S['elements']:
 if e['name'].startswith('SITE_GAZEBO') or any(x in e['name'] for x in ['SITE_INNER_STONE_GATEHOUSE','SITE_INNER_GATEHOUSE_UNDER','SITE_GATEHOUSE']):
  vv=[]
  for p in e.get('parts',[]):
   v,_=ex.world_part(p,e);vv.append(v)
  if vv:
   v=np.concatenate(vv);print(e['name'],'BOUNDS',v.min(0).round(5).tolist(),v.max(0).round(5).tolist(),'PARTS',len(e['parts']))
   if not e['name'].startswith('SITE_GAZEBO'):
    for j,p in enumerate(e['parts']):
     v,_=ex.world_part(p,e);print(' ',j,p['material'],v.min(0).round(4).tolist(),v.max(0).round(4).tolist(),p['geometry']['type'])
