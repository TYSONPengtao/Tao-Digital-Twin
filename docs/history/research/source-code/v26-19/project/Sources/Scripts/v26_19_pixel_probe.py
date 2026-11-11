import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_19_views import VIEWS
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V26_18/Blender/Architecture_Complete_V26_18.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
for o in sc.objects:
 if o.type=='MESH'and(o.hide_render or not o.visible_get()):o.hide_viewport=True
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows=[]
for vi,uvs in[(1,[(476,491),(493,483),(525,475),(515,511),(468,515),(550,520)]),(4,[(550,595),(600,590),(620,580),(620,610),(490,625),(510,600)])]:
 tag,pos,aim,lens=VIEWS[vi];pos=Vector(pos);fw=(Vector(aim)-pos).normalized();right=fw.cross(Vector((0,0,1))).normalized();up=right.cross(fw);fp=1100*lens/36
 for u,v in uvs:
  d=(fw+right*((u+.5-550)/fp)+up*((500-v-.5)/fp)).normalized();hit,location,normal,ind,o,_=sc.ray_cast(dg,pos,d,distance=30)
  row={'view':tag,'uv':[u,v],'object':o.name if hit else None,'point':list(location)if hit else None,'normal':list(normal)if hit else None,'material':o.data.materials[o.data.polygons[ind].material_index].name if hit and o.type=='MESH'and ind>=0 else None};rows.append(row);print('PIXEL',row,flush=True)
(W/'v26_19/Pixel_Probe.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
