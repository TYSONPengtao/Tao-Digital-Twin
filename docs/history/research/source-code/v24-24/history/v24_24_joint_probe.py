import bpy,sys,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_24/Blender/Architecture_Complete_V24_24.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.resolution_x=1120;sc.render.resolution_y=800
c=bpy.data.objects['V24_24_Gate_Junction_High'];vf=c.data.view_frame(scene=sc);xmin=min(v.x for v in vf);xmax=max(v.x for v in vf);ymin=min(v.y for v in vf);ymax=max(v.y for v in vf);z=vf[0].z
for x,y in[(.49,.46),(.52,.45),(.55,.445),(.58,.44),(.55,.48),(.48,.49),(.46,.48)]:
 d=c.matrix_world.to_3x3()@Vector((xmin+(xmax-xmin)*x,ymax-(ymax-ymin)*y,z)).normalized();hit,loc,no,i,o,m=sc.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,d);print('GAP_RAY',x,y,o.name if o else None,list(loc),list(no),flush=True)
o=bpy.data.objects['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry'];me=o.data;me.calc_loop_triangles();tr=BVHTree.FromPolygons([o.matrix_world@p.co for p in me.vertices],[t.vertices[:]for t in me.loop_triangles],all_triangles=True)
for x in [8.34,8.6,8.9,9.2,9.5,9.7]:
 for y in [-12.1,-11.95,-11.8,-11.65,-11.4]:
  h=tr.ray_cast(Vector((x,y,6)),Vector((0,0,-1)),5)[0];print('ROOF',x,y,list(h)if h else None,flush=True)
