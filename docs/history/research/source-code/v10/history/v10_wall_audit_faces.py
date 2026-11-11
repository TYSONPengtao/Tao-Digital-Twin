import json
from pathlib import Path
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V9_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));E={e['name']:e for e in S['elements']}
print(E['SITE_COURTYARD_WEST_WHITE_INSIDE']['parts'])
print('source texture refs',str(S['materials'])[:2000])
for n in ['SITE_GATE_EAST_FLANK','SITE_COURTYARD_WEST_TILE_WALL']:
 print(n,'faces metadata',[(p['material'],len(p['geometry']['vertices']),p['geometry']['vertices'][:4]) for p in E[n]['parts']])
