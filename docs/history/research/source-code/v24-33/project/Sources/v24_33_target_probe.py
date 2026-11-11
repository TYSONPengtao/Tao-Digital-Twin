import bpy,json,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_33';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_32/Blender/Architecture_Complete_V24_32.blend');sc=bpy.context.scene;sc.frame_set(40);dg=bpy.context.evaluated_depsgraph_get();out=[]
def ray(tag,ori,di):
 h,p,n,fi,o,ma=sc.ray_cast(dg,Vector(ori),Vector(di),distance=30);r={'tag':tag,'origin':list(ori),'hit':bool(h),'point':list(p) if h else None,'normal':list(n) if h else None,'face':int(fi),'object':o.name if h else None,'material':o.data.materials[o.data.polygons[fi].material_index].name if h and fi>=0 and o.data.materials else None};out.append(r);print(r,flush=True)
views=json.loads((D/'Target_Diagnostic_Views.json').read_text('utf8'))
for tag,pos,aim,lens in views:
 if not tag.startswith('Storage'):continue
 c=bpy.data.cameras.new(tag);ob=bpy.data.objects.new(tag,c);sc.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(aim)-ob.location).to_track_quat('-Z','Y').to_euler();c.lens=lens;sc.render.resolution_x=960;sc.render.resolution_y=800;fr=c.view_frame(scene=sc);xl=min(v.x for v in fr);xh=max(v.x for v in fr);yl=min(v.y for v in fr);yh=max(v.y for v in fr);bpy.context.view_layer.update()
 pixels=[(750,400),(480,400),(330,650),(530,500)] if 'Gap'in tag else [(400,560),(400,700),(500,600),(500,550),(400,300),(320,200)]
 for px,py in pixels:
  local=Vector((xl+(xh-xl)*px/960,yh-(yh-yl)*py/800,fr[0].z));ray(tag+f'_{px}_{py}',pos,(ob.matrix_world.to_3x3()@local).normalized())
for ob in bpy.data.objects:
 if ob.type!='MESH' or not ob.name.endswith('__FRAME_Geometry'):continue
 pts=[ob.matrix_world@Vector(p) for p in ob.bound_box];lo=[min(v[k] for v in pts) for k in range(3)];hi=[max(v[k] for v in pts) for k in range(3)];cx=(lo[0]+hi[0])/2;cy=(lo[1]+hi[1])/2;z=lo[2]
 if 0<cx<13 and 0<cy<10:
  for delta in [-.15,0,.15]:ray('DOOR_FLOOR_'+ob.name,(cx+delta if hi[0]-lo[0]<hi[1]-lo[1] else cx,cy if hi[0]-lo[0]<hi[1]-lo[1] else cy+delta,z+.12),(0,0,-1))
(D/'Target_Probes_Before.json').write_text(json.dumps(out,indent=2),encoding='utf8')
