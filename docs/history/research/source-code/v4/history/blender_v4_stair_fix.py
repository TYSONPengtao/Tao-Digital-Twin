import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(r'E:\jz\JIA\Rebuild_V4');SCENE=json.loads((OUT/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
def linear(c):
 c=c/255
 return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
def material(name,spec):
 m=bpy.data.materials.new(name);m.diffuse_color=(*[linear(x) for x in spec['color']],1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*[linear(x) for x in spec['color']],1);bs.inputs['Roughness'].default_value=spec['roughness'];bs.inputs['Metallic'].default_value=spec.get('metallic',0)
 if spec.get('alpha',1)<1:bs.inputs['Transmission Weight'].default_value=.85;bs.inputs['IOR'].default_value=spec.get('ior',1.52)
 return m
for mode in ['ARCH','VIS']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1.0
 bpy.ops.wm.obj_import(filepath=str(OUT/'08_Export'/f'Production_1QK_{mode}.obj'),forward_axis='Y',up_axis='Z',use_split_objects=True,use_split_groups=False)
 mats={k:material(k,v) for k,v in SCENE['materials'].items()};col=bpy.data.collections.new('ARCH_MODEL');bpy.context.scene.collection.children.link(col);vcol=bpy.data.collections.new('VIS_MODEL');bpy.context.scene.collection.children.link(vcol);sitecol=bpy.data.collections.new('SITE_MODEL');bpy.context.scene.collection.children.link(sitecol)
 elem={e['name']:e for e in SCENE['elements']};groups={};mesh_cache={}
 for ob in list(bpy.context.scene.objects):
  for i,m in enumerate(ob.data.materials):
   key=m.name.split('.')[0]
   if key in mats:ob.data.materials[i]=mats[key]
  target=sitecol if 'SITE_' in ob.name or 'LANE' in ob.name or 'ROAD' in ob.name or 'COURTYARD' in ob.name else vcol if ob.name.startswith('VIS_MODEL') else col
  for old in list(ob.users_collection):old.objects.unlink(ob)
  target.objects.link(ob)
  fields=ob.name.split('__');e=elem.get(fields[1]) if len(fields)>2 else None
  if e:
   if e['name'] not in groups:
    group=bpy.data.objects.new(e['name'],None);target.objects.link(group);groups[e['name']]=group
    for k in ['source','confidence','layer','family','status','definition','classification']:group[k]=str(e.get(k,''))
    if 'definition' in e:
     group.location=e['origin'];group.rotation_euler[2]=e.get('angle',0)
   group=groups[e['name']]
   if 'definition' in e:
    key=(e['definition'],fields[-1]);angle=e.get('angle',0);origin=Vector(e['origin']);inv=Matrix.Rotation(-angle,3,'Z')
    if key not in mesh_cache:
     for v in ob.data.vertices:v.co=inv@(v.co-origin)
     ob.data.name='DEF_'+e['definition']+'__'+fields[-1];mesh_cache[key]=ob.data
    else:ob.data=mesh_cache[key]
   ob.parent=group
   ob['Element']=e['name'];ob['Confidence']=e['confidence'];ob['Layer']=e['layer']
  if e and e['confidence']=='LOW':
   ob.hide_render=True;ob['Confidence']='LOW';ob['Default_Visibility']='HIDDEN_UNCERTAIN'
  # metre-based planar/box mapping with consistent one metre texel scale.
  uv=ob.data.uv_layers.new(name='UV_1m') if not ob.data.uv_layers else ob.data.uv_layers[0]
  for face in ob.data.polygons:
   axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3) if k!=axis]
   for li in face.loop_indices:
    p=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]],p[axes[1]])
  if (e and e.get('definition','').startswith('ROMAN_')) or (e and e['name'].startswith('SITE_TREE')):
   for poly in ob.data.polygons:poly.use_smooth=True
  ob['LengthUnit']='metres';ob['Source']='Architecture_Scene.json';ob['Reconstruction']='Clean rebuilt geometry; reference mesh excluded'
 for cam in SCENE['cameras']:
  cd=bpy.data.cameras.new(cam['name']);ob=bpy.data.objects.new(cam['name'],cd);bpy.context.scene.collection.objects.link(ob);ob.location=cam['position'];direction=Vector(cam['target'])-ob.location;ob.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cd.angle=math.radians(cam['fov']);ob['Status']=cam['status']
  if cam['name']=='CAM_02_Front':bpy.context.scene.camera=ob
 bpy.context.view_layer.update();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];bounds_min=[min((o.matrix_world@v.co)[k] for o in meshes for v in o.data.vertices) for k in range(3)];bounds_max=[max((o.matrix_world@v.co)[k] for o in meshes for v in o.data.vertices) for k in range(3)]
 bpy.ops.object.select_all(action='DESELECT')
 for ob in bpy.context.scene.objects:
  if ob.type=='CAMERA' or (ob.type=='EMPTY' and ob.get('confidence')!='LOW') or (ob.type=='MESH' and not ob.hide_render):ob.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(OUT/'08_Export'/f'Production_1QK_{mode}.fbx'),use_selection=True,global_scale=1.0,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',object_types={'MESH','CAMERA','EMPTY'},bake_anim=False,add_leaf_bones=False)
 bpy.ops.export_scene.gltf(filepath=str(OUT/'08_Export'/f'Production_1QK_{mode}.glb'),use_selection=True,export_format='GLB',export_cameras=True)
 bpy.context.scene.world=bpy.data.worlds.new('World');bpy.context.scene.world.use_nodes=True;bpy.context.scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.75,.8,1);bpy.context.scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 sun_data=bpy.data.lights.new('REVIEW_SUN','SUN');sun_data.energy=2.2;sun=bpy.data.objects.new('REVIEW_SUN',sun_data);bpy.context.scene.collection.objects.link(sun);sun.rotation_euler=(.5,-.4,-.5)
 bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=24;bpy.context.scene.render.resolution_x=1600;bpy.context.scene.render.resolution_y=1000;bpy.context.scene.render.resolution_percentage=100
 bpy.context.scene.render.image_settings.file_format='PNG';bpy.context.scene.view_settings.view_transform='Standard';bpy.context.scene.render.film_transparent=False
 for camera_name in ([] if mode=='ARCH' else ['CAM_13_Stair_Coordination']):
  hidden=[]
  if camera_name=='CAM_13_Stair_Coordination':
   for ob in bpy.context.scene.objects:
    if ob.type=='MESH' and not ob.hide_render and (ob.get('Layer') in ['10_WALL_EXT','11_WALL_INT','20_COLUMN','21_BEAM','50_ROOF','51_CANOPY','31_WINDOW','30_DOOR','41_RAILING'] and not ob.get('Element','').startswith(('STAIR','RAIL_STAIR')) or ob.get('Element','').startswith(('SLAB_JOINED_','CONSTRUCTION_TERRACE','TERRACE','ROOF_'))):
     hidden.append(ob);ob.hide_render=True
  bpy.context.scene.camera=bpy.data.objects[camera_name];bpy.context.scene.render.filepath=str(OUT/'09_Report'/f'{mode}_{camera_name}.png');bpy.ops.render.render(write_still=True)
  for ob in hidden:ob.hide_render=False
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'08_Export'/f'Production_1QK_{mode}.blend'))
 (OUT/'09_Report'/f'Blender_{mode}_Export_QA.json').write_text(json.dumps({'mesh_objects':len(meshes),'unique_meshes':len(set(o.data.name for o in meshes)),'semantic_groups':len(groups),'bounds_m':[bounds_min,bounds_max],'unit_scale':1.0,'cameras':len(SCENE['cameras']),'UV':'Planar per face normal, 1 model metre = 1 UV unit','fbx':'exported; readback pending','glb':'exported; readback pending'},indent=2),encoding='utf-8')
print('BLENDER EXPORTS COMPLETE')
