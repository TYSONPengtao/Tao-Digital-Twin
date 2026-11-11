import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path('E:/jz/JIA/Rebuild_V20');bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V20_Readback_LOCAL.blend'));sc=bpy.context.scene
cam=bpy.data.objects['V20_Storage_Aligned_Gallery'];cam.location=[14.15,-15.45,1.1];cam.rotation_euler=(Vector([18.82,-15.45,1.0])-cam.location).to_track_quat('-Z','Y').to_euler();sc.frame_set(40);bpy.ops.wm.save_as_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V20_Readback_LOCAL.blend'));sc.camera=cam;sc.render.filepath=str(O/'06_Report/V20_Storage_Aligned_Gallery.png');bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
 if ob.type in ['MESH','EMPTY','CAMERA']:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'05_Export/Complete_Site_V20_LOCAL.glb'),use_selection=True,export_format='GLB',export_cameras=True,export_extras=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_current_frame=True)
v=json.loads((O/'06_Report/Preview_View_States.json').read_text(encoding='utf8'));v['inspection_lighting']='Interior inspection point lights; all model geometry visible';v['review_camera_positions']={'V20_House_Entry_One_Solid_Step':[8.5,-2.2,1.1],'V20_Storage_Aligned_Gallery':[14.15,-15.45,1.1]};(O/'06_Report/Preview_View_States.json').write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');print('GALLERY REVIEW COMPLETE')
