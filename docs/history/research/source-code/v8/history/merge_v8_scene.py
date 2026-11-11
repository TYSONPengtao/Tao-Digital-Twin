import sys,json,copy,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');V7=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid')
p=O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json'
old=json.loads((V7/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));S=copy.deepcopy(old)
interior=json.loads((W/'v8_interior/Interior_Patch_V8.json').read_text(encoding='utf-8'))
eaves=json.loads((W/'v8_chinese_eaves/Mutation.json').read_text(encoding='utf-8'))
roman=json.loads((W/'v8_column_arch/Column_Arch_Patch_V8.json').read_text(encoding='utf-8'))
replace={e['name']:e for e in interior['elements']+eaves['replace']+roman['elements']}
delete=set(eaves['remove'])
S['elements']=[copy.deepcopy(replace.get(e['name'],e)) for e in S['elements'] if e['name'] not in delete]+copy.deepcopy(eaves['add'])
for patch in [interior,roman,eaves]:S['definitions'].update(patch.get('definitions',{}))
for k in ['door_registry','openings','rooms','room_connectivity','v8_interior_changes']:S[k]=copy.deepcopy(interior[k])
S['v8_column_arch_changes']=roman['report'];S['v8_changes']=eaves['changes']
S['revision_notes']=S.get('revision_notes',[])+['V8 2026-10-09: user specified stair direction, bathroom layout, terrain-only west farmyard, Chinese flown eaves and Roman column side contacts.']
p.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
prev={e['name']:e for e in old['elements']};now={e['name']:e for e in S['elements']}
changed=[n for n,e in now.items() if prev.get(n)!=e or ('definition' in e and old['definitions'].get(e['definition'])!=S['definitions'].get(e['definition']))]
removed=sorted(set(prev)-set(now))
(O/'02_Data/V8_Changed_Nodes.json').write_text(json.dumps({'changed':changed,'removed':removed},ensure_ascii=False,indent=2),encoding='utf-8')
for srcdir,label in [(W/'v8_interior','Interior'),(W/'v8_chinese_eaves','Chinese_Eaves'),(W/'v8_column_arch','Column_Arch'),(W/'v8_terrain_clear','Terrain_Clearance')]:
    dest=O/'07_Evidence'/label;dest.mkdir(parents=True,exist_ok=True)
    for f in srcdir.iterdir():
        if f.is_file() and f.suffix in ['.json','.md','.png','.jpg','.csv','.py'] and 'Scene' not in f.name and f.name not in ['Mutation.json','Interior_Patch_V8.json','Column_Arch_Patch_V8.json']:
            shutil.copy2(f,dest/f.name)
for name,src in [('Interior_QA_V8.json',W/'v8_interior/Interior_QA_V8.json'),('Chinese_Eaves_Geometry_QA.json',W/'v8_chinese_eaves/Geometry_QA.json'),('Column_Arch_QA.json',W/'v8_column_arch/Column_Arch_QA.json'),('Independent_Terrain_Clearance_QA.json',W/'v8_terrain_clear/Independent_Terrain_Clearance_QA.json')]:shutil.copy2(src,O/'06_Report'/name)
print('Merged',len(changed),'changed/add elements;',len(removed),'removed; V7 untouched',flush=True)
