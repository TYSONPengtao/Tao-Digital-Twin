import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_20/Blender/Architecture_Complete_V24_20.blend');sc=bpy.context.scene;sc.frame_set(40);cam=bpy.data.objects['V24_20_Roof_Units'];dg=bpy.context.evaluated_depsgraph_get()
for px,py in [(770,170),(790,170),(810,170),(770,190),(790,190),(810,190),(790,210),(770,150)]:
 d=Vector(((px/1400-.5)*36/50,(.5-py/1050)*36/50*.75,-1));d=cam.matrix_world.to_3x3()@d;hit=sc.ray_cast(dg,cam.location,d.normalized(),distance=100);print('HIT',px,py,hit[4].name if hit[0]else None,list(hit[1])if hit[0]else None,flush=True)
