import bpy,math
from pathlib import Path
from mathutils import Vector
O=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid')
bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Reality_Hybrid_V10_LOCAL.blend'))
sc=bpy.context.scene
bpy.data.collections['BASE_REALITY_UNCHANGED'].hide_render=True
bpy.data.collections['PATCH_ONLY_MISSING_AREA'].hide_render=True
col=bpy.data.collections['FULL_EDITABLE_WALL_REVIEW_ONLY'];col.hide_render=False;col.hide_viewport=False
for ob in col.objects:ob.hide_render=ob.name.startswith('SITE_PERIMETER_')
cam=bpy.data.objects['V10_Wall_Detail'];cam.location=[5,-6,2.8];cam.rotation_euler=(Vector([0,-6,1.05])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.angle=math.radians(52);sc.camera=cam
sc.render.filepath=str(O/'06_Report/V10_Complete_Courtyard_Wall.png');bpy.ops.render.render(write_still=True)
print('Complete courtyard wall preview rendered; exchange/model files untouched',flush=True)
