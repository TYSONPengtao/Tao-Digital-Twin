from pathlib import Path
import bpy,json,math
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_35';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_34/Blender/Architecture_Complete_V24_34.blend');sc=bpy.context.scene;sc.frame_set(40);sc.render.resolution_x=1500;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;c=bpy.data.objects.new('IDENTIFY',bpy.data.cameras.new('IDENTIFY'));sc.collection.objects.link(c);c.location=(26,-13.5,4.4);c.rotation_euler=(Vector((13.8,-7.5,1.5))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=35;sc.camera=c;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();corners=c.data.view_frame(scene=sc);lo=Vector((min(v.x for v in corners),min(v.y for v in corners),corners[0].z));hi=Vector((max(v.x for v in corners),max(v.y for v in corners),corners[0].z));rows=[]
for xy in [(1020,430),(950,470),(1100,410),(1150,450),(1080,540),(870,510),(1170,500),(700,550),(1200,480),(720,370)]:
 x,y=xy;local=Vector((lo.x+(hi.x-lo.x)*x/1500,hi.y-(hi.y-lo.y)*y/1100,lo.z));dire=(c.matrix_world.to_3x3()@local).normalized();origin=c.location.copy()
 for _ in range(15):
  hit,p,no,face,o,mat=sc.ray_cast(deps,origin,dire,distance=100)
  if not hit:break
  if not o.hide_render:rows.append({'pixel':xy,'object':o.name,'point':list(p),'normal':list(no),'face':face});break
  origin=p+dire*.001
(D/'Visible_Artifact_Rays.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2),flush=True)
