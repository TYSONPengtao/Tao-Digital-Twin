import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_22/Blender/Architecture_Complete_V24_22.blend')
o=bpy.data.objects['SITE_V16_GRADED_INTERIOR_SOIL_Geometry'];me=o.data;me.calc_loop_triangles();b=BVHTree.FromPolygons([o.matrix_world@v.co for v in me.vertices],[t.vertices[:]for t in me.loop_triangles],all_triangles=True)
a=[]
for y in [-15.24,-14.85,-14.18,-13.,-12.,-11.6]:
 h,loc,no,i,o,m=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((12.9,y,1)),Vector((0,0,-1)),distance=8)
 a.append([y,loc.z if h else None,o.name if o else None])
Path('C:/Users/PENG/Documents/Codex/2026-10-07/files-pasted-by-the-user-rhino/work/v24_23/Ground_Grade_Scene.json').write_text(json.dumps(a));print(a,flush=True)
