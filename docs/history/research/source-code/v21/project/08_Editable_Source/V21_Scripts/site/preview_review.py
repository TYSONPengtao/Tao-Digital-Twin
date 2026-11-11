import bpy,math,json
from pathlib import Path
from mathutils import Vector
D=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V21/05_Export/Actual_Rhino_V21_Readback_LOCAL.blend')
sc=bpy.context.scene
sc.cycles.samples=12
sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
tests=[['Front_Fretwork_Final_Camera',[14.65,-16.65,1.00],[14.65,-14.855,1.10],84]]
cam=bpy.data.objects['V21_Storage_Front_Fretwork'];sc.camera=cam
for name,pos,tar,fov in tests:
 cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.angle=math.radians(fov)
 sc.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
(D/'Camera_Review.json').write_text(json.dumps(tests,indent=2),encoding='utf8')
