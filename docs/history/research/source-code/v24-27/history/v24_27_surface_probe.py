import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_27/Blender/Architecture_Complete_V24_27.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();cam=bpy.data.objects['V24_27_House_Step_From_Kitchen'];dep=bpy.context.evaluated_depsgraph_get();inv=cam.calc_matrix_camera(dep,x=1120,y=800).inverted();out=[]
obs=[o for o in bpy.data.objects if o.type=='MESH'and not o.hide_render and any(k in o.name for k in ['COURT','Court','Paving','STONE_FLOOR'])]
for px,py in [(465,735),(480,685),(500,650),(530,620),(555,590),(570,565),(580,550)]:
 p=inv@Vector((2*px/1120-1,1-2*py/800,-1,1));p/=p.w;direction=(cam.matrix_world.to_3x3()@Vector(p[:3])).normalized();hits=[]
 for o in obs:
  iv=o.matrix_world.inverted();origin=iv@cam.location;dv=(iv.to_3x3()@direction).normalized();hit,loc,no,face=o.ray_cast(origin,dv)
  if hit:
   q=o.matrix_world@loc;dis=(q-cam.location).length
   if dis<20:hits.append({'object':o.name,'point':list(q),'distance':dis,'face':face})
 hits.sort(key=lambda r:r['distance']);out.append({'pixel':[px,py],'hits':hits[:4]})
print(json.dumps(out,ensure_ascii=False,indent=2),flush=True)
