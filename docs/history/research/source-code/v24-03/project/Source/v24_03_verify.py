"""Fresh native Blender geometry, material, action and site preservation verification."""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as q
O=Path('E:/jz/JIA/Rebuild_V24_03');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_03.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
base=json.loads((R/'V24_03_Before_Snapshot.json').read_text(encoding='utf8'));delta=json.loads((R/'V24_03_Changes.json').read_text(encoding='utf8'));build=json.loads((R/'V24_03_Build.json').read_text(encoding='utf8'))
checks=[]
def ck(label,ok,**kw):checks.append({'check':label,'pass':bool(ok),**kw})
for n,r in base['materials'].items():ck('Original real shader '+n,n in bpy.data.materials and q._material(bpy.data.materials[n])['hash']==r['hash'])
for n,r in base['images'].items():ck('Original packed image '+n,n in bpy.data.images and q._image(bpy.data.images[n])==r)
for n,h in base['actions'].items():ck('Original door action '+n,n in bpy.data.actions and q._action(bpy.data.actions[n])==h)
allowed=set(delta['changed_old_objects']);removed=set(delta['removed_objects']);roof=delta['module_reports']['roof'];junction=delta['module_reports']['junction'];kitchen=delta['module_reports']['kitchen']
planned_removed=set(roof.get('removed_objects',[]))|set(junction.get('removed_objects',[]))|set(kitchen.get('removed_objects',[]))
planned_changed=set(roof.get('changed_old_objects',[]))|set(junction.get('changed_old_objects',[]))|set(kitchen.get('changed_old_objects',[]))
ck('Both junction tests passed',junction['status'].startswith('PASS') and all(r['pass']for r in junction['checks']))
ck('Exactly one independent kitchen veranda post',kitchen['freestanding_veranda_columns']==1 and 'V24_03_Kitchen_Single_Veranda_Column' in bpy.data.objects)
ck('Only declared source objects removed',removed<=planned_removed,actual=sorted(removed),planned=sorted(planned_removed))
ck('Only declared source objects changed',allowed<=planned_changed,actual=sorted(allowed),planned=sorted(planned_changed))
for n,r in base['objects'].items():
 if n in removed:continue
 ob=bpy.data.objects.get(n);ck('Original object retained '+n,ob is not None)
 if ob is None:continue
 ck('Original parent/transform/action '+n,q._matrix(ob.matrix_world)==r['matrix'] and (ob.parent.name if ob.parent else None)==r['parent'] and q._animation(ob)==r['animation'])
 if n not in allowed and r['mesh_hash']:ck('Unmodified site geometry/UV/material '+n,q._mesh_hash(ob.data)==r['mesh_hash'])
for n,h in delta['expected_mesh_hashes'].items():ck('Exact saved mesh readback '+n,n in bpy.data.objects and q._mesh_hash(bpy.data.objects[n].data)==h)
newstats=[]
for n in delta['added_objects']:
 ob=bpy.data.objects[n]
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data);boundary=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
 ck('Closed finite new solid '+n,boundary==0 and vol>1e-10 and all(abs(c)<1e6 for v in ob.data.vertices for c in v.co),non_manifold_edges=boundary,volume_m3=vol)
 ck('Original material and UV on new solid '+n,bool(ob.data.uv_layers) and all(m and m.name in base['materials'] for m in ob.data.materials))
 newstats.append({'name':n,'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'volume_m3':vol})
for frame,poses in base['door_poses'].items():
 sc.frame_set(int(frame));bpy.context.view_layer.update()
 for n,m in poses.items():ck('Door pose '+n+' frame '+frame,n in bpy.data.objects and q._matrix(bpy.data.objects[n].matrix_world)==m)
sc.frame_set(40);bpy.context.view_layer.update()
ck('All original 26 moving door roots retained',len(base['doors'])==26 and all(n in bpy.data.objects for n in base['doors']))
ck('All 15 carved fields retained',len([ob for ob in bpy.data.objects if ob.name.startswith('V24_Gate_Reference_Relief_')])==15)
ck('No white/clay override',all(v.material_override is None for v in sc.view_layers))
from mathutils.bvhtree import BVHTree
from v24_xieshan_roof_blender import fitted_bearing_z,CX,CY
def world_tree(n):
 ob=bpy.data.objects[n];return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(p.vertices)for p in ob.data.polygons])
core=world_tree('V24_XIESHAN_09_Continuous_Eave_Bearing_Core');mould=world_tree('V24_XIESHAN_08_Five_Continuous_Stepped_Eave_Bands');clear=[]
for z0,z1 in [(2.655,2.695),(2.695,2.736),(2.736,2.770),(2.770,2.815),(2.815,2.865)]:
 z=fitted_bearing_z((z0+z1)/2);origin=Vector((CX,CY-2,z));dm=mould.ray_cast(origin,Vector((0,1,0)),5);dc=core.ray_cast(origin,Vector((0,1,0)),5);ok=dm[0]is not None and dc[0]is not None and dc[3]-dm[3]>.025;clear.append({'z_m':z,'pass':bool(ok),'core_inset_m':float(dc[3]-dm[3])if ok else None})
ck('All five eave fascia levels exposed ahead of bearing core',all(r['pass']for r in clear),ray_tests=clear)
beam=bpy.data.objects['SITE_KITCHEN_V12_BEFORE_WOOD_04_Geometry'];wall=bpy.data.objects['V24_03_Kitchen_Rear_Gable_Wall'];beam_y=max((beam.matrix_world@Vector(v)).y for v in beam.bound_box);wall_y=min((wall.matrix_world@Vector(v)).y for v in wall.bound_box)
ck('Rear lintel has real masonry bearing',beam_y-wall_y>=.01,embedded_length_m=beam_y-wall_y)
with P.open('rb') as f:model_sha=hashlib.file_digest(f,'sha256').hexdigest()
ck('Saved model matches build digest',model_sha==build['model_sha256'])
fail=[r for r in checks if not r['pass']];report={'status':'PASS_V24_03_FRESH_BLEND_QA' if not fail else 'FAIL_V24_03_FRESH_BLEND_QA','model':str(P),'model_sha256':model_sha,'checks':checks,'failures':fail,'new_geometry':newstats,'retained_materials':len(base['materials']),'retained_images':len(base['images']),'door_roots':len(base['doors'])}
(R/'V24_03_Fresh_Blend_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(report['status'],len(checks),len(fail),flush=True)
if fail:raise AssertionError(json.dumps(fail[:12],ensure_ascii=False))
