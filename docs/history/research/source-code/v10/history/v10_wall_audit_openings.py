import json,math
from pathlib import Path
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V9_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8')); E={e['name']:e for e in S['elements']}
for n in ['SITE_GATE_EAST_FLANK','SITE_GATE_EAST_FLANK_TILE_COPING','SITE_INNER_DARK_TIMBER_DOORS','SITE_INNER_STONE_GATEHOUSE','SITE_COURTYARD_WEST_WHITE_INSIDE']:
 print(n,json.dumps({k:v for k,v in E[n].items() if k!='parts'},ensure_ascii=False))
print('retire',str(S.get('v8_changes'))[:3500]);print('gatenames',[(e['name'],e.get('classification')) for e in S['elements'] if 'GATE' in e['name']]);print('otherwallnames',[(e['name'],e.get('classification')) for e in S['elements'] if 'WALL' in e['name'] and e['layer']=='60_SITE'])
print('gap',math.dist([-14.97732094598484,-8.325656081075762],[-12.501865173706502,-12.863215399690171]))
