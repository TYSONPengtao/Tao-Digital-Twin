import json
from pathlib import Path
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V9_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
print('SITE',json.dumps(S['site'],ensure_ascii=False)[:20000])
for e in S['elements']:
 if e['name'] in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1','SITE_COURTYARD_WEST_TILE_WALL','SITE_COURTYARD_WEST_TILE_WALL_TILE_COPING','SITE_GATE_EAST_FLANK','SITE_GATE_EAST_FLANK_TILE_COPING']:
  print(e['name'],json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False))
  print('MAT', {p.get('material') for p in e['parts']})
