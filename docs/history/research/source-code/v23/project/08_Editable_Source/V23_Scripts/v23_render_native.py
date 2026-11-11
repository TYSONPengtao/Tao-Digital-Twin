"""Rebuild every visible node from the newly saved V22 native readback."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
import numpy as np
B=Path('E:/jz/JIA/Rebuild_V22');O=Path('E:/jz/JIA/Rebuild_V23')
bpy.ops.wm.open_mainfile(filepath=str(B/'05_Export/Actual_Rhino_V22_Readback_LOCAL.blend'))
sc=bpy.context.scene
for ob in bpy.data.objects:
 if ob.type=='LIGHT':ob.visible_camera=False;ob.visible_glossy=False;ob.visible_transmission=False
I=json.loads((O/'02_Data/Native_Readback_Index_V23.json').read_text(encoding='utf8'))
M=json.loads((O/'02_Data/Native_Render_Materials.json').read_text(encoding='utf8'))
AQ=json.loads((O/'06_Report/V23_Assembly_QA.json').read_text(encoding='utf8'))
col=bpy.data.collections['ACTUAL_RHINO_V22_READBACK'];col.name='ACTUAL_RHINO_V23_READBACK'
for ob in list(col.objects):
 if ob.type in ['MESH','EMPTY']:
  me=ob.data if ob.type=='MESH' else None
  bpy.data.objects.remove(ob,do_unlink=True)
  if me and not me.users:bpy.data.meshes.remove(me)
for act in list(bpy.data.actions):
 if act.users==0:bpy.data.actions.remove(act)
for im in bpy.data.images:
 if im.source=='FILE':
  p=im.filepath.replace('Rebuild_V22','Rebuild_V23')
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
 m['Appearance_Source']='V22 native material and actual readback UV'
for j,r in enumerate(I):
 n=r['name'];d=np.load(O/'02_Data'/r['file']);v=d['vertices'];f=d['faces'];uv=d['uv']
 par=bpy.data.objects.new(n,None);col.objects.link(par)
 me=bpy.data.meshes.new(n);me.from_pydata(v.tolist(),[],f.tolist());me.update()
 ob=bpy.data.objects.new(n+'_Geometry',me);col.objects.link(ob);ob.parent=par
 for mat in r['materials']:me.materials.append(bpy.data.materials[mat])
 me.polygons.foreach_set('material_index',d['material_ids'])
 u=me.uv_layers.new(name='Native_Review_UV');u.data.foreach_set('uv',uv[f.ravel()].astype(np.float32).ravel())
 par['Parameters']=json.dumps(r['element'],ensure_ascii=False);par['GeometrySource']='Saved V23 native 3DM readback'
 ob['Original_Rhino_Objects']=r['native_objects']
 if j%70==0:print('READBACK MESH',j,len(I),flush=True)
for ob in bpy.data.objects:
 if ob.type=='CAMERA' and ob.name.startswith('V22_'):ob.name=ob.name.replace('V22_','V23_')
for name,pos,tar,fov in AQ['cameras']:
 cam=bpy.data.objects.get(name)
 if not cam:
  cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);sc.collection.objects.link(cam)
 cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.data.angle=math.radians(fov)
DM=json.loads((O/'02_Data/Door_Manifest_V23.json').read_text(encoding='utf8'))
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
bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V23_Readback_LOCAL.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
 if ob.type in ['MESH','EMPTY','CAMERA']:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'05_Export/Complete_Site_V23_LOCAL.glb'),use_selection=True,export_format='GLB',export_cameras=True,export_extras=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_current_frame=True)
names=[r[0] for r in AQ['cameras']]+['V23_Native_Whole_Site']
clay=bpy.data.materials.new('V23_Comparison_Clay');clay.use_nodes=True
bs=next(n for n in clay.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.62,.65,.67,1);bs.inputs['Roughness'].default_value=.78
clayglass=clay.copy();clayglass.name='V23_Comparison_Clear_Glass'
bs=next(n for n in clayglass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Transmission Weight'].default_value=.94;bs.inputs['Roughness'].default_value=.10;bs.inputs['IOR'].default_value=1.45
groutclay=clay.copy();groutclay.name='V23_Comparison_Joint';bs=next(n for n in groutclay.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.28,.30,.30,1)
originals=[(o,list(o.data.materials)) for o in col.objects if o.type=='MESH']
preview_frames={}
for n in names:
 frame=20 if n in ['V23_Inner_Gate_Ideal_Compare','V23_Gate_Hardware'] else 40
 sc.frame_set(frame);preview_frames[n]=frame
 comparison='Native_' not in n
 for ob,mats in originals:
  for j,m in enumerate(mats):
   ob.data.materials[j]=(clayglass if ('glass' in m.name.lower() or 'glazing' in m.name.lower()) else groutclay if 'Filled_Joint' in m.name else clay) if comparison else m
 sc.camera=bpy.data.objects[n];sc.render.filepath=str(O/'06_Report'/f'{n}.png');bpy.ops.render.render(write_still=True);print('RENDERED',n,flush=True)
for ob,mats in originals:
 for j,m in enumerate(mats):ob.data.materials[j]=m
sc.frame_set(20);sc.camera=bpy.data.objects['V23_Inner_Gate_Ideal_Compare'];sc.render.filepath=str(O/'06_Report/V23_Inner_Gate_Materials.png');bpy.ops.render.render(write_still=True)
sc.frame_set(40)
native_hash=hashlib.file_digest((O/'04_Rhino/Architecture_Complete_V23_COMPACT_ENU.3dm').open('rb'),'sha256').hexdigest()
(O/'06_Report/Preview_View_States.json').write_text(json.dumps({'geometry':'Saved V23 3DM actual mesh readback','native_model_sha256':native_hash,'view_names':names,'camera_count':len([o for o in sc.objects if o.type=='CAMERA']),'visibility':'All native indexed geometry visible; interior inspection lights retained','source_coordinate_system':'LOCAL metres','comparison_material':'Clay inspection materials; native and GLB retain real materials','preview_animation_frames':preview_frames,'additional_material_preview':{'file':'V23_Inner_Gate_Materials.png','camera':'V23_Inner_Gate_Ideal_Compare','frame':20},'pose_note':'Gate ideal comparison uses partial inward animation pose to expose leaf details; native/GLB default is fully open at frame40'},ensure_ascii=False,indent=2),encoding='utf8')
print('V22 READBACK EXPORT AND PREVIEWS COMPLETE',flush=True)
