import bpy,sys,json,math,numpy as np
from pathlib import Path
from mathutils import Vector,kdtree
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_07_common import *
from v24_03_junction_blender import _bounds,_tree,_closed_stats
base=json.loads((R/'V24_07_Before_Snapshot.json').read_text(encoding='utf8'));delta=json.loads((R/'V24_07_Changes.json').read_text(encoding='utf8'));build=json.loads((R/'V24_07_Build.json').read_text(encoding='utf8'));checks=[]
def ck(n,ok,**kw):checks.append({'check':n,'pass':bool(ok),**kw})
# Capture the original shaped pulls in their actual closed world positions.
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;sc.frame_set(1);bpy.context.view_layer.update();oldpull={}
for n in[r['name']for r in delta['doors']['leaves']]:
 o=bpy.data.objects[n];ids={i for f in o.data.polygons if f.material_index==3 for i in f.vertices};oldpull[n]=[tuple(o.matrix_world@o.data.vertices[i].co)for i in ids]
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();allowed=set(delta['declared_changes'])
ck('Only intended gate door and adjacent contact changes',set(delta['changed_objects'])<=allowed);ck('No scene objects removed',not delta['removed_objects'])
for n,r in base['materials'].items():ck('Original shader '+n,n in bpy.data.materials and q._material(bpy.data.materials[n])['hash']==r['hash'])
for n,r in base['images'].items():ck('Packed image '+n,n in bpy.data.images and q._image(bpy.data.images[n])==r)
for n,h in base['actions'].items():ck('Original animation action '+n,n in bpy.data.actions and q._action(bpy.data.actions[n])==h)
for n,r in base['objects'].items():
 o=bpy.data.objects.get(n);ck('Retained original object '+n,o is not None)
 if o is None:continue
 ck('Parent animation and visibility '+n,(o.parent.name if o.parent else None)==r['parent']and q._animation(o)==r['animation']and o.hide_render==r['hide_render'])
 expected=np.array(r['matrix'])
 if n in delta['roof_objects']+delta['attachments']:expected[2,3]+=delta['height']['roof_translation_z_m']
 ck('Original transform or exact marked roof lowering '+n,np.max(np.abs(np.array(q._matrix(o.matrix_world))-expected))<1e-5)
 if r['mesh_hash']and n not in allowed:ck('Original site geometry UV and materials '+n,q._mesh_hash(o.data)==r['mesh_hash'])
for n,h in delta['expected_mesh_hashes'].items():ck('Saved mesh digest '+n,q._mesh_hash(bpy.data.objects[n].data)==h)
for n in delta['supports']+delta['doors']['changed_objects']+delta['doors']['added_objects']:
 o=bpy.data.objects[n];s=_closed_stats(o);ck('Closed positive gate component '+n,s['boundary_edges']==0 and s['volume_m3']>0,**s)
for r in build['kitchen_contacts']:
 s=_closed_stats(bpy.data.objects[r['name']]);ck('Closed kitchen end '+r['name'],s['boundary_edges']==0 and s['volume_m3']>0 and r['materials_preserved']and r['uv_preserved'],**s)
for f,poses in base['door_poses'].items():
 sc.frame_set(int(f));bpy.context.view_layer.update()
 for n,m in poses.items():ck('Original door pose '+n+' frame '+f,q._matrix(bpy.data.objects[n].matrix_world)==m)
sc.frame_set(1);bpy.context.view_layer.update()
for n,pts in oldpull.items():
 o=bpy.data.objects[n];ids={i for f in o.data.polygons if f.material_index==3 for i in f.vertices};kd=kdtree.KDTree(len(ids))
 for j,i in enumerate(ids):kd.insert(o.matrix_world@o.data.vertices[i].co,j)
 kd.balance();dist=[kd.find(Vector(p))[2]for p in pts];ck('Original cast bronze pull retained '+n,max(dist)<1e-5,maximum_vertex_distance_m=max(dist))
 lo,hi=_bounds(o);ck('Original leaf height and 10mm header clearance '+n,abs(lo[2]+.337)<1e-5 and abs(hi[2]-2.0733)<1e-5 and _bounds(bpy.data.objects['SITE_V21_GATE_REFERENCE_FIXED_TIMBER_TRANSOM_Geometry'])[0][2]-hi[2]>.009)
 ck('Same wood and bronze shaders '+n,[m.name for m in o.data.materials]==['M_V21_GATE_REF_06','M_V21_GATE_REF_07','M_V21_GATE_REF_08','M_V23_GATE_CAST_BRONZE'])
