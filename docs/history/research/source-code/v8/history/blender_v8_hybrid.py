import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');B=json.loads((O/'02_Data/Base_Index.json').read_text(encoding='utf-8'));I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));M=json.loads((O/'02_Data/Materials.json').read_text(encoding='utf-8'));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf-8'));a=math.radians(C['rotation_deg']);c=math.cos(a);s=math.sin(a);R=np.array([[c,-s,0],[s,c,0],[0,0,1]]);origin=np.array(C['origin'])
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
basecol=bpy.data.collections.new('BASE_REALITY_UNCHANGED');sc.collection.children.link(basecol);patchcol=bpy.data.collections.new('PATCH_ONLY_MISSING_AREA');sc.collection.children.link(patchcol)
def photo(name,path):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();tx=n.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(path),check_existing=True);tx.image.pack();bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=1;bs.inputs['Specular IOR Level'].default_value=0;bs.inputs['Emission Strength'].default_value=0;out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color']);m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Emission Color']);m.node_tree.links.new(bs.outputs[0],out.inputs[0]);m['ImageRole']='Original measured photo, unchanged pixels; standard exchange shader';return m
def linear(x):
 x=x/255;return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
mats={}
for k,v in M.items():
 if v.get('texture'):mats[k]=photo(k,v['texture']);continue
 m=bpy.data.materials.new(k);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*[linear(x) for x in v['color']],1);bs.inputs['Roughness'].default_value=v['roughness'];bs.inputs['Metallic'].default_value=v.get('metallic',0)
 if v.get('alpha',1)<1:bs.inputs['Transmission Weight'].default_value=.85;bs.inputs['IOR'].default_value=v.get('ior',1.52)
 mats[k]=m
def meshob(name,verts,faces,uv,materials,mid,col):
 me=bpy.data.meshes.new(name);me.from_pydata(verts.tolist(),[],faces.tolist());me.update();ob=bpy.data.objects.new(name,me);col.objects.link(ob)
 for m in materials:me.materials.append(m)
 if mid is not None:me.polygons.foreach_set('material_index',mid.astype(np.int32))
 u=me.uv_layers.new(name='Original_Photo_UV');vi=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',vi);u.data.foreach_set('uv',uv[vi].astype(np.float32).ravel());return ob
for b in B:
 d=np.load(O/'02_Data'/f'Base_{b["index"]}.npz');v=(d['vertices']-origin)@R;f=d['faces'];faces=[q[:3].tolist() if q[2]==q[3] else q.tolist() for q in f];mat=photo('BASE_'+b['material_name'],b['texture']);me=bpy.data.meshes.new(b['name']);me.from_pydata(v.tolist(),[],faces);me.materials.append(mat);me.update();ob=bpy.data.objects.new(b['name'],me);basecol.objects.link(ob);uv=me.uv_layers.new(name='Original_Photo_UV');vi=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',vi);uv.data.foreach_set('uv',d['uv'][vi].astype(np.float32).ravel())
 for p in me.polygons:p.use_smooth=True
 if hasattr(me,'normals_split_custom_set_from_vertices'):me.normals_split_custom_set_from_vertices((d['normals']@R).tolist())
 ob['Role']='SOURCE_REALITY_AUTHORIZED_LOCAL_DERIVATIVE';ob['Source_Object_ID']=b['source_id'];ob['Source_Vertices']=b['vertices'];ob['Source_Faces']=b['faces'];ob['Coordinate_Transform']='Rigid ENU-to-local; original source preserved; localized V8 terrain/roof contact edits, retained original UV pixels';print('base',b['index'],len(me.polygons),flush=True)
for row in I:
 d=np.load(O/'02_Data'/row['file']);e=row['element'];v=d['vertices'];f=d['faces'];uv=d['uv'];mi=d['material_ids'];group=bpy.data.objects.new(row['name'],None);patchcol.objects.link(group)
 if e.get('definition'):
  angle=e.get('angle',0);cc=math.cos(angle);ss=math.sin(angle);inv=np.array([[cc,ss,0],[-ss,cc,0],[0,0,1]]);v=(v-np.array(e.get('origin',[0,0,0])))@inv.T;group.location=e['origin'];group.rotation_euler[2]=angle
 for k in ['door_id','role','parent_id','source','confidence','layer','family','interaction','swing_status']:group[k]=str(e.get(k,''))
 group['Parameters']=json.dumps(e,ensure_ascii=False);group['PatchRole']=row['role'];ob=meshob(row['name']+'_Geometry',v,f,uv,[mats[m] for m in row['materials']],mi,patchcol);ob.parent=group;ob['Element']=row['name'];ob['Role']=e.get('role','PATCH_SURFACE')
 if e.get('role')=='LEAF':ob['door_id']=e['door_id'];ob['Pivot_Status']='Actual geometry origin at provisional hinge axis'
