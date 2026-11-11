import bpy,sys,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_9_views import VIEWS
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V26_9/Blender/Architecture_Complete_V26_9.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.resolution_x=1000;sc.render.resolution_y=820
_,pos,aim,lens=VIEWS[1];c=bpy.data.objects.new('probe',bpy.data.cameras.new('probe'));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;sc.camera=c;bpy.context.view_layer.update();vf=c.data.view_frame(scene=sc);rows=[]
for x,y in [(345,770),(360,768),(360,776),(370,765),(340,754),(352,780),(400,770)]:
 xx=x/1000;yy=y/820;p=vf[3].lerp(vf[0],xx).lerp(vf[2].lerp(vf[1],xx),yy);d=c.matrix_world.to_3x3()@p;d.normalize();hit,loc,no,idx,obj,mat=sc.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,d)
 rows.append({'pixel':[x,y],'object':obj.name if obj else None,'loc':list(loc),'face':idx,'normal':list(no),'material':obj.data.materials[obj.data.polygons[idx].material_index].name if obj and obj.type=='MESH'else None})
(W/'v26_9/Corner_Raycast.json').write_text(json.dumps(rows,indent=2),'utf8');print('CORNER_HITS',json.dumps(rows),flush=True)
