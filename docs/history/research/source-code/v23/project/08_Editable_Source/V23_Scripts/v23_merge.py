import json,copy,shutil
from pathlib import Path
W=Path(__file__).parent;D=W/'v23';D.mkdir(exist_ok=True);B=Path('E:/jz/JIA/Rebuild_V22')
E={e['name']:e for e in json.loads((B/'08_Editable_Source/Architecture_Scene_V22.json').read_text(encoding='utf8'))['elements']}
Q={'replace':[],'add':[],'remove':[],'materials':{},'cameras':[],'change_notes':[]};seen=set()
for task in ['gate_relief','gate_roof','gate_wood','gate_junction']:
 p=W/f'v23_{task}'/'Mutation.json';m=json.loads(p.read_text(encoding='utf8'))
 ctrl=json.loads((p.parent/'Design_Control.json').read_text(encoding='utf8'));assert ctrl['status'].startswith('PASS')
 for kind in ['replace','add']:
  for e in m[kind]:
   assert e['name'] not in seen;seen.add(e['name']);assert (e['name'] in E)==(kind=='replace')
   Q[kind].append(e)
 Q['remove']+=m['remove'];Q['materials'].update(m['materials']);Q['cameras']+=m['cameras'];Q['change_notes']+=m['change_notes']
assert not set(Q['remove'])&seen
compact=W/'v23_gate_roof_refit/Mutation.json'
if compact.exists():
 a=json.loads(compact.read_text(encoding='utf8'));ns={e['name'] for e in a['replace']}
 Q['replace']=[e for e in Q['replace'] if e['name'] not in ns]+a['replace'];Q['change_notes']+=a['change_notes']
DM=json.loads((B/'02_Data/Door_Manifest_V22.json').read_text(encoding='utf8'));DM.update(version='V23',ue_engine_tested=False)
assert len(DM['doors'])==26 and sum(r['operation']=='SLIDING' for r in DM['doors'])==4
for r in DM['doors']:assert r['name'] in E and r['name'] not in Q['remove']
(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
(D/'Door_Manifest.json').write_text(json.dumps(DM,ensure_ascii=False,indent=2),encoding='utf8')
print('V23 PATCH',len(Q['replace']),len(Q['add']),len(Q['remove']),'doors',len(DM['doors']),flush=True)
