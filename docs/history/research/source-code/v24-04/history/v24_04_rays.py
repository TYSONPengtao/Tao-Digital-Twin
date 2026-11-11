import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_03/Blender/Architecture_Complete_V24_03.blend');sc=bpy.context.scene;sc.frame_set(40)
c=bpy.data.objects.new('Probe_Camera',bpy.data.cameras.new('Probe_Camera'));sc.collection.objects.link(c);c.location=(4.2,-.6,2.1);c.rotation_euler=(Vector((9.6,-2.8,1.5))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=28
bpy.context.view_layer.update();proj=c.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=1200,y=900);inv=(proj@c.matrix_world.inverted()).inverted();dg=bpy.context.evaluated_depsgraph_get()
for x,y in [(200,450),(340,420),(360,500),(375,500),(390,500),(410,500),(430,500),(450,500),(385,600),(500,250),(500,200),(430,250)]:
 p=inv@Vector((x/600-1,1-y/450,1,1));p=Vector(p[:3])/p.w;hit,loc,normal,index,obj,mat=sc.ray_cast(dg,c.location,(p-c.location).normalized());print('RAY',x,y,hit,tuple(loc),obj.name if obj else None,flush=True)
