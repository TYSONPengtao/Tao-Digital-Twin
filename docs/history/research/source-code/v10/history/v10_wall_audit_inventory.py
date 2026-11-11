import json,sys
from pathlib import Path
W=Path(r'work/v10_wall_audit');W.mkdir(exist_ok=True)
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V9_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
print(S.keys())
for e in S['elements']:
 n=e['name']
 if ('SITE' in n and any(k in n for k in ['WALL','GATE','SCREEN','FENCE'])):
  print(n,'parts',len(e.get('parts',[])),'keys',list(e.keys()))
  print(' first',str(e.get('parts',[])[:1])[:550])
(W/'Wall_Nodes.json').write_text(json.dumps([e for e in S['elements'] if 'SITE' in e['name'] and any(k in e['name'] for k in ['WALL','GATE','SCREEN','FENCE'])],ensure_ascii=False),encoding='utf-8')
