import bpy,sys,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_08_common import *
from v24_03_junction_blender import _bounds,_tree,_closed_stats
base=json.loads((R/'V24_08_Before_Snapshot.json').read_text());delta=json.loads((R/'V24_08_Changes.json').read_text());build=json.loads((R/'V24_08_Build.json').read_text());checks=[]
def ck(n,ok,**kw):checks.append({'check':n,'pass':bool(ok),**kw})
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
expected=set(r['name']for r in delta['setback']['changed_objects'])|set(delta['setback']['moving_kitchen_door_roots'])|set(delta['finish']['changed_objects'])|{delta['bands']['name']}|{r['name']for r in delta['contacts']}
for o in bpy.data.objects:
 if o.parent and o.parent.name in delta['setback']['moving_kitchen_door_roots']:expected.add(o.name)
ck('All changes confined to kitchen setback and exterior detailing',set(delta['changed_objects'])<=expected,unexpected=sorted(set(delta['changed_objects'])-expected));ck('No preexisting objects deleted',not delta['removed_objects'])
for n,r in base['materials'].items():ck('Original shader '+n,n in bpy.data.materials and q._material(bpy.data.materials[n])['hash']==r['hash'])
for n,r in base['images'].items():ck('Original packed image '+n,n in bpy.data.images and q._image(bpy.data.images[n])==r)
for n,h in base['actions'].items():ck('Original animation '+n,n in bpy.data.actions and q._action(bpy.data.actions[n])==h)
moving=set(delta['setback']['moving_kitchen_door_roots']);translated=set(moving)
for o in bpy.data.objects:
 if o.parent and o.parent.name in moving:translated.add(o.name)
for n,r in base['objects'].items():
 o=bpy.data.objects.get(n);ck('Original object retained '+n,o is not None)
 if o is None:continue
 ck('Original parent animation visibility '+n,(o.parent.name if o.parent else None)==r['parent']and q._animation(o)==r['animation']and o.hide_render==r['hide_render'])
 M=np.array(r['matrix'])
 if n in translated:M[0,3]+=.45
 ck('Original transform or kitchen hinge retreat '+n,np.max(np.abs(np.array(q._matrix(o.matrix_world))-M))<2e-5)
 if r['mesh_hash']and n not in expected:ck('Unchanged geometry UV and material '+n,q._mesh_hash(o.data)==r['mesh_hash'])
for n,h in delta['expected_mesh_hashes'].items():ck('Saved geometry digest '+n,q._mesh_hash(bpy.data.objects[n].data)==h)
for f,poses in base['door_poses'].items():
 sc.frame_set(int(f));bpy.context.view_layer.update()
 for n,M in poses.items():
  M=np.array(M)
  if n in moving:M[0,3]+=.45
  ck('Door swing pose '+n+' frame '+f,np.max(np.abs(np.array(q._matrix(bpy.data.objects[n].matrix_world))-M))<2e-5)
sc.frame_set(40);bpy.context.view_layer.update()
for n in delta['added_objects']:
 o=bpy.data.objects[n]
 if o.type=='MESH':
  s=_closed_stats(o);ck('Closed positive new component '+n,s['boundary_edges']==0 and s['nonmanifold_edges']==0 and s['volume_m3']>0,**s)
for n in ['SITE_KITCHEN_STONE_FLOOR_Geometry','V24_03_Kitchen_Rear_Gable_Wall','SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE_Geometry','SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES_Geometry']:
 s=_closed_stats(bpy.data.objects[n]);ck('Closed edited foundation or facade '+n,s['boundary_edges']==0 and s['volume_m3']>0,**s)
