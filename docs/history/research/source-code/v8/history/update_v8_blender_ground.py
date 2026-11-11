import bpy,json,math
from pathlib import Path
import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'))
bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Reality_Hybrid_V8_LOCAL.blend'))
sc=bpy.context.scene;col=bpy.data.collections['PATCH_ONLY_MISSING_AREA'];added=[]
paths={p.name.casefold():p for folder in ['Base','Patch'] for p in (O/'03_Textures'/folder).iterdir() if p.is_file()}
def restore_image_paths():
 for im in bpy.data.images:
  key=Path(im.filepath.replace('\\','/')).name.casefold()
  if key in paths:im.filepath=str(paths[key])
restore_image_paths()
for r in I:
 if r['name'] in bpy.data.objects:
  if not r['name'].startswith('V8_CONTACT_GAP_'):continue
  old=bpy.data.objects[r['name']]
  for child in list(old.children):bpy.data.objects.remove(child,do_unlink=True)
  bpy.data.objects.remove(old,do_unlink=True)
 d=np.load(O/'02_Data'/r['file']);e=r['element'];v=d['vertices'];f=d['faces'];u=d['uv'];mi=d['material_ids']
 assert not e.get('definition'),'New ground should have LOCAL baked coordinates'
 group=bpy.data.objects.new(r['name'],None);col.objects.link(group)
 for k in ['role','source','confidence','layer']:group[k]=str(e.get(k,''))
 group['Parameters']=json.dumps(e,ensure_ascii=False);group['PatchRole']=r['role']
 me=bpy.data.meshes.new(r['name']+'_Geometry');me.from_pydata(v.tolist(),[],f.tolist());me.update()
 for m in r['materials']:me.materials.append(bpy.data.materials[m])
 me.polygons.foreach_set('material_index',mi.astype(np.int32));uv=me.uv_layers.new(name='Original_Photo_UV');vi=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',vi);uv.data.foreach_set('uv',u[vi].astype(np.float32).ravel())
 ob=bpy.data.objects.new(r['name']+'_Geometry',me);col.objects.link(ob);ob.parent=group;ob['Role']=e.get('role','MEASURED_GROUND_GAP_REPAIR');ob['Element']=r['name'];added.append(r['name'])
assert added,'No missing ground patch found'
bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
 if ob.type in ['MESH','EMPTY','CAMERA']:ob.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(O/'05_Export/Reality_Hybrid_V8_LOCAL.fbx'),use_selection=True,global_scale=1,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',object_types={'MESH','EMPTY','CAMERA'},bake_anim=False,use_custom_props=True,path_mode='COPY',embed_textures=True)
bpy.ops.export_scene.gltf(filepath=str(O/'05_Export/Reality_Hybrid_V8_LOCAL.glb'),use_selection=True,export_format='GLB',export_cameras=True,export_extras=True)
bpy.ops.wm.obj_export(filepath=str(O/'05_Export/Reality_Hybrid_V8_LOCAL.obj'),export_selected_objects=True,forward_axis='Y',up_axis='Z',export_triangulated_mesh=False,export_uv=True,export_normals=True,export_materials=True,path_mode='COPY')
for name in ['V8_Whole_Site','V8_Wall_Building_Closure']:
 sc.camera=bpy.data.objects[name];sc.render.filepath=str(O/'06_Report'/f'{name}.png');bpy.ops.render.render(write_still=True)
sc.camera=bpy.data.objects['V8_Whole_Site'];restore_image_paths();bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Reality_Hybrid_V8_LOCAL.blend'))
q=O/'06_Report/Blender_Hybrid_Export_QA.json';j=json.loads(q.read_text(encoding='utf-8'));j.update(patch_nodes=len(I),mesh_objects=sum(o.type=='MESH' for o in sc.objects),final_ground_gap_repair_nodes=added);q.write_text(json.dumps(j,indent=2),encoding='utf-8')
print('Ground residual patches added and exchanges refreshed:',added,flush=True)
