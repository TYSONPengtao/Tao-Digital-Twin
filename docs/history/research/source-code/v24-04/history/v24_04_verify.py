import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_04_common import *
from v24_03_junction_blender import _bounds,_tree,_closed_stats
from v24_04_roof import fitted_bearing_z,CX,CY
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
base=json.loads((R/'V24_04_Before_Snapshot.json').read_text(encoding='utf8'));delta=json.loads((R/'V24_04_Changes.json').read_text(encoding='utf8'));contact=json.loads((R/'V24_04_Closure_and_Contact.json').read_text(encoding='utf8'));build=json.loads((R/'V24_04_Build.json').read_text(encoding='utf8'))
checks=[]
def ck(n,ok,**kw):checks.append({'check':n,'pass':bool(ok),**kw})
for n,r in base['materials'].items():ck('Original shader '+n,n in bpy.data.materials and q._material(bpy.data.materials[n])['hash']==r['hash'])
for n,r in base['images'].items():ck('Packed reference/image '+n,n in bpy.data.images and q._image(bpy.data.images[n])==r)
for n,h in base['actions'].items():ck('Original animation '+n,n in bpy.data.actions and q._action(bpy.data.actions[n])==h)
allowed=set(contact['restored_for_new_roof'])|{n for n in base['objects']if n.startswith('V24_XIESHAN_')}|{'V24_03_Kitchen_Rear_Gable_Wall','V24_03_Kitchen_Rear_Stone_Plinth','V24_03_Kitchen_Rear_Corner_Downpipe','V24_03_Kitchen_Rear_Drain_Elbow'}
ck('Changes limited to roof, adjoining contacts and rear closure',set(delta['changed_objects'])<=allowed,unexpected=sorted(set(delta['changed_objects'])-allowed))
ck('No original scene objects lost',not delta['removed_objects'],removed=delta['removed_objects'])
for n,r in base['objects'].items():
 ob=bpy.data.objects.get(n);ck('Object retained '+n,ob is not None)
 if ob is None:continue
 ck('Parent/animation retained '+n,(ob.parent.name if ob.parent else None)==r['parent']and q._animation(ob)==r['animation'])
 if n not in ['V24_03_Kitchen_Rear_Corner_Downpipe','V24_03_Kitchen_Rear_Drain_Elbow']:ck('Original transform '+n,q._matrix(ob.matrix_world)==r['matrix'])
 if n not in allowed and r['mesh_hash']:ck('Unchanged geometry/UV '+n,q._mesh_hash(ob.data)==r['mesh_hash'])
for n,h in delta['expected_mesh_hashes'].items():ck('Exact saved geometry '+n,q._mesh_hash(bpy.data.objects[n].data)==h)
for n in [n for n in delta['expected_mesh_hashes']if n.startswith('V24_XIESHAN_')]+['V24_03_Kitchen_Rear_Gable_Wall','V24_03_Kitchen_Rear_Stone_Plinth']:
 ob=bpy.data.objects[n];s=q._stats(ob.data);ck('Independent closed positive solids '+n,s['closed']and s['signed_volume_m3']>0,**s)
for n in contact['restored_for_new_roof']:
 s=_closed_stats(bpy.data.objects[n]);ck('No open contact cut '+n,s['boundary_edges']==0,**s)
for f,poses in base['door_poses'].items():
 sc.frame_set(int(f));bpy.context.view_layer.update()
 for n,mat in poses.items():ck('Unchanged door pose '+n+' '+f,q._matrix(bpy.data.objects[n].matrix_world)==mat)
sc.frame_set(40);bpy.context.view_layer.update()
ck('26 moving doors retained',len(base['doors'])==26)
ck('15 relief fields retained',len([o for o in bpy.data.objects if o.name.startswith('V24_Gate_Reference_Relief_')])==15)
ck('Real materials enabled',all(v.material_override is None for v in sc.view_layers))
core=_tree(bpy.data.objects['V24_XIESHAN_09_Continuous_Eave_Bearing_Core']);bands=_tree(bpy.data.objects['V24_XIESHAN_08_Five_Continuous_Stepped_Eave_Bands'])
for k,(a,b)in enumerate([(2.655,2.695),(2.695,2.736),(2.736,2.770),(2.770,2.815),(2.815,2.865)]):
 p=Vector((CX,CY-2,fitted_bearing_z((a+b)/2)));one=bands.ray_cast(p,Vector((0,1,0)),5);two=core.ray_cast(p,Vector((0,1,0)),5)
 ck('Exposed eave tier '+str(k+1),one[0]is not None and two[0]is not None and two[3]-one[3]>.025)
