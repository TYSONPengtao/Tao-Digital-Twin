from pathlib import Path
import json,collections
W=Path(__file__).parent;D=W/'v25';D.mkdir(exist_ok=True);b=json.loads((W/'v24_37/Before_Snapshot.json').read_text());rows=[]
for name,mat in b['materials'].items():
 if name.startswith(('M_PTJIA6_','M_MB7_','M_V14_ORIGINAL_EXTERIOR_')):continue
 shader=mat['shader'];nodes=shader.get('nodes',[]);rows.append({'name':name,'types':dict(collections.Counter(n['type']for n in nodes)),'images':[(n['name'],n.get('image'))for n in nodes if n['type']=='ShaderNodeTexImage'],'links':shader.get('links',[]),'base_inputs':[(n['name'],n['inputs'])for n in nodes if n['type']=='ShaderNodeBsdfPrincipled']})
(D/'Material_Probe.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');print('NON_PHOTO_MATERIALS',len(rows))
for r in rows:print(r['name'],r['types'],r['images'])
