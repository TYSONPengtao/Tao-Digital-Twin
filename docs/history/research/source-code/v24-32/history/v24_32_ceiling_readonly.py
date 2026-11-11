import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_32/Blender/Architecture_Complete_V24_32.blend');sc=bpy.context.scene;sc.frame_set(40);dg=bpy.context.evaluated_depsgraph_get()
for loc in [(8.45,5.5,8.5),(6.,3.5,8.5),(11.,5.,8.5)]:
 ok,q,no,k,o,ma=sc.ray_cast(dg,Vector(loc),Vector((0,0,1)),distance=6)
 if ok:
  p=o.data.polygons[k];print('CEILING',loc,o.name,list(q),o.data.materials[p.material_index].name,flush=True)
