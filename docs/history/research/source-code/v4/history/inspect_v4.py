import json
from pathlib import Path
s=json.loads(Path(r'E:\jz\JIA\Rebuild_V3\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
for e in s['elements']:
 if any(k in e['name'] for k in ['WINDOW','WIN_','CANOPY','SITE_SHED','SITE_COURTYARD','SITE_EARTH','BALCONY','UTILITY','COURTYARD','ROOF_MAIN','GATE_METAL']):
  print(e['name'],e.get('definition'),e.get('origin'),len(e.get('parts',[])),json.dumps(e.get('parameters',{})))
print('KEYS',list(s));print('MATS',list(s['materials']));print('coordinate',s['coordinate'])
print('WINDOW_DEFINITION')
for k,v in s['definitions'].items():
 if k.startswith('WIN'): print(k,json.dumps(v)[:1800]);break
