import json,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid');p=O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(p)==read(O/'06_Report/V10_Baseline_Hashes.json')['baseline_scene_sha256']
S=read(p);names={e['name']:e for e in S['elements']};changed=[];removed=[];changes=[];sources=[]
for folder in ['v10_courtyard_wall','v10_perimeter_detail']:
 mp=W/folder/'Mutation.json';m=read(mp);qa=read(W/folder/'Geometry_QA.json');assert qa['status'].startswith('PASS')
 ns=[e['name'] for e in m['replace']+m['add']]+m['remove'];assert not(set(ns)&set(changed+removed))
 for e in m['replace']:assert e['name'] in names;names[e['name']]=e;changed.append(e['name'])
 for e in m['add']:assert e['name'] not in names;names[e['name']]=e;changed.append(e['name'])
 for n in m['remove']:assert n in names;del names[n];removed.append(n)
 for n,d in m['definitions'].items():assert n not in S['definitions'];S['definitions'][n]=d
 S['materials'].update(m['materials']);changes.extend(m['changes'] if isinstance(m['changes'],list) else [m['changes']]);sources.append({'folder':folder,'sha256':sha(mp),'names':ns})
 dest=O/'07_Evidence'/folder;dest.mkdir(exist_ok=True)
 for src in (W/folder).iterdir():
  if src.is_file():shutil.copy2(src,dest/src.name)
S['elements']=list(names.values());S['name']='Production_1QK_Architecture_V10';S['v10_changes']=changes;S['revision_notes'].append('V10: Chinese courtyard wall reference detail with individual tiles/bricks, real lattice holes and stepped panels. Existing wall route, openings, retaining stone bases, V9 roof junctions and room changes preserved. Diagram dimensions remain provisional.')
save(p,S);save(O/'02_Data/V10_Changed_Nodes.json',{'changed':sorted(changed),'removed':sorted(removed),'sources':sources,'scene_sha256':sha(p)})
reg=read(O/'02_Data/Interaction_Registry_V9.json');reg['version']='V10';reg['source_scene_sha256']=sha(p);reg['V10_door_layout_changed']=False;save(O/'02_Data/Interaction_Registry_V10.json',reg)
dest=O/'07_Evidence/v10_wall_audit';shutil.copytree(W/'v10_wall_audit',dest,dirs_exist_ok=True)
save(O/'06_Report/V10_Merge_Manifest.json',{'status':'PASS','changed':changed,'removed':removed,'sources':sources,'scene_sha256':sha(p),'original_source_meshes_modified':False})
print('Merged V10',len(changed),'changed',len(removed),'removed',sum(len(e.get('parts',[])) for e in m['replace']+m['add']),'lastpatch parts',flush=True)
