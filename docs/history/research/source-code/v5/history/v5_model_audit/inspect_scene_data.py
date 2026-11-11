import json
from pathlib import Path
s=json.loads(Path(r'E:\jz\JIA\Rebuild_V4\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
print('keys',list(s));print('levels',s.get('levels'));print('grid',s.get('grid'))
for k in ['openings','walls','rooms']:
 print(k,json.dumps(s.get(k),ensure_ascii=False)[:8000])
for e in s['elements']:
 if e['layer']=='30_DOOR' or e['layer']=='11_WALL_INT':print(json.dumps(e,ensure_ascii=False))
for k,v in s['definitions'].items():
 if 'DOOR' in k:print('DEFINITION',k,json.dumps(v,ensure_ascii=False))
