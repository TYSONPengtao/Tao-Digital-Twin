import bpy,json
from mathutils import Vector
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Reality_Hybrid_V7_LOCAL.blend'));sc=bpy.context.scene
cam=bpy.data.objects['V7_F2_Stair_Wall'];dg=bpy.context.evaluated_depsgraph_get()
print('CAMERA',list(cam.location),flush=True)
for target in [[6.4,7.3,5.5],[6.4,7.3,6.2],[6.4,7.3,4.5],[5.5,7.3,5.5],[7.5,7.3,5.5]]:
 dr=Vector(target)-cam.location;hit,loc,n,ind,ob,mat=sc.ray_cast(dg,cam.location,dr.normalized(),distance=20)
 print('RAY',target,'hits',ob.name if ob else None,'location',list(loc),'distance',(loc-cam.location).length,flush=True)