# Inspect actual closed/intermediate/open leaf intersections outside the small
# mechanical hinge mounts. These mounts intentionally connect leaf and jamb.
targets=['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry','SITE_V21_GATE_REFERENCE_LAYER_03_Geometry','SITE_V21_GATE_REFERENCE_FIXED_TIMBER_TRANSOM_Geometry','V24_07_Gate_Moulded_Timber_Jambs'];swing=[]
for f in[1,10,20,30,40]:
 sc.frame_set(f);bpy.context.view_layer.update()
 for n in oldpull:
  o=bpy.data.objects[n];hinge=o.matrix_world.translation;pts=[o.matrix_world@v.co for v in o.data.vertices];faces=[]
  for p in o.data.polygons:
   center=sum((pts[i]for i in p.vertices),Vector())/len(p.vertices)
   if p.material_index==3 and math.hypot(center.x-hinge.x,center.y-hinge.y)<.11:continue
   faces.append(list(p.vertices))
  tr=BVHTree.FromPolygons(pts,faces,epsilon=1e-7)
  for t in targets:
   ov=tr.overlap(_tree(bpy.data.objects[t]))
   if ov:swing.append({'frame':f,'door':n,'target':t,'triangle_pairs':len(ov)})
ck('Timber leaves and pulls clear stone header and fixed jambs through inward swing',not swing,collisions=swing)
sc.frame_set(40);bpy.context.view_layer.update();roof=[bpy.data.objects[n]for n in delta['roof_objects']];rb=[[min(_bounds(o)[0][i]for o in roof)for i in range(3)],[max(_bounds(o)[1][i]for o in roof)for i in range(3)]];pb=_bounds(bpy.data.objects['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry']);cy=sum(pb[i][1]for i in[0,1])/2
ck('User marked underside lowered 0.4m to about 3.10m',abs(rb[0][2]-3.10)<1e-5 and abs(delta['height']['roof_translation_z_m']+.4)<1e-5,minimum_underside_z_m=rb[0][2])
ck('No repeated excessive global kitchen clearance',.015<rb[0][2]-delta['height']['user_mark_2_kitchen_coping_hit'][2]<.05,local_clearance_m=rb[0][2]-delta['height']['user_mark_2_kitchen_coping_hit'][2])
ck('Balanced short eaves retained',abs(sum(rb[i][1]for i in[0,1])/2-cy)<1e-5 and abs((pb[0][1]-rb[0][1])-(rb[1][1]-pb[1][1]))<.001)
coll=[];rd=[(o,_bounds(o),_tree(o))for o in roof]
for o in bpy.data.objects:
 if o.type!='MESH'or not(o.name.startswith(('SITE_KITCHEN_','SITE_V22_KITCHEN_','KITCHEN_V22_','V24_Kitchen_','V24_06_Kitchen_'))or o.name in['SITE_V21_GATE_KITCHEN_FLUSH_GABLE_CLOSURE_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry']):continue
 lo,hi=_bounds(o);tr=None
 for ro,bb,rt in rd:
  if any(hi[i]<bb[0][i]or lo[i]>bb[1][i]for i in range(3)):continue
  if tr is None:tr=_tree(o)
  ov=tr.overlap(rt)
  if ov:coll.append({'kitchen':o.name,'gate':ro.name,'triangle_pairs':len(ov)})
ck('No gate kitchen roof surface interpenetration after fitted joint',not coll,collisions=coll)
for n in delta['supports']:ck('Shortened plain upper bearing reaches soffit '+n,_bounds(bpy.data.objects[n])[1][2]>rb[0][2]+.015)
ck('26 moving door roots retained',len(base['doors'])==26);ck('15 real stone relief fields retained',len([o for o in bpy.data.objects if o.name.startswith('V24_Gate_Reference_Relief_')])==15);ck('Original materials enabled',all(v.material_override is None for v in sc.view_layers))
ck('Selected two trees remain absent',all(n not in bpy.data.objects for n in['SITE_TREE_5_Geometry','SITE_TREE_6_Geometry']));ck('One independent veranda post retained','V24_03_Kitchen_Single_Veranda_Column'in bpy.data.objects and 'SITE_KITCHEN_V12_BEFORE_WOOD_15_Geometry'not in bpy.data.objects)
ck('Saved model SHA matches build',sha(P)==build['sha256']);fail=[c for c in checks if not c['pass']];report={'status':'PASS_V24_07_FRESH_BLEND_QA'if not fail else'FAIL_V24_07_FRESH_BLEND_QA','model_sha256':sha(P),'checks':checks,'failures':fail,'height':delta['height'],'materials':len(base['materials']),'images':len(base['images']),'moving_doors':len(base['doors'])};write('V24_07_Fresh_Blend_QA.json',report);print(report['status'],len(checks),len(fail),flush=True)
if fail:raise AssertionError(json.dumps(fail[:20],ensure_ascii=False))
