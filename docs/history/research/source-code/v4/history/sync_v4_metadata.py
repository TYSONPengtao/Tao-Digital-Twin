import json
from pathlib import Path
p=Path(r'E:\jz\JIA\Rebuild_V4\05_Intermediate\Architecture_Scene.json');s=json.loads(p.read_text(encoding='utf-8'));by={e['name']:e for e in s['elements']}
for o in s['openings']:
 n=o['name']
 if n in ['DOOR_BACKROOM_F2_R','DOOR_BACKROOM_F3_R']:
  o['previous_name']=n;o['previous_origin']=o['origin'];n=n.replace('BACKROOM','BATH')
 e=by.get(n)
 if e and 'definition' in e:o.update(name=n,origin=e['origin'],angle=e.get('angle',0),definition=e['definition'])
p.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
print('Opening registry synchronized to corrected native placements; geometry unchanged')
