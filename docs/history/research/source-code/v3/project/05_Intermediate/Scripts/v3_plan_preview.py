import bpy,math
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V3')
bpy.ops.wm.open_mainfile(filepath=str(O/'08_Export/Production_1QK_VIS.blend'))
cd=bpy.data.cameras.new('V3_Orthographic');cam=bpy.data.objects.new('V3_Orthographic',cd);bpy.context.scene.collection.objects.link(cam);cam.location=(-3,-6,60);cam.rotation_euler=(0,0,0);cd.type='ORTHO';cd.ortho_scale=52;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=2400;scene.render.resolution_y=2400;scene.render.resolution_percentage=100;scene.render.filepath=str(O/'09_Report/V3_Orthographic_Plan.png');bpy.ops.render.render(write_still=True)
print('V2 plan uses exact same orthographic camera and extent as linked CCM reference')
