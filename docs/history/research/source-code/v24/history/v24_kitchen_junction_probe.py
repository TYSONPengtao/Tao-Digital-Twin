import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_kitchen_junction_blender import apply_v24_kitchen_junction
O=W/'v24_kitchen_junction_probe';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24.blend')
proof=apply_v24_kitchen_junction(bpy,O)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True
sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for j,(pos,tar,angle) in enumerate([([8.9,-13.2,2.1],[10.5,-11.85,3.45],90)]):
 cd=bpy.data.cameras.new('V24_Kitchen_Junction_Probe');cam=bpy.data.objects.new('V24_Kitchen_Junction_Probe',cd);sc.collection.objects.link(cam)
 cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cd.angle=math.radians(angle);sc.camera=cam
 sc.render.filepath=str(O/f'Kitchen_Junction_{j+1}.png');bpy.ops.render.render(write_still=True)
print('KITCHEN_PROBE_COMPLETE',flush=True)
