import bpy,bmesh,json,shutil
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V3');fixes={}
for mode in ['ARCH','VIS']:
 p=O/'08_Export'/f'Production_1QK_{mode}.blend';bpy.ops.wm.open_mainfile(filepath=str(p));removed=0
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  if not any(face.area<1e-10 for face in ob.data.polygons):continue
  bm=bmesh.new();bm.from_mesh(ob.data);bad=[f for f in bm.faces if f.calc_area()<1e-10];removed+=len(bad);bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY');bm.to_mesh(ob.data);bm.free();ob.data.update()
 bpy.ops.object.select_all(action='DESELECT')
 for ob in bpy.context.scene.objects:
  if ob.type=='CAMERA' or (ob.type=='EMPTY' and ob.get('confidence')!='LOW') or (ob.type=='MESH' and not ob.hide_render):ob.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(O/'08_Export'/f'Production_1QK_{mode}.fbx'),use_selection=True,global_scale=1.0,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',object_types={'MESH','CAMERA','EMPTY'},bake_anim=False,add_leaf_bones=False)
 bpy.ops.export_scene.gltf(filepath=str(O/'08_Export'/f'Production_1QK_{mode}.glb'),use_selection=True,export_format='GLB',export_cameras=True)
 bpy.ops.wm.obj_export(filepath=str(O/'08_Export'/f'Production_1QK_{mode}.obj'),export_selected_objects=True,forward_axis='Y',up_axis='Z',export_triangulated_mesh=True,export_uv=True,export_normals=True,export_materials=True)
 bpy.context.scene.camera=bpy.data.objects['CAM_06_Whole_Site'];bpy.ops.wm.save_as_mainfile(filepath=str(p));fixes[mode]={'zero_area_ground_triangles_removed':removed,'dimensional_change':0}
(O/'09_Report/Exchange_Surface_Cleanup.json').write_text(json.dumps(fixes,indent=2),encoding='utf-8');print(fixes)
for ext in ['obj','mtl']:shutil.copy2(O/'08_Export'/('Production_1QK_ARCH.'+ext),O/'08_Export'/('Production_1QK_Rebuild.'+ext))
