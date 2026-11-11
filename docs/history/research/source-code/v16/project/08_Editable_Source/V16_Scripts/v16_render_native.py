import bpy,json,math
from pathlib import Path
from mathutils import Vector
import numpy as np
O=Path(r'E:/jz/JIA/Rebuild_V16');I=json.loads((O/'02_Data/Native_Readback_Index_V16.json').read_text(encoding='utf8'));M=json.loads((O/'02_Data/Native_Render_Materials.json').read_text(encoding='utf8'))
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
col=bpy.data.collections.new('ACTUAL_RHINO_V16_READBACK');sc.collection.children.link(col)
def linear(x):
 x=x/255;return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
mats={}
for key,v in M.items():
 m=bpy.data.materials.new(key);m.use_nodes=True;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*[linear(c) for c in v['color']],1);bs.inputs['Roughness'].default_value=v.get('roughness',.6);bs.inputs['Metallic'].default_value=v.get('metallic',0)
 if v.get('alpha',1)<1:
  sock=bs.inputs.get('Transmission Weight') or bs.inputs.get('Transmission')
  if sock:sock.default_value=.75
  bs.inputs['IOR'].default_value=v.get('ior',1.52)
 if v.get('native_bitmap'):
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(v['native_bitmap'],check_existing=True);m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
 if v.get('native_bump'):
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(v['native_bump'],check_existing=True);tx.image.colorspace_settings.name='Non-Color';bn=m.node_tree.nodes.new('ShaderNodeBump');bn.inputs['Strength'].default_value=.20;bn.inputs['Distance'].default_value=.004;m.node_tree.links.new(tx.outputs['Color'],bn.inputs['Height']);m.node_tree.links.new(bn.outputs['Normal'],bs.inputs['Normal'])
 m.diffuse_color=(*[linear(c) for c in v['color']],1);m['Appearance_Source']='Actual native named material bitmap and corrected mesh UV; original exterior bitmap and UV preserved';mats[key]=m
for row in I:
 d=np.load(O/'02_Data'/row['file']);e=row['element'];v=d['vertices'];f=d['faces'];uv=d['uv'];mid=d['material_ids'];group=bpy.data.objects.new(row['name'],None);col.objects.link(group)
 if e.get('definition') or (e.get('role')=='LEAF' and e.get('door_id')):
  pivot=e.get('hinge_origin_local_m',e.get('origin',[0,0,0])) if e.get('role')=='LEAF' else e.get('origin',[0,0,0]);a=e.get('angle',0);c=math.cos(a);s=math.sin(a);inv=np.array([[c,s,0],[-s,c,0],[0,0,1]]);v=(v-np.array(pivot))@inv.T;group.location=pivot;group.rotation_euler[2]=a;group['Pivot_LOCAL_m']=list(pivot)
 for key in ['door_id','role','parent_door_id','assembly_id','source','confidence','layer','family']:group[key]=str(e.get(key,''))
 group['Parameters']=json.dumps(e,ensure_ascii=False);group['GeometrySource']='Fresh V16 native Mesh readback; unchanged Brep/block geometry verified against V15 by full native hash'
 triangle_uv=uv[f.ravel()];me=bpy.data.meshes.new(row['name']);me.from_pydata(v.tolist(),[],f.tolist());me.update();ob=bpy.data.objects.new(row['name']+'_Geometry',me);col.objects.link(ob);ob.parent=group
 for key in row['materials']:me.materials.append(mats[key])
 me.polygons.foreach_set('material_index',mid.astype(np.int32));u=me.uv_layers.new(name='Native_Review_UV');u.data.foreach_set('uv',triangle_uv.astype(np.float32).ravel());ob['Original_Rhino_Objects']=row['native_objects']
 if row['name'].startswith(('SITE_V12_REBUILT_EARTH','SITE_V16_GRADED_INTERIOR_SOIL','SITE_V12_REBUILT_ROAD','SITE_V14_ORIGINAL_EXTERIOR')):
  for p in me.polygons:p.use_smooth=p.normal.z>.35
  if 'normals' in d.files:me.normals_split_custom_set(d['normals'][f.ravel()].tolist());me.update()
