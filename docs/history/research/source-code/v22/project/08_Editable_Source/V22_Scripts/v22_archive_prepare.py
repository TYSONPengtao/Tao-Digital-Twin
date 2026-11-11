import json
from pathlib import Path
W=Path(__file__).parent;D=W/'v22_pavilion';q=json.loads((D/'Mutation.json').read_text(encoding='utf8'))
q['replace']=[e for e in q['replace'] if e['name']!='SITE_GAZEBO_V11_KNEE_BRACES']
q['change_notes']=[s for s in q['change_notes'] if not s.startswith('按最新“正确亭子”')]
(D/'Photo_Patch_Input.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8')
print('ARCHIVE INPUT PREPARED')
