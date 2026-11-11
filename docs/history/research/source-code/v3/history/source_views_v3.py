import bpy,math
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath=str(W/'CCM_Reference_Local.blend'))
scene=bpy.context.scene;scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
out=W/'evidence_v3';out.mkdir(exist_ok=True)
for name,pos,target in [('South_Outer_Wall',[7,-33,8],[7,-16,0]),('West_Service_Entry',[-22,-22,7],[-13,-11,.5]),('Inner_Gate',[6,-23,6],[6,-12,1]),('SE_Passage',[27,-24,7],[13,-14,.7]),('Inside_SW_Passage',[-6,-12,2],[-13,-12,1]),('Overall',[30,-42,38],[-4,-3,1])]:
 cam=scene.camera;cam.data.type='PERSP';cam.data.lens=35;cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
print('SOURCE VIEWS COMPLETE')