sc.world=bpy.data.worlds.new('Native_Review_World');sc.world.use_nodes=True;bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.7,.73,.78,1);bg.inputs['Strength'].default_value=.75
ld=bpy.data.lights.new('Native_Review_Sun','SUN');ld.energy=2.2;ld.angle=.12;lo=bpy.data.objects.new('Native_Review_Sun',ld);sc.collection.objects.link(lo);lo.rotation_euler=[math.radians(28),math.radians(-22),math.radians(-35)]
cameras=[('V16_Native_Whole_Site', [50, -66, 42], [-3, -4, 2], 49, None), ('V16_Native_Top', [-1, -3, 75], [-1, -3, 0], 50, 64), ('V16_Native_Graded_Courtyard', [-22, -5, 3.8], [-6, 1, -0.48], 74, None), ('V16_Native_Screenwall_Inside', [10.5, -14.8, 1.0], [3, -16.35, -0.05], 74, None), ('V16_Native_West_Wall_Drain', [-19.3, -9.3, 0.3], [-21.6, -4.2, -0.85], 71, None), ('V16_Native_South_Wall_Drain', [-3.8, -19.2, -0.6], [6, -17.2, -2.1], 73, None), ('V16_Native_Outer_Storage_Base', [24.5, -18.8, -1.5], [20.2, -15.5, -2.35], 65, None), ('V16_Native_Entry_Route', [-10, -11.22, 1.3], [6.6, -11.95, 1.0], 63, None)]
for name,pos,tar,fov,ortho in cameras:
 cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cd.angle=math.radians(fov)
 if ortho:cd.type='ORTHO';cd.ortho_scale=ortho
sc.render.engine='CYCLES';sc.cycles.samples=16;sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.view_settings.view_transform='Standard';sc.render.image_settings.file_format='PNG';sc.camera=bpy.data.objects[cameras[0][0]];bpy.context.view_layer.update()
for img in bpy.data.images:
 if img.source=='FILE':img.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V16_Readback_LOCAL.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
 if ob.type in ['MESH','EMPTY','CAMERA']:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'05_Export/Complete_Site_V16_LOCAL.glb'),use_selection=True,export_format='GLB',export_cameras=True,export_extras=True)
for i,p in enumerate([[5.4,6.80,9.4],[7.7,6.82,9.4],[2.4,6.8,9.4],[10.6,3.4,9.8],[10.2,7.9,9.6]]):
 ld=bpy.data.lights.new('Hall_Review_Light_'+str(i),'POINT');ld.energy=140;ld.shadow_soft_size=.45;lo=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(lo);lo.location=p;lo['Role']='Inspection light, not modeled as surveyed fixture'
for name,_,_,_,_ in cameras:
 for did in ['DOOR_LAUNDRY_F3__LEAF_Geometry','DOOR_STUDY_F3__LEAF_Geometry']:bpy.data.objects[did].hide_render=('F3_' in name)
 sc.camera=bpy.data.objects[name];sc.view_settings.exposure=-.25 if 'F3_' in name else 0;sc.render.filepath=str(O/'06_Report'/f'{name}.png');bpy.ops.render.render(write_still=True);print('RENDERED ACTUAL 3DM',name,flush=True)
(O/'06_Report/Preview_View_States.json').write_text(json.dumps({'geometry':'Native 3DM verified readback','F3_hall_views':'Two closed door leaves temporarily hidden for clear-opening and floor continuity inspection; native 3DM and GLB retain their closed leaves and hinge data. Inspection point lights used for visibility.','other_views':'All indexed native geometry visible'},ensure_ascii=False,indent=2),encoding='utf8')
print('V16 actual native geometry review images complete',flush=True)
