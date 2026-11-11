import bpy,sys,json,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_16';P=Path('E:/jz/JIA/Rebuild_V26_16/Blender/Architecture_Complete_V26_16.blend');bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();cam=bpy.data.objects.new('Probe',bpy.data.cameras.new('Probe'));sc.collection.objects.link(cam);cam.location=(10.7,3.,1.95);cam.rotation_euler=(Vector((9.2,2.05,3.12))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=34;sc.camera=cam;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();M=(cam.calc_matrix_camera(deps,x=1000,y=1100)@cam.matrix_world.inverted()).inverted();out=[]
for x,y in[(540,441),(550,431),(525,420),(540,455),(600,390),(680,480),(450,530),(550,510),(500,400)]:
 p=M@Vector((x/500-1,1-y/550,1,1));p=p.xyz/p.w;ray=(p-cam.location).normalized();yes,pos,no,index,ob,mat=sc.ray_cast(deps,cam.location,ray);out.append({'pixel':[x,y],'object':ob.name if yes else None,'position':list(pos),'normal':list(no),'face':index,'material':ob.data.materials[ob.data.polygons[index].material_index].name if yes and index>=0 else None})
(D/'Visible_Head_Pixel_Probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('VISIBLE_PIXEL_PROBE',out,flush=True)
