import json,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid');p=O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
baseline=read(O/'06_Report/V9_Baseline_Hashes.json');assert sha(p)==baseline['baseline_scene_sha256'],'Scene already edited; do not merge twice'
S=read(p);shutil.copy2(p,O/'07_Evidence/V9_Scene_Before_Local_Eave_Repair.json');names={e['name']:e for e in S['elements']};changed=[];removed=[];changes=[];sources=[]
for folder,label in [('v9_roof_relation','Roof_Relation'),('v9_eave_layers','Visible_Eave_Layers')]:
 mpath=W/folder/'Mutation.json';m=read(mpath);qa=read(W/folder/'Geometry_QA.json');assert qa['status'].startswith('PASS')
 scope_names=[e['name'] for e in m['replace']+m['add']]+m['remove'];assert not(set(scope_names)&set(changed+removed)),scope_names
 for e in m['replace']:assert e['name'] in names;names[e['name']]=e;changed.append(e['name'])
 for e in m['add']:assert e['name'] not in names;names[e['name']]=e;changed.append(e['name'])
 for n in m['remove']:assert n in names;del names[n];removed.append(n)
 for n,d in m['definitions'].items():assert n not in S['definitions'];S['definitions'][n]=d
 S['materials'].update(m['materials']);changes.extend(m['changes']);sources.append({'patch':str(mpath),'sha256':sha(mpath),'names':scope_names})
 dest=O/'07_Evidence'/folder;dest.mkdir(exist_ok=True)
 for src in (W/folder).iterdir():
  if src.is_file():shutil.copy2(src,dest/src.name)
 shutil.copy2(W/folder/'Geometry_QA.json',O/'06_Report'/f'{label}_Geometry_QA.json')
S['elements']=list(names.values());S['name']='Production_1QK_Architecture_V9';S['v9_changes']=changes;S['revision_notes'].append('V9: local kitchen lower roof underlap beneath higher gate eave; visible gray gate eave layers and kitchen timber/metal trim; V8 user-deleted third-floor beam remains absent. Hidden battens not modelled as measured.')
save(p,S)
save(O/'02_Data/V9_Changed_Nodes.json',{'changed':sorted(changed),'removed':sorted(removed),'retired_current_user_elements':['BEAM_X_F3_2.1_0'],'sources':sources,'scene_sha256':sha(p)})
scope=read(O/'02_Data/V8_Allowed_Repair_Scope.json');scope['V9_scope_note']='Geometry regenerated only for named eave joint elements inside inherited authorized repair scope; no original source mesh edits.';save(O/'02_Data/V9_Allowed_Repair_Scope.json',scope)
reg=read(O/'02_Data/Interaction_Registry_V8.json');reg['version']='V9';reg['source_scene_sha256']=sha(p);reg['V9_scene_sha256']=sha(p);reg['V9_door_layout_changed']=False;save(O/'02_Data/Interaction_Registry_V9.json',reg)
save(O/'06_Report/V9_Merge_Manifest.json',{'status':'PASS','changed':sorted(changed),'removed':sorted(removed),'retained_user_deleted_beam':True,'sources':sources,'scene_sha256':sha(p),'original_source_meshes_modified':False})
print('Merged V9',len(changed),'changed/new nodes; removed',removed,flush=True)
