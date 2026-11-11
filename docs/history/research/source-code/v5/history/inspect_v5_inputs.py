import json
from pathlib import Path
s=json.loads(Path(r'E:\jz\JIA\Rebuild_V4\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
for e in s['elements']:
 if 'STUDY' in e['name'] or (e['layer']=='11_WALL_INT' and e['name']=='PARTITIONS_JOINED_F3'):
  print(json.dumps(e,ensure_ascii=False))
print('Materials',[(k,v) for k,v in s['materials'].items() if 'Wood' in k or 'Glass' in k or 'FRAME' in k])
