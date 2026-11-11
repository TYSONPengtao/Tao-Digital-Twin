from pathlib import Path
import json,sys
W=Path(__file__).parents[1];sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
S=json.loads(Path('E:/jz/JIA/Rebuild_V19/08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'));ex.SCENE=S
for e in S['elements']:
 n=e['name']
 if n.startswith(('PARTITIONS','SLAB','FLOOR','STAIR','DOOR_FRONT','WIN_','WINDOW_')) or n in ['GROUND_FLOOR_TILE_GRID','ENTRY_PORCH_SLAB','MAIN_HOUSE_PORCH','SITE_COURT_PAVER_FLOOR'] or ('FLOOR' in n and not n.startswith('SITE')):
  ps=ex.expand_parts(e);v=np.concatenate([ex.world_part(p,e)[0] for p in ps]);print(n,len(ps),np.round([v.min(0),v.max(0)],4).tolist())
  if n.startswith(('PARTITIONS','FLOOR','DOOR_FRONT')):print(json.dumps(e,ensure_ascii=False)[:10000])
print('MATERIALS',json.dumps({k:v for k,v in S['materials'].items() if any(t in k.upper() for t in ['FLOOR','WOOD','TILE','MARBLE','PLASTER'])},ensure_ascii=False))
print('FLOOR_NAMES',[e['name'] for e in S['elements'] if any(q in e['name'] for q in ['FLOOR','PLINTH','SLAB','TERRAZZO','TILE_GRID'])])
