import bpy,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_29/Blender/Architecture_Complete_V24_29.blend');sc=bpy.context.scene;sc.frame_set(40)
for o in sc.objects:
 if o.hide_render:o.hide_set(True)
sc.render.resolution_x=1600;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
c=bpy.data.objects['V24_29_Courtyard_Flush'];f=c.data.view_frame(scene=sc);x0=min(p.x for p in f);x1=max(p.x for p in f);y0=min(p.y for p in f);y1=max(p.y for p in f)
dg=bpy.context.evaluated_depsgraph_get()
for x,y in [(650,1060),(800,1010),(400,1060),(700,1000),(650,990),(300,1070),(100,1070),(950,970),(1050,1000)]:
 p=Vector((x0+(x1-x0)*(x+.5)/1600,y0+(y1-y0)*(1-(y+.5)/1100),f[0].z));d=c.matrix_world.to_3x3()@p.normalized();hit,loc,no,face,o,m=sc.ray_cast(dg,c.location,d,distance=100.)
 print('PIXEL',x,y,o.name if hit else None,[round(q,6)for q in loc],list(no),o.data.materials[o.data.polygons[face].material_index].name if hit and o.type=='MESH' and 0<=face<len(o.data.polygons)and o.data.materials else None,flush=True)
