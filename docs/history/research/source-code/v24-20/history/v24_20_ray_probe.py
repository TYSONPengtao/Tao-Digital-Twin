import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_20/Blender/Architecture_Complete_V24_20.blend');s=bpy.context.scene;s.frame_set(40);dg=bpy.context.evaluated_depsgraph_get()
for x,y in [(12,5),(11,3),(10,6),(9,7),(8,5),(5,5)]:
 h=s.ray_cast(dg,Vector((x,y,16)),Vector((0,0,-1)),distance=8);print('RAY',x,y,h[0],h[1][:],h[4].name if h[0]else None,flush=True)
for n in ['V24_20_House_Unified_Pan_Barrel_Slope_1','ROOF_MAIN_JOINED_Geometry']:
 o=bpy.data.objects[n];print('OBJ',n,o.hide_render,o.matrix_world[:],flush=True)
for y in [-8.,-6.,-4.]:
 edge=13.245+(y+8.276)*(.714/4.994)
 for x in np.arange(edge-.25,edge+.09,.05)if False else[edge-.18,edge-.12,edge-.06,edge,edge+.05]:
  h=s.ray_cast(dg,Vector((x,y,.2)),Vector((0,0,-1)),distance=2)
  if h[0]:
   o=h[4];f=o.data.polygons[h[3]];m=o.data.materials[f.material_index];print('FOOT',round(x,4),y,list(h[1]),o.name,m.name,list(f.normal),list(f.center),flush=True)
