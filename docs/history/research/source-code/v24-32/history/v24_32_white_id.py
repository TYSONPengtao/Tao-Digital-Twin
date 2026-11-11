import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_32/Blender/Architecture_Complete_V24_32.blend');sc=bpy.context.scene;sc.frame_set(40);sc.render.resolution_x=1600;sc.render.resolution_y=1100;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();c=bpy.data.objects['V24_32_Exterior_Right_Flat'];fr=c.data.view_frame(scene=sc);xl=min(p.x for p in fr);xh=max(p.x for p in fr);yl=min(p.y for p in fr);yh=max(p.y for p in fr);zz=fr[0].z
for py in [910,925,940,955]:
 for px in [1234,1246,1254]:
  d=(c.matrix_world.to_3x3()@Vector((xl+(xh-xl)*px/1600,yh-(yh-yl)*py/1100,zz))).normalized();ok,q,no,k,o,ma=sc.ray_cast(dg,c.location,d,distance=50)
  print(px,py,o.name if ok else None,list(q)if ok else None,flush=True)
