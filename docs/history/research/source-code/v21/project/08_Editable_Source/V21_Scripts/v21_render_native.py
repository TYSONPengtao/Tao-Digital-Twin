"""Rebuild every visible node from the newly saved V21 native readback."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
import numpy as np
B=Path('E:/jz/JIA/Rebuild_V20');O=Path('E:/jz/JIA/Rebuild_V21')
bpy.ops.wm.open_mainfile(filepath=str(B/'05_Export/Actual_Rhino_V20_Readback_LOCAL.blend'))
sc=bpy.context.scene
inspection_rows=[('F3_Landing',[7.1,8.3,9.75],130),('F3_Terrace',[2,6,9.4],130)]
for name,pos,power in inspection_rows:
 key='V21_INSPECTION_'+name;ld=bpy.data.lights.new(key,'POINT');ld.energy=power;ld.shadow_soft_size=1.1
 ob=bpy.data.objects.new(key,ld);sc.collection.objects.link(ob);ob.location=pos
 ob['Purpose']='Review illumination only, not a surveyed fixture'
for ob in bpy.data.objects:
 if ob.type=='LIGHT':ob.visible_camera=False;ob.visible_glossy=False;ob.visible_transmission=False
for name,power in [('V20_INSPECTION_F1_Hall',100),('V20_INSPECTION_F1_Rear',60)]:
 bpy.data.objects[name].data.energy=power
(O/'06_Report/Interior_Inspection_Lighting.json').write_text(json.dumps({'new_point_lights':inspection_rows,'radius_m':1.1,'light_emitter_visibility':'Camera/glossy/transmission disabled; diffuse and shadow retained','geometry_visibility':'All native model geometry visible','purpose':'Inspection only, not modeled as-built fixtures'},indent=2),encoding='utf8')
I=json.loads((O/'02_Data/Native_Readback_Index_V21.json').read_text(encoding='utf8'))
M=json.loads((O/'02_Data/Native_Render_Materials.json').read_text(encoding='utf8'))
AQ=json.loads((O/'06_Report/V21_Assembly_QA.json').read_text(encoding='utf8'))
col=bpy.data.collections['ACTUAL_RHINO_V20_READBACK'];col.name='ACTUAL_RHINO_V21_READBACK'
for ob in list(col.objects):
 if ob.type in ['MESH','EMPTY']:
  me=ob.data if ob.type=='MESH' else None
  bpy.data.objects.remove(ob,do_unlink=True)
  if me and not me.users:bpy.data.meshes.remove(me)
for act in list(bpy.data.actions):
 if act.users==0:bpy.data.actions.remove(act)
for im in bpy.data.images:
 if im.source=='FILE':
  p=im.filepath.replace('Rebuild_V20','Rebuild_V21')
  if Path(p).exists():im.filepath=p
for name,md in M.items():
 if bpy.data.materials.get(name):continue
 m=bpy.data.materials.new(name);m.use_nodes=True
 bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 bs.inputs['Base Color'].default_value=tuple((c/255)**2.2 for c in md['color'])+(1,)
 bs.inputs['Roughness'].default_value=md['roughness'];bs.inputs['Metallic'].default_value=md['metallic']
 if md['alpha']<1:bs.inputs['Transmission Weight'].default_value=1-md['alpha']
 if md.get('native_bitmap'):
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(md['native_bitmap'],check_existing=True)
  tx.extension='REPEAT';m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
 if md.get('native_bump'):
  bt=m.node_tree.nodes.new('ShaderNodeTexImage');bt.image=bpy.data.images.load(md['native_bump'],check_existing=True)
  bt.image.colorspace_settings.name='Non-Color';bn=m.node_tree.nodes.new('ShaderNodeBump')
  bn.inputs['Strength'].default_value=.18;bn.inputs['Distance'].default_value=md.get('bump_distance_m',.003)
  m.node_tree.links.new(bt.outputs['Color'],bn.inputs['Height']);m.node_tree.links.new(bn.outputs['Normal'],bs.inputs['Normal'])
 m['Appearance_Source']='V21 native material and actual readback UV'
for j,r in enumerate(I):
 n=r['name'];d=np.load(O/'02_Data'/r['file']);v=d['vertices'];f=d['faces'];uv=d['uv']
 par=bpy.data.objects.new(n,None);col.objects.link(par)
 me=bpy.data.meshes.new(n);me.from_pydata(v.tolist(),[],f.tolist());me.update()
 ob=bpy.data.objects.new(n+'_Geometry',me);col.objects.link(ob);ob.parent=par
 for mat in r['materials']:me.materials.append(bpy.data.materials[mat])
 me.polygons.foreach_set('material_index',d['material_ids'])
 u=me.uv_layers.new(name='Native_Review_UV');u.data.foreach_set('uv',uv[f.ravel()].astype(np.float32).ravel())
 par['Parameters']=json.dumps(r['element'],ensure_ascii=False);par['GeometrySource']='Saved V21 native 3DM readback'
 ob['Original_Rhino_Objects']=r['native_objects']
 if j%70==0:print('READBACK MESH',j,len(I),flush=True)
for ob in bpy.data.objects:
 if ob.type=='CAMERA' and ob.name.startswith('V20_'):ob.name=ob.name.replace('V20_','V21_')
for name,pos,tar,fov in AQ['cameras']:
 cam=bpy.data.objects.get(name)
 if not cam:
  cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);sc.collection.objects.link(cam)
 cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.data.angle=math.radians(fov)
DM=json.loads((O/'02_Data/Door_Manifest_V21.json').read_text(encoding='utf8'))
for r in DM['doors']:
 par=bpy.data.objects[r['name']];ob=bpy.data.objects[r['name']+'_Geometry'];pivot=Vector(r['hinge_local_m'])
 for v in ob.data.vertices:v.co-=pivot
 par.location=pivot
 for k,v in r.items():par[k]=json.dumps(v) if isinstance(v,(dict,list)) or v is None else v
 par['UE_Interaction']=r.get('operation','HINGED_INWARD');par['DefaultPose']='OPEN'
 par['HingeCoordinateSystem']='LOCAL metres'
bpy.context.view_layer.update()
for r in DM['doors']:
 if r.get('parent_door_id'):
  par=bpy.data.objects[r['name']];wm=par.matrix_world.copy();par.parent=bpy.data.objects[r['parent_door_id']];par.matrix_world=wm
bpy.context.view_layer.update()
for r in DM['doors']:
 if r.get('parent_door_id'):continue
 par=bpy.data.objects[r['name']]
 if r.get('operation')=='SLIDING':
  po=par.location.copy();delta=Vector(r['open_translation_m'])
  par.location=po-delta;par.keyframe_insert(data_path='location',frame=1)
  par.location=po;par.keyframe_insert(data_path='location',frame=40);prefix='Slide_'
 else:
  par.rotation_mode='XYZ';par.rotation_euler.z=-math.radians(r['open_angle_deg'])
  par.keyframe_insert(data_path='rotation_euler',frame=1,index=2);par.rotation_euler.z=0
  par.keyframe_insert(data_path='rotation_euler',frame=40,index=2);prefix='Inward_'
 act=par.animation_data.action;act.name=prefix+r['name'];track=par.animation_data.nla_tracks.new();track.name=act.name
 track.strips.new(act.name,1,act);par.animation_data.action=None
sc.frame_end=40;sc.frame_set(40)
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True
sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V21_Readback_LOCAL.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
 if ob.type in ['MESH','EMPTY','CAMERA']:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'05_Export/Complete_Site_V21_LOCAL.glb'),use_selection=True,export_format='GLB',export_cameras=True,export_extras=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_current_frame=True)
names=[r[0] for r in AQ['cameras']]+['V21_Native_Whole_Site','V21_Native_Top']
for n in names:
 sc.camera=bpy.data.objects[n];sc.render.filepath=str(O/'06_Report'/f'{n}.png');bpy.ops.render.render(write_still=True);print('RENDERED',n,flush=True)
native_hash=hashlib.file_digest((O/'04_Rhino/Architecture_Complete_V21_ALIGNED_ENU.3dm').open('rb'),'sha256').hexdigest()
(O/'06_Report/Preview_View_States.json').write_text(json.dumps({'geometry':'Saved V21 3DM actual mesh readback','native_model_sha256':native_hash,'view_names':names,'camera_count':len([o for o in sc.objects if o.type=='CAMERA']),'visibility':'All native indexed geometry visible; interior inspection lights retained','source_coordinate_system':'LOCAL metres'},ensure_ascii=False,indent=2),encoding='utf8')
print('V21 READBACK EXPORT AND PREVIEWS COMPLETE',flush=True)
