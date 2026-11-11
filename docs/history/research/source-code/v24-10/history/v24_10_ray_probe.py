import bpy,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_10/Blender/Architecture_Complete_V24_10.blend');sc=bpy.context.scene;sc.frame_set(40);dep=bpy.context.evaluated_depsgraph_get();out=[]
for cn,pts in [('V24_10_Outside',[(1450,700),(1500,800),(1510,900),(1350,760),(1535,640)]),('V24_10_Top',[(1050,180),(1150,310),(1100,255),(1020,330)])]:
 c=bpy.data.objects[cn];proj=c.calc_matrix_camera(dep,x=1600,y=1200,scale_x=1,scale_y=1).inverted()
 for x,y in pts:
  p=proj@Vector((2*x/1600-1,1-2*y/1200,-1,1));p/=p.w;local=Vector(p[:3]);origin=c.matrix_world.translation;direction=c.matrix_world.to_3x3()@local.normalized()
  if c.data.type=='ORTHO':origin=c.matrix_world@local;direction=c.matrix_world.to_3x3()@Vector((0,0,-1))
  hit,loc,no,idx,ob,mat=sc.ray_cast(dep,origin,direction);out.append({'camera':cn,'pixel':[x,y],'object':ob.name if hit else None,'point':list(loc),'material':ob.data.materials[ob.data.polygons[idx].material_index].name if hit and ob.type=='MESH'else None})
(W/'v24_10/Final_Ray_Probe.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out),flush=True)
