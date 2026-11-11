import json,copy
from pathlib import Path
W=Path(__file__).parent;D=W/'v22';D.mkdir(exist_ok=True);B=Path('E:/jz/JIA/Rebuild_V21')
Q={'replace':[],'add':[],'remove':[],'materials':{},'cameras':[],'change_notes':[]};seen={}
E={e['name']:e for e in json.loads((B/'08_Editable_Source/Architecture_Scene_V21.json').read_text(encoding='utf8'))['elements']}
DM=json.loads((B/'02_Data/Door_Manifest_V21.json').read_text(encoding='utf8'));doors={r['name']:r for r in DM['doors']}
for r in doors.values():r.setdefault('operation','HINGED_INWARD')
for task in ['house','gate','kitchen','pavilion','wall']:
 p=W/f'v22_{task}'/'Mutation.json';a=json.loads(p.read_text(encoding='utf8'))
 for k in ['replace','add']:
  for e in a.get(k,[]):
   n=e['name'];assert n not in seen,('conflicting owner',n,task,seen.get(n));seen[n]=task
   assert (n in E)==(k=='replace'),(k,n,'baseline presence',n in E)
   Q[k].append(e)
 Q['remove']+=a.get('remove',[])
 for n,m in a.get('materials',{}).items():
  assert n not in Q['materials'] or Q['materials'][n]==m,('material conflict',n)
  Q['materials'][n]=m
 Q['cameras']+=a.get('cameras',[]);Q['change_notes']+=a.get('change_notes',[])
 dp=p.parent/'Door_Updates.json'
 if dp.exists():
  du=json.loads(dp.read_text(encoding='utf8'))
  for n in du.get('remove',[]):doors.pop(n,None)
  for r in du.get('upsert',[]):doors[r['name']]=r
Q['remove']=list(dict.fromkeys(Q['remove']));assert not set(Q['remove']).intersection(seen)
for n in Q['remove']:doors.pop(n,None)
final=set(E).difference(Q['remove']).union(seen)
for n,r in doors.items():
 assert n in final,(n,'door missing')
 assert r.get('operation','HINGED_INWARD') in ['HINGED_INWARD','SLIDING']
 assert len(r['hinge_local_m'])==3
 if r.get('operation')=='SLIDING':assert len(r['open_translation_m'])==3
 else:assert 'open_angle_deg' in r
DM.update(default_pose='OPEN; hinged doors inward, house front glass leaves slide laterally',doors=list(doors.values()),version='V22',ue_engine_tested=False)
for c in Q['cameras']:
 if c[0]=='V22_Inner_Gate_Ideal_Compare':c[1:]=[[6.6,-16.7,1.7],[6.6,-11.65,1.7],74]
names=[r[0] for r in Q['cameras']];assert len(set(names))==len(names)
(D/'Door_Manifest.json').write_text(json.dumps(DM,ensure_ascii=False,indent=2),encoding='utf8')
(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
print('V22 PATCH',len(Q['replace']),len(Q['add']),len(Q['remove']),'DOORS',len(doors),'VIEWS',len(names),flush=True)