print('Created hybrid scene',len(B),'base meshes',len(I),'patch nodes',flush=True)
world=bpy.data.worlds.new('Photo_Matched_World');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.77,.82,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65;sc.world=world
sd=bpy.data.lights.new('Sun_For_Rebuilt_Materials','SUN');sd.energy=1.4;sun=bpy.data.objects.new('Sun_For_Rebuilt_Materials',sd);sc.collection.objects.link(sun);sun.rotation_euler=(.45,-.4,-.65)
cameras=[('V8_Whole_Site',[54,-68,56],[0,0,3],54),('V8_West_Terrain_Only',[-8,-5,68],[-8,-2,-.3],53),('V8_Chinese_Eaves',[1,-24,7.2],[7,-13,3.7],65),('V8_Kitchen_Gate_Joint',[3.1,-14.8,8.1],[8.7,-11.7,4.2],63),('V8_Roman_Arch_Contact',[6.5,-8.8,2.8],[6.5,0,2.85],56),('V8_Stair_Right_Wall',[8.6,9.2,1.55],[5.8,9.2,2.15],78),('V8_Wall_Building_Closure',[-4,3.5,3.3],[0,1.6,1.0],55)]
for name,pos,tar,fov in cameras:
 cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cd.angle=math.radians(fov)
sc.camera=bpy.data.objects['V8_Whole_Site'];bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
 if ob.type in ['MESH','EMPTY','CAMERA']:ob.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(O/'05_Export/Reality_Hybrid_V8_LOCAL.fbx'),use_selection=True,global_scale=1,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',object_types={'MESH','EMPTY','CAMERA'},bake_anim=False,use_custom_props=True,path_mode='COPY',embed_textures=True)
bpy.ops.export_scene.gltf(filepath=str(O/'05_Export/Reality_Hybrid_V8_LOCAL.glb'),use_selection=True,export_format='GLB',export_cameras=True,export_extras=True)
bpy.ops.wm.obj_export(filepath=str(O/'05_Export/Reality_Hybrid_V8_LOCAL.obj'),export_selected_objects=True,forward_axis='Y',up_axis='Z',export_triangulated_mesh=False,export_uv=True,export_normals=True,export_materials=True,path_mode='COPY')
sc.render.engine='CYCLES';sc.cycles.samples=16;sc.render.resolution_x=1700;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.view_settings.view_transform='Standard';sc.render.image_settings.file_format='PNG'
preview=bpy.data.lights.new('Interior_QA_Preview_Light','POINT');preview.energy=150;preview.shadow_soft_size=.5;pl=bpy.data.objects.new('Interior_QA_Preview_Light',preview);sc.collection.objects.link(pl);pl.location=[6.4,5.8,6.8]
for name,_,_,_ in cameras:
 sc.camera=bpy.data.objects[name];sc.render.filepath=str(O/'06_Report'/f'{name}.png');bpy.ops.render.render(write_still=True)
sc.camera=bpy.data.objects['V8_Whole_Site'];bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Reality_Hybrid_V8_LOCAL.blend'))
(O/'06_Report/Blender_Hybrid_Export_QA.json').write_text(json.dumps({'base_meshes':len(B),'patch_nodes':len(I),'mesh_objects':sum(o.type=='MESH' for o in sc.objects),'images_packed':len(bpy.data.images),'local_coordinate_origin_ENU':C['origin'],'local_to_ENU_rotation_deg':C['rotation_deg'],'photos':'Original base UV/photo pixels retained, patch uses supported original photo projection or retained modeled material','ue5_project_imported':False},indent=2),encoding='utf-8')
print('V8 corrected hybrid exported and rendered',flush=True)
