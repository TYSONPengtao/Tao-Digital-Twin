import bpy,json,math
from pathlib import Path
from mathutils import Vector
import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V12');I=json.loads((O/'02_Data/Modeled_Index_V12.json').read_text(encoding='utf8'));M=json.loads((O/'02_Data/Materials.json').read_text(encoding='utf8'))
TM=json.loads((O/'03_Textures/Modeled_PBR/Material_Texture_Index.json').read_text(encoding='utf8'))['materials']
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
col=bpy.data.collections.new('V12_ALL_MODELED_ARCHITECTURE_AND_GROUND');sc.collection.children.link(col)
def linear(x):
 x=x/255;return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
mats={}
for k,v in M.items():
 m=bpy.data.materials.new(k);m.use_nodes=True;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*[linear(x) for x in v['color']],1);bs.inputs['Roughness'].default_value=v.get('roughness',.6);bs.inputs['Metallic'].default_value=v.get('metallic',0)
 if v.get('alpha',1)<1:
  socket=bs.inputs.get('Transmission Weight') or bs.inputs.get('Transmission')
  if socket:socket.default_value=.8
  bs.inputs['IOR'].default_value=v.get('ior',1.52)
 if k in TM:
  ti=TM[k];uvn=m.node_tree.nodes.new('ShaderNodeTexCoord');mp=m.node_tree.nodes.new('ShaderNodeMapping');su,sv=ti['physical_tile_m'];mp.inputs['Scale'].default_value=(1/su,1/sv,1);m.node_tree.links.new(uvn.outputs['UV'],mp.inputs['Vector'])
  for key,socket,noncolor in [('base_color','Base Color',False),('roughness','Roughness',True),('normal',None,True)]:
   tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(O/ti[key]),check_existing=True)
   if noncolor:tex.image.colorspace_settings.name='Non-Color'
   m.node_tree.links.new(mp.outputs['Vector'],tex.inputs['Vector'])
   if socket:m.node_tree.links.new(tex.outputs['Color'],bs.inputs[socket])
   else:
    n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.25;m.node_tree.links.new(tex.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],bs.inputs['Normal'])
 m.diffuse_color=(*[linear(x) for x in v['color']],v.get('alpha',1));m['Appearance_Source']='Photo-referenced modeled PBR microtexture; source weathering not baked';mats[k]=m
ground_meshes=[]
for row in I:
 d=np.load(O/'02_Data'/row['file']);e=row['element'];v=d['vertices'];f=d['faces'];uv=d['uv'];mid=d['material_ids'];group=bpy.data.objects.new(row['name'],None);col.objects.link(group)
 if e.get('definition') or (e.get('role')=='LEAF' and e.get('door_id')):
  pivot=e.get('hinge_origin_local_m',e.get('origin',[0,0,0])) if e.get('role')=='LEAF' else e.get('origin',[0,0,0])
  a=e.get('angle',0);c=math.cos(a);s=math.sin(a);inv=np.array([[c,s,0],[-s,c,0],[0,0,1]]);v=(v-np.array(pivot))@inv.T;group.location=pivot;group.rotation_euler[2]=a
  group['Pivot_LOCAL_m']=list(pivot)
 for k in ['door_id','role','parent_door_id','assembly_id','source','confidence','layer','family']:group[k]=str(e.get(k,''))
 group['Parameters']=json.dumps(e,ensure_ascii=False)
 triangle_uv=uv[f.ravel()]
 smooth_ground=row['name'].startswith(('SITE_V12_REBUILT_EARTH','SITE_V12_REBUILT_ROAD'))
 if smooth_ground:
  _,weld_indices,weld_inverse=np.unique(np.round(v,8),axis=0,return_index=True,return_inverse=True);v=v[weld_indices];f=weld_inverse[f]
 me=bpy.data.meshes.new(row['name']);me.from_pydata(v.tolist(),[],f.tolist());me.update();ob=bpy.data.objects.new(row['name']+'_Geometry',me);col.objects.link(ob);ob.parent=group
 if smooth_ground:
  for polygon in me.polygons:polygon.use_smooth=polygon.normal.z>.35
  ground_meshes.append((ob,v,f,'EARTH' if row['name'].startswith('SITE_V12_REBUILT_EARTH') else 'ROAD'))
  ob['Terrain_Shading']='Shared top-only normal field across adjacent panels; side and bottom normals excluded; elevations unchanged'
 for m in row['materials']:me.materials.append(mats[m])
 me.polygons.foreach_set('material_index',mid.astype(np.int32));u=me.uv_layers.new(name='Modeled_Metre_UV');u.data.foreach_set('uv',triangle_uv.astype(np.float32).ravel());ob['SourcePhotogrammetricFaces']=0;ob['GeometryRole']='Reconstructed modeled surface or component'
