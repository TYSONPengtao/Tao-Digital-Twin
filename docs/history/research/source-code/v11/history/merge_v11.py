import sys,json,shutil,hashlib,copy
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
from shapely.geometry import Polygon
from shapely.ops import unary_union
O=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid');p=O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(p)==read(O/'06_Report/V11_Baseline_Hashes.json')['baseline_scene_sha256']
S=read(p);names={e['name']:e for e in S['elements']};changed=[];removed=[];changes=[];sources=[];door_add=[]
folders=['v11_wall_junction','v11_pavilion','v11_outer_gate','v11_kitchen_interface']
for folder in folders:
 mp=W/folder/'Mutation.json';assert mp.exists(),folder
 m=read(mp);qa=read(W/folder/'Geometry_QA.json');assert str(qa.get('status','')).startswith('PASS') or qa.get('pass_') is True,folder
 if m.get('source_scene_sha256'):assert m['source_scene_sha256']==sha(p)
 ns=[e['name'] for e in m['replace']+m['add']]+m.get('remove',[]);assert not(set(ns)&set(changed+removed)),(folder,'conflicting changes')
 for e in m['replace']:assert e['name'] in names;names[e['name']]=e;changed.append(e['name'])
 for e in m['add']:assert e['name'] not in names;names[e['name']]=e;changed.append(e['name'])
 for n in m.get('remove',[]):assert n in names;del names[n];removed.append(n)
 for n,d in m.get('definitions',{}).items():assert n not in S['definitions'];S['definitions'][n]=d
 S['materials'].update(m.get('materials',{}));changes.extend(m['changes'] if isinstance(m['changes'],list) else [m['changes']]);sources.append({'folder':folder,'sha256':sha(mp),'names':ns})
 door_add.extend(m.get('door_registry_additions',[]))
 dest=O/'07_Evidence'/folder;dest.mkdir(exist_ok=True)
 for src in (W/folder).iterdir():
  if src.is_file():shutil.copy2(src,dest/src.name)
  elif src.is_dir() and src.name=='Evidence':shutil.copytree(src,dest/src.name,dirs_exist_ok=True)
S['elements']=list(names.values());S['name']='Production_1QK_Architecture_V11';S['v11_changes']=changes
S['revision_notes'].append('V11 user corrections: right-angle courtyard corner, wholly internal modern Chinese timber pavilion, DNG-supported kitchen outer wall interface, completed west outer wall and actual four-panel exterior gate. Prior main-building/room/eave corrections and original scan photographs preserved. Reference dimensions provisional.')
if door_add:
 ids={r['door_id'] for r in S['door_registry']}
 for r in door_add:assert r['door_id'] not in ids;ids.add(r['door_id']);S['door_registry'].append(r)
save(p,S);save(O/'02_Data/V11_Changed_Nodes.json',{'changed':sorted(changed),'removed':sorted(removed),'sources':sources,'scene_sha256':sha(p)})
# The user explicitly corrects these local structures and requests completion
# of the outer wall/gate: extend allowed patch footprints, never modify scan.
ex.SCENE=S;scope=read(O/'02_Data/V11_Allowed_Repair_Scope.json');pieces=[]
for e in S['elements']:
 if e['name'] not in changed:continue
 for part in ex.expand_parts(e):
  v,f=ex.world_part(part,e)
  if v is None:continue
  q=Polygon(v[:,:2]).convex_hull
  if not q.is_empty:pieces.append(q.buffer(.03))
add=unary_union(pieces);polys=list(add.geoms) if add.geom_type=='MultiPolygon' else [add]
for q in polys:
 if q.geom_type=='Polygon':scope['polygons'].append({'outer':list(q.exterior.coords),'holes':[list(i.coords) for i in q.interiors],'role':'V11_EXPLICIT_USER_CORRECTED_STRUCTURE_ONLY','source':'User 2026-10-09 annotated corner/pavilion/kitchen/external gate and missing-wall screenshots'})
scope['source_meshes_modified']=False;scope['added_footprint_area_m2']=add.area;save(O/'02_Data/V11_Allowed_Repair_Scope.json',scope)
reg=read(O/'02_Data/Interaction_Registry_V10.json');reg['version']='V11';reg['source_scene_sha256']=sha(p);reg['V11_interior_door_layout_changed']=False;reg['V11_exterior_gate_additions']=door_add;reg['door_registry']=copy.deepcopy(S['door_registry']);save(O/'02_Data/Interaction_Registry_V11.json',reg)
save(O/'06_Report/V11_Merge_Manifest.json',{'status':'PASS','changed':changed,'removed':removed,'sources':sources,'scene_sha256':sha(p),'source_meshes_modified':False,'new_explicitly_authorized_footprints_m2':add.area,'door_registry_added':len(door_add)})
print('Merged V11',len(changed),'changed',len(removed),'removed',len(door_add),'gate registry rows',flush=True)