wall=bpy.data.objects['V24_03_Kitchen_Rear_Gable_Wall'];tree=_tree(wall);miss=[]
for row in contact['roof_top_fit']:
 x,y,top=row['x'],row['y'],row['wall_top_z']
 if x<7.71 or x>14.09:continue
 for z in [-.3,.2,1.,2.,top-.04]:
  hit=tree.ray_cast(Vector((x,y+1,z)),Vector((0,-1,0)),2)
  if hit[0]is None:miss.append([x,y,z])
ck('Whole rear and end return opaque from plinth to roof',not miss,missing_rays=miss)
ck('Wall top fitted to existing roof underside',contact['all_roof_top_samples_hit'],missing=[r for r in contact['roof_top_fit']if not r['roof_hit']])
perim=_tree(bpy.data.objects['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry']);end=_tree(bpy.data.objects[contact['upper_return']['object']]);ov=end.overlap(perim);ck('Upper return meets actual full-height perimeter wall',bool(ov),triangle_pairs=len(ov));ov2=end.overlap(tree);ck('Upper return meets kitchen rear wall',bool(ov2),triangle_pairs=len(ov2))
for n in delta['added_objects']:
 if n not in bpy.data.objects or bpy.data.objects[n].type!='MESH':continue
 s=q._stats(bpy.data.objects[n].data);ck('Closed new return solid '+n,s['closed']and s['signed_volume_m3']>0,**s)
# Reproduce rays through the exact opening visible in the original review view.
cam=bpy.data.objects.new('QA_Opening_Camera',bpy.data.cameras.new('QA_Opening_Camera'));sc.collection.objects.link(cam);cam.location=(4.2,-.6,2.1);cam.rotation_euler=(Vector((9.6,-2.8,1.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=28;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();proj=cam.calc_matrix_camera(dg,x=1200,y=900);inv=(proj@cam.matrix_world.inverted()).inverted()
visible=[]
for px,py in [(390,450),(400,450),(410,450),(420,450),(390,500),(400,500),(410,500),(420,500),(390,560),(410,560),(420,560)]:
 p=inv@Vector((px/600-1,1-py/450,1,1));p=Vector(p[:3])/p.w;hit,loc,normal,index,obj,mat=sc.ray_cast(dg,cam.location,(p-cam.location).normalized());name=obj.name if obj else'';visible.append({'pixel':[px,py],'hit':name});ck('Former visible opening blocked '+str([px,py]),hit and(name.startswith('V24_04_Kitchen_Perimeter_')or name=='V24_03_Kitchen_Rear_Gable_Wall'or name.startswith('SITE_PERIMETER_')or name.startswith('SITE_V15_PERIMETER_')),hit=name)
bpy.data.objects.remove(cam,do_unlink=True)
# Recheck all actual gate/kitchen crossings after a fresh file load.
rr=[(o,_bounds(o),_tree(o))for o in bpy.data.objects if o.type=='MESH'and o.name.startswith('V24_XIESHAN_')];coll=[]
for n in contact['restored_for_new_roof']:
 ob=bpy.data.objects[n];lo,hi=_bounds(ob);tr=_tree(ob)
 for ro,bb,rt in rr:
  if any(hi[i]<bb[0][i]or lo[i]>bb[1][i]for i in range(3)):continue
  ov=tr.overlap(rt)
  if ov:coll.append({'kitchen':n,'roof':ro.name,'triangles':len(ov)})
ck('No kitchen/gate roof triangle crossings',not coll,collisions=coll)
h=sha(P);ck('Saved model digest matches build',h==build['sha256'])
fail=[x for x in checks if not x['pass']];report={'status':'PASS_V24_04_FRESH_BLEND_QA'if not fail else'FAIL_V24_04_FRESH_BLEND_QA','model_sha256':h,'checks':checks,'failures':fail,'retained_original_materials':len(base['materials']),'retained_packed_images':len(base['images']),'door_roots':len(base['doors'])};write('V24_04_Fresh_Blend_QA.json',report);print(report['status'],len(checks),len(fail),flush=True)
if fail:raise AssertionError(json.dumps(fail[:12],ensure_ascii=False))