# A closed terrain panel's vertical/bottom faces must never influence its top normals.
# Share the top normal field across neighboring panels of the same surface category.
for category in ['EARTH','ROAD']:
 items=[a for a in ground_meshes if a[3]==category];xyz=np.concatenate([a[1] for a in items]);_,inv=np.unique(np.round(xyz,4),axis=0,return_inverse=True);normal_sums=np.zeros((int(inv.max())+1,3));offset=0;records=[]
 for ob,v,f,_ in items:
  face_cross=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);lengths=np.linalg.norm(face_cross,axis=1);face_normals=face_cross/np.maximum(lengths[:,None],1e-30);top=face_normals[:,2]>.35;vertex_ids=inv[offset:offset+len(v)];offset+=len(v)
  for corner in range(3):np.add.at(normal_sums,vertex_ids[f[top,corner]],face_cross[top])
  records.append((ob,f,vertex_ids,face_normals,top))
 normal_sums/=np.maximum(np.linalg.norm(normal_sums,axis=1)[:,None],1e-30)
 for ob,f,vertex_ids,face_normals,top in records:
  split=np.repeat(face_normals[:,None,:],3,axis=1);split[top]=normal_sums[vertex_ids[f[top]]];ob.data.normals_split_custom_set(split.reshape(-1,3).tolist());ob.data.update()
groups={ob.get('door_id'):ob for ob in col.objects if ob.type=='EMPTY' and ob.get('role')=='LEAF'}
for did,ob in groups.items():
 pa=groups.get(ob.get('parent_door_id'))
 if pa:bpy.context.view_layer.update();mw=ob.matrix_world.copy();ob.parent=pa;ob.matrix_world=mw
world=bpy.data.worlds.new('Neutral_Inspection');world.use_nodes=True;bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.75,.79,.83,1);bg.inputs[1].default_value=.7;sc.world=world
sd=bpy.data.lights.new('Site_Inspection_Sun','SUN');sd.energy=2.2;sun=bpy.data.objects.new('Site_Inspection_Sun',sd);sc.collection.objects.link(sun);sun.rotation_euler=(.4,-.55,-.4)
cameras=[('V12_Whole_Site',[98,-124,88],[-2,-4,0],54,None),('V12_Architecture',[35,-52,29],[1,-4,2],54,None),('V12_Top_Roofs',[-3,-4,65],[-3,-4,0],50,64),('V12_Kitchen_Timber',[4.4,-9.4,2.3],[10.5,-7.2,1.9],60,None),('V12_Kitchen_Truss',[9.65,-7.05,.95],[11,-7.05,3.25],94,None),('V12_Kitchen_Interior_Front',[12.0,-7.05,1.1],[8.9,-7.05,2.0],110,None),('V12_Entrance_Ramp',[-20,-18,3],[-15,-11.5,-.1],60,None),('V12_Screenwall',[0,-23,6],[7,-16.9,2.8],56,None)]
for name,pos,tar,fov,ortho in cameras:
 cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cd.angle=math.radians(fov)
 if ortho:cd.type='ORTHO';cd.ortho_scale=ortho
sc.camera=bpy.data.objects['V12_Whole_Site'];bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
 if ob.type in ['MESH','EMPTY','CAMERA']:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'05_Export/Complete_Site_V12_LOCAL.glb'),use_selection=True,export_format='GLB',export_cameras=True,export_extras=True)
bpy.ops.export_scene.fbx(filepath=str(O/'05_Export/Complete_Site_V12_LOCAL.fbx'),use_selection=True,global_scale=1,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',object_types={'MESH','EMPTY','CAMERA'},bake_anim=False,use_custom_props=True,path_mode='COPY',embed_textures=True)
sc.render.engine='CYCLES';sc.cycles.samples=12;sc.render.resolution_x=1600;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.view_settings.view_transform='Standard'
format_enums=[i.identifier for i in sc.render.image_settings.bl_rna.properties['file_format'].enum_items];assert 'PNG' in format_enums;sc.render.image_settings.file_format='PNG'
light=bpy.data.lights.new('Kitchen_Inspection_Light','POINT');light.energy=100;light.shadow_soft_size=.65;lo=bpy.data.objects.new('Kitchen_Inspection_Light',light);sc.collection.objects.link(lo);lo.location=[10,-7,2.1];lo['Role']='Review-only inspection light, not surveyed fixture'
for name,_,_,_,_ in cameras:
 sc.camera=bpy.data.objects[name];sc.render.filepath=str(O/'06_Report'/f'{name}.png');bpy.ops.render.render(write_still=True)
sc.camera=bpy.data.objects['V12_Whole_Site'];bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Complete_Site_V12_LOCAL.blend'))
(O/'06_Report/Modeled_Exchange_QA.json').write_text(json.dumps({'status':'EXPORTED_PENDING_READBACK','modeled_nodes':len(I),'triangles':sum(r['triangles'] for r in I),'source_photogrammetry_triangles':0,'reconstructed_geometry_in_missing_area':True,'coordinate':'LOCAL metres Z-up; apply Coordinate.json for original ENU','ue5_imported':False,'appearance':'Photo-referenced modeled PBR microtexture; source photographs and textures provided separately','pbr_textured_materials':len(TM)},indent=2),encoding='utf8')
print('V12 all-modeled export/render complete',flush=True)
