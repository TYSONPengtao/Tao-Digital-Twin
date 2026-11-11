import bpy,json,sys
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_23/Blender/Architecture_Complete_V24_23.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.resolution_x=1120;sc.render.resolution_y=800
for cam,points in [('Storage_Wide',[(.44,.395),(.43,.41),(.42,.38),(.46,.40),(.47,.44)])]:
 c=bpy.data.objects['V24_23_'+cam];vf=c.data.view_frame(scene=sc);xmin=min(v.x for v in vf);xmax=max(v.x for v in vf);ymin=min(v.y for v in vf);ymax=max(v.y for v in vf);z=vf[0].z
 for x,y in points:
  d=c.matrix_world.to_3x3()@Vector((xmin+(xmax-xmin)*x,ymax-(ymax-ymin)*y,z)).normalized();hit,loc,no,i,o,m=sc.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,d)
  print('HIT',cam,(x,y),o.name if o else None,list(loc),i,flush=True)
