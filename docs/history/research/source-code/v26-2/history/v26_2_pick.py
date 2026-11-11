from pathlib import Path
import bpy,sys,json
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_2_views import VIEWS
P='E:/jz/JIA/Rebuild_V26_2/Blender/Architecture_Complete_V26_2.blend';bpy.ops.wm.open_mainfile(filepath=P);sc=bpy.context.scene;sc.frame_set(40);sc.render.resolution_x=1000;sc.render.resolution_y=800;sc.render.resolution_percentage=100
points={'03_Rear_Window_Wall':[(650,650),(450,590),(550,730),(850,740),(800,505),(780,600)],'05_Ceiling_Head_Joints':[(660,648),(700,600),(744,552),(600,500)],'01_Stair_Wall_Band':[(500,600),(500,350)]}
for tag,pos,aim,lens in VIEWS:
 if tag not in points:continue
 c=bpy.data.objects.new('pick',bpy.data.cameras.new('pick'));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;sc.camera=c;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();frame=c.data.view_frame(scene=sc);xmin,xmax=min(p.x for p in frame),max(p.x for p in frame);ymin,ymax=min(p.y for p in frame),max(p.y for p in frame);z=frame[0].z
 for px,py in points[tag]:
  d=c.matrix_world.to_3x3()@Vector((xmin+(px+.5)/1000*(xmax-xmin),ymax-(py+.5)/800*(ymax-ymin),z));d.normalize();hit,p,no,face,obj,mat=sc.ray_cast(dg,c.matrix_world.translation,d)
  if hit:
   me=obj.data;pol=me.polygons[face];print('PICK',tag,px,py,obj.name,face,me.materials[pol.material_index].name,'point',list(p),'normal',list(no),'vertices',[[*(obj.matrix_world@me.vertices[i].co)]for i in pol.vertices],flush=True)
 for node in bpy.data.materials['M_Wall_Interior'].node_tree.nodes:
  print('WALL_NODE',node.type,[(i.name,str(i.default_value))for i in node.inputs if hasattr(i,'default_value')],flush=True)
