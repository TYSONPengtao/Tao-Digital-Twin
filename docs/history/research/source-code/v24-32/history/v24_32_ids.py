import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_32/Blender/Architecture_Complete_V24_32.blend');sc=bpy.context.scene;sc.frame_set(40);sc.render.resolution_x=1120;sc.render.resolution_y=800;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();c=bpy.data.objects['V24_32_Exterior_Back_Flat'];fr=c.data.view_frame(scene=sc);xl=min(p.x for p in fr);xh=max(p.x for p in fr);yl=min(p.y for p in fr);yh=max(p.y for p in fr);zz=fr[0].z
for py in [356,360,364,495,500,505]:
 for px in [626,631,636,641]:
  d=(c.matrix_world.to_3x3()@Vector((xl+(xh-xl)*px/1120,yh-(yh-yl)*py/800,zz))).normalized();ok,q,no,k,o,ma=sc.ray_cast(dg,c.location,d,distance=50)
  print(px,py,o.name if ok else None,list(q)if ok else None,flush=True)
