import bpy,json,math
from pathlib import Path
from mathutils import Vector
import numpy as np
B=Path(r'E:/jz/JIA/Rebuild_V19');O=Path(r'E:/jz/JIA/Rebuild_V20');bpy.ops.wm.open_mainfile(filepath=str(B/'05_Export/Actual_Rhino_V19_Readback_LOCAL.blend'));sc=bpy.context.scene
I=json.loads((O/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'));M=json.loads((O/'02_Data/Native_Render_Materials.json').read_text(encoding='utf8'));AQ=json.loads((O/'06_Report/V20_Assembly_QA.json').read_text(encoding='utf8'));changed=set(AQ['changed_nodes']);col=bpy.data.collections['ACTUAL_RHINO_V19_READBACK'];col.name='ACTUAL_RHINO_V20_READBACK'
for n in AQ['removed_nodes']:
 par=bpy.data.objects.get(n)
 if par:
  for child in list(par.children):
   me=child.data if child.type=='MESH' else None;bpy.data.objects.remove(child,do_unlink=True)
   if me and not me.users:bpy.data.meshes.remove(me)
  bpy.data.objects.remove(par,do_unlink=True)
for im in bpy.data.images:
 if im.source=='FILE':
  p=im.filepath.replace('Rebuild_V19','Rebuild_V20')
  if Path(p).exists():im.filepath=p
for name,md in M.items():
 if not name.startswith('M_V20_'):continue
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=tuple((c/255)**2.2 for c in md['color'])+(1,);bs.inputs['Roughness'].default_value=md['roughness'];bs.inputs['Metallic'].default_value=md['metallic']
 if md['alpha']<1:bs.inputs['Transmission Weight'].default_value=1-md['alpha']
 if md.get('native_bitmap'):
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(md['native_bitmap'],check_existing=True);tx.extension='REPEAT';m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
 if md.get('native_bump'):
  bt=m.node_tree.nodes.new('ShaderNodeTexImage');bt.image=bpy.data.images.load(md['native_bump'],check_existing=True);bt.image.colorspace_settings.name='Non-Color';bn=m.node_tree.nodes.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.18;bn.inputs['Distance'].default_value=md.get('bump_distance_m',.003);m.node_tree.links.new(bt.outputs['Color'],bn.inputs['Height']);m.node_tree.links.new(bn.outputs['Normal'],bs.inputs['Normal'])
 m['Appearance_Source']='V20 actual native 3DM bitmap material and readback UV'
for r in I:
 n=r['name']
 if n not in changed:continue
 d=np.load(O/'02_Data'/r['file']);old=bpy.data.objects.get(n+'_Geometry')
 if old:
  oldme=old.data;par=old.parent;bpy.data.objects.remove(old,do_unlink=True)
  if not oldme.users:bpy.data.meshes.remove(oldme)
 else:par=bpy.data.objects.new(n,None);col.objects.link(par)
 me=bpy.data.meshes.new(n);v=d['vertices'];f=d['faces'];uv=d['uv'];me.from_pydata(v.tolist(),[],f.tolist());me.update();ob=bpy.data.objects.new(n+'_Geometry',me);col.objects.link(ob);ob.parent=par
 for mat in r['materials']:me.materials.append(bpy.data.materials[mat])
 me.polygons.foreach_set('material_index',d['material_ids']);u=me.uv_layers.new(name='Native_Review_UV');u.data.foreach_set('uv',uv[f.ravel()].astype(np.float32).ravel());par['Parameters']=json.dumps(r['element'],ensure_ascii=False);par['GeometrySource']='Saved V20 native 3DM mesh and UV';ob['Original_Rhino_Objects']=r['native_objects'];print('REFRESHED V20',n,len(f),flush=True)
for ob in bpy.data.objects:
 if ob.type=='CAMERA' and ob.name.startswith('V19_'):ob.name=ob.name.replace('V19_','V20_')
newviews=AQ['cameras']
for name,pos,tar,fov in newviews:
 cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cd.angle=math.radians(fov)

# Each leaf has a genuine pivot transform, an inward animation and a default open pose.
DM=json.loads((O/'02_Data/Door_Manifest_V20.json').read_text(encoding='utf8'))
for row in DM['doors']:
    n=row['name'];par=bpy.data.objects[n];ob=bpy.data.objects[n+'_Geometry'];pivot=Vector(row['hinge_local_m'])
    par.location=(0,0,0);par.rotation_euler=(0,0,0);par.scale=(1,1,1)
    for v in ob.data.vertices:v.co-=pivot
    par.location=pivot
    for k,v in row.items():par[k]=json.dumps(v) if isinstance(v,(dict,list)) or v is None else v
    par['UE_Interaction']='HINGED_INWARD';par['DefaultPose']='OPEN_INWARD';par['HingeCoordinateSystem']='LOCAL metres'
bpy.context.view_layer.update()
for row in DM['doors']:
    if row.get('parent_door_id'):
        ob=bpy.data.objects[row['name']];world=ob.matrix_world.copy();ob.parent=bpy.data.objects[row['parent_door_id']];ob.matrix_world=world
bpy.context.view_layer.update()
for row in DM['doors']:
    if row.get('parent_door_id'):continue
    par=bpy.data.objects[row['name']];deg=row['open_angle_deg'];par.rotation_mode='XYZ';par.rotation_euler.z=-math.radians(deg);par.keyframe_insert(data_path='rotation_euler',frame=1,index=2);par.rotation_euler.z=0;par.keyframe_insert(data_path='rotation_euler',frame=40,index=2)
    act=par.animation_data.action;act.name='Inward_'+row['name'];track=par.animation_data.nla_tracks.new();track.name=act.name;strip=track.strips.new(act.name,1,act);par.animation_data.action=None
sc.frame_end=40;sc.frame_set(40)

sc.render.engine='CYCLES';sc.cycles.samples=20;sc.cycles.use_denoising=True;sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.camera=bpy.data.objects[newviews[0][0]]
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V20_Readback_LOCAL.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
 if ob.type in ['MESH','EMPTY','CAMERA']:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'05_Export/Complete_Site_V20_LOCAL.glb'),use_selection=True,export_format='GLB',export_cameras=True,export_extras=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_current_frame=True)
names=[r[0] for r in newviews]+['V20_Native_Whole_Site','V20_Native_Top']
for name in names:
 sc.camera=bpy.data.objects[name];sc.render.filepath=str(O/'06_Report'/f'{name}.png');bpy.ops.render.render(write_still=True);print('RENDERED V20',name,flush=True)
(O/'06_Report/Preview_View_States.json').write_text(json.dumps({'geometry':'Saved V20 3DM actual mesh readback','view_names':names,'camera_count':len([ob for ob in sc.objects if ob.type=='CAMERA']),'visibility':'All native indexed geometry visible; inherited inspection lighting','source_coordinate_system':'LOCAL metres'},ensure_ascii=False,indent=2),encoding='utf8');print('V20 EXPORT AND RENDERS COMPLETE',flush=True)
