import bpy,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_33';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_32/Blender/Architecture_Complete_V24_32.blend');sc=bpy.context.scene;sc.frame_set(40);dg=bpy.context.evaluated_depsgraph_get();out=[]
def ray(tag,origin,direction):
 hit,p,n,fi,o,ma=sc.ray_cast(dg,Vector(origin),Vector(direction),distance=20)
 row={'tag':tag,'origin':origin,'hit':bool(hit),'point':list(p) if hit else None,'normal':list(n) if hit else None,'object':o.name if hit else None,'material':o.data.materials[o.data.polygons[fi].material_index].name if hit and fi>=0 and o.data.materials else None};out.append(row);print(row,flush=True)
for fl,z in [(2,3.4500244140625),(3,7.05)]:
 for x in [3.65,3.78,3.85,3.92,3.99,4.03,4.15]:ray('F%d_TERRACE_THRESH'%fl,(x,6.4,z+.2),(0,0,-1))
 for y in [7.12,7.19,7.21,7.26,7.29,7.31,7.35,7.39,7.41]:ray('F%d_FRONT_EDGE'%fl,(6.,y,z+.2),(0,0,-1))
for y in [1.12,1.3,3.,6.6,7.25]:ray('TERRACE_FLOOR',(1.7,y,7.3),(0,0,-1))
# Identify the visible roof tile intrusion from the matching terrace view.
loc=Vector((1.7,7.,8.55));aim=Vector((1.7,2.,7.7));q=(aim-loc).to_track_quat('-Z','Y');c=bpy.data.cameras.new('Probe');ob=bpy.data.objects.new('Probe',c);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=q.to_euler();c.lens=20;sc.render.resolution_x=960;sc.render.resolution_y=800;fr=c.view_frame(scene=sc);xl=min(v.x for v in fr);xh=max(v.x for v in fr);yl=min(v.y for v in fr);yh=max(v.y for v in fr);bpy.context.view_layer.update()
for px,py in [(300,445),(285,460),(320,455)]:
 local=Vector((xl+(xh-xl)*px/960,yh-(yh-yl)*py/800,fr[0].z));ray('TERRACE_TILE_INTRUSION',list(loc),list((ob.matrix_world.to_3x3()@local).normalized()))
(D/'Floor_Probes_Before.json').write_text(json.dumps(out,indent=2),encoding='utf8')
