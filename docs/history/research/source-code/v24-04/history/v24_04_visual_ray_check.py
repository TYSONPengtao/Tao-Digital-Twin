import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_04/Blender/Architecture_Complete_V24_04.blend');sc=bpy.context.scene;sc.frame_set(40)
c=bpy.data.objects.new('Visual_Check',bpy.data.cameras.new('Visual_Check'));sc.collection.objects.link(c);c.location=(4.2,-.6,2.1);c.rotation_euler=(Vector((9.6,-2.8,1.5))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=28;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();pr=c.calc_matrix_camera(dg,x=1600,y=1200);inv=(pr@c.matrix_world.inverted()).inverted()
for x,y in [(970,600),(980,600),(990,600),(1000,600),(1010,600),(970,900),(980,900),(990,900),(1000,900),(1010,900)]:
 p=inv@Vector((x/800-1,1-y/600,1,1));p=Vector(p[:3])/p.w;hit,loc,no,idx,o,mat=sc.ray_cast(dg,c.location,(p-c.location).normalized());m=o.data.materials[o.data.polygons[idx].material_index].name if o and o.type=='MESH'and idx<len(o.data.polygons)and len(o.data.materials)else None;print('VISUAL_RAY',x,y,o.name if o else None,tuple(loc),m,flush=True)
