from pathlib import Path
import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V26_1/Blender/Architecture_Complete_V26_1.blend');sc=bpy.context.scene;sc.frame_set(40);sc.render.resolution_x=1100;sc.render.resolution_y=825;sc.render.resolution_percentage=100;dg=bpy.context.evaluated_depsgraph_get()
for tag,points in [('07_Reference_Screenwall',[(520,370),(650,395),(636,510),(640,610),(590,500),(585,330)]),('08_Gate_Floor',[(670,650),(725,595),(570,600),(350,510),(200,390),(820,630)])]:
 c=bpy.data.objects['V26_1_'+tag];frame=c.data.view_frame(scene=sc);xmin=min(p.x for p in frame);xmax=max(p.x for p in frame);ymin=min(p.y for p in frame);ymax=max(p.y for p in frame);z=frame[0].z
 for x,y in points:
  d=c.matrix_world.to_3x3()@Vector((xmin+(x+.5)/1100*(xmax-xmin),ymax-(y+.5)/825*(ymax-ymin),z));d.normalize();hit,pos,no,face,o,mat=sc.ray_cast(dg,c.matrix_world.translation,d);print('PICK',tag,x,y,o.name if hit else None,tuple(pos)if hit else None,'face',face,flush=True)
