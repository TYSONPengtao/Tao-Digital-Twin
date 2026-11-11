import json
from pathlib import Path
S=json.loads(Path(r'E:/jz/JIA/Rebuild_V9_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));E={e['name']:e for e in S['elements']}
print(E['KZ_1_1_F1'])
