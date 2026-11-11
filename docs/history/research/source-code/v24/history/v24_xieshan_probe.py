import bpy,sys,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_xieshan_roof_blender import apply_v24_xieshan_roof
O=W/'v24_xieshan_probe';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24_02.blend')
apply_v24_xieshan_roof(bpy,O)
s=bpy.context.scene;s.frame_set(20);s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
for label,pos,tar,lens in [('Xieshan_Low',[4.4,-16.5,2.0],[6.6,-11.57,2.35],35),('Xieshan_Top',[3.2,-14.5,5.7],[6.6,-11.57,2.90],42)]:
 c=bpy.data.objects.new(label,bpy.data.cameras.new(label));s.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;s.camera=c;s.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True);print('VIEW',label,flush=True)
print('PROBE DONE',flush=True)