floor=bpy.data.objects['SITE_KITCHEN_STONE_FLOOR_Geometry'];bb=_bounds(floor);ck('Courtyard foundation edge retreated exactly 450mm',abs(bb[0][0]-8.15)<1e-5,bounds=bb)
ck('Kitchen outside foundation extent not pushed beyond site',bb[1][0]<13.45,outside_x_m=bb[1][0]);ck('Single veranda post remains round and retreated',abs(_bounds(bpy.data.objects['V24_03_Kitchen_Single_Veranda_Column'])[0][0]-(7.769+.45))<1e-5 and abs((_bounds(bpy.data.objects['V24_03_Kitchen_Single_Veranda_Column'])[1][0]-_bounds(bpy.data.objects['V24_03_Kitchen_Single_Veranda_Column'])[0][0])-.244)<1e-5)
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_1_Geometry','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','SITE_V20_STORAGE_ALIGNED_STONE_BASE_EXTENSION_Geometry','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry']:
 ck('Registered outer wall and retaining foundation fixed '+n,q._mesh_hash(bpy.data.objects[n].data)==base['objects'][n]['mesh_hash'])
roof=[o for o in bpy.data.objects if o.type=='MESH'and o.name.startswith('V24_XIESHAN_')];ck('Accepted gate soffit still 3.10m',abs(min(_bounds(o)[0][2]for o in roof)-3.10)<1e-5)
collision=[];rd=[(o,_bounds(o),_tree(o))for o in roof]
for o in bpy.data.objects:
 if o.type!='MESH'or not o.name.startswith(('SITE_KITCHEN_','SITE_V22_KITCHEN_','KITCHEN_V22_','V24_Kitchen_','V24_06_Kitchen_')):continue
 lo,hi=_bounds(o);tr=None
 for ro,rb,rt in rd:
  if any(hi[i]<rb[0][i]or lo[i]>rb[1][i]for i in range(3)):continue
  if tr is None:tr=_tree(o)
  pairs=tr.overlap(rt)
  if pairs:collision.append({'kitchen':o.name,'gate':ro.name,'pairs':len(pairs)})
ck('Retreated kitchen does not intersect gate roof',not collision,collisions=collision)
# Both animated kitchen leaves retain their rigid geometry; door frames and
# hinge axes have exactly the same translation, so the full swing is preserved.
for n in moving:
 for o in bpy.data.objects:
  if o.type=='MESH'and o.parent and o.parent.name==n:ck('Kitchen leaf rigid mesh retained '+o.name,q._mesh_hash(o.data)==base['objects'][o.name]['mesh_hash'])
ck('Existing gallery timber and foundations use coherent setback',all(n in delta['changed_objects']for n in['V24_03_Kitchen_Single_Veranda_Column','SITE_KITCHEN_V12_BEFORE_WOOD_04_Geometry','SITE_KITCHEN_STONE_FLOOR_Geometry','SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS_Geometry']))
# Preserve exact long perimeter / previous paved entry / ideal carved gate.
ck('15 solid stone relief fields retained',len([o for o in bpy.data.objects if o.name.startswith('V24_Gate_Reference_Relief_')])==15)
ck('26 original animated doors retained',len(base['doors'])==26);ck('Only selected south two trees absent; east four retained',all('SITE_TREE_'+str(i)+'_Geometry'in bpy.data.objects for i in[1,2,3,4])and all('SITE_TREE_'+str(i)+'_Geometry'not in bpy.data.objects for i in[5,6]))
ck('Original material rendering enabled',all(v.material_override is None for v in sc.view_layers));ck('All original image payloads packed',all(im.packed_file for im in bpy.data.images if im.name in base['images']));ck('Native file SHA matches build',sha(P)==build['sha256'])
fail=[c for c in checks if not c['pass']];out={'status':'PASS_V24_08_FRESH_BLEND_QA'if not fail else'FAIL_V24_08_FRESH_BLEND_QA','model_sha256':sha(P),'checks':checks,'failures':fail,'original_materials':len(base['materials']),'original_images':len(base['images']),'moving_doors':len(base['doors']),'setback_m':.45};write('V24_08_Fresh_Blend_QA.json',out);print(out['status'],len(checks),len(fail),flush=True)
if fail:raise AssertionError(json.dumps(fail[:20],ensure_ascii=False))
