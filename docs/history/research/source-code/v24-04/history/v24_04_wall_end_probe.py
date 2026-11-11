import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_04/Blender/Architecture_Complete_V24_04.blend')
for n in ['SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_0_TILE_COPING_Geometry']:
 ob=bpy.data.objects[n];p=sorted(set(tuple(round(c,4)for c in ob.matrix_world@v.co)for v in ob.data.vertices));p=[q for q in p if 13.5<q[0]<15 and -3.4<q[1]<-1.4];print('ENDPOINT',n,json.dumps(p),flush=True)
for n in ['SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS_Geometry','SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS_Geometry']:
 o=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8)
 for e in bm.edges:
  if e.is_boundary:print('BOUNDARY',n,[tuple(o.matrix_world@v.co)for v in e.verts],[(f.calc_area(),len(f.verts))for f in e.link_faces],flush=True)
 bm.free()
