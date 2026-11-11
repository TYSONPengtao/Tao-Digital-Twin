import bpy,sys,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_9_views import VIEWS
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V26_8/Blender/Architecture_Complete_V26_8.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.resolution_x=1000;sc.render.resolution_y=820
_,pos,aim,lens=VIEWS[14];c=bpy.data.objects.new('probe',bpy.data.cameras.new('probe'));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;sc.camera=c;bpy.context.view_layer.update();vf=c.data.view_frame(scene=sc);rows=[]
for x,y in [(440,401),(480,400),(511,389),(535,375),(400,410),(490,430)]:
 xx=x/1000;yy=1-y/820;p=vf[3].lerp(vf[0],xx).lerp(vf[2].lerp(vf[1],xx),yy);d=c.matrix_world.to_3x3()@p;d.normalize();hit,loc,no,idx,obj,mat=sc.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,d)
 rows.append({'pixel':[x,y],'object':obj.name if obj else None,'loc':list(loc),'face':idx,'normal':list(no),'material':obj.data.materials[obj.data.polygons[idx].material_index].name if obj and obj.type=='MESH'else None})
(W/'v26_9/Fragment_Raycast.json').write_text(json.dumps(rows,indent=2),'utf8');print('FRAGMENT_HITS',json.dumps(rows),flush=True)
