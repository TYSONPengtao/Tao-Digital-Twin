import bpy,json,numpy as np
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_37/Blender/Architecture_Complete_V24_37.blend');o=bpy.data.objects['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'];dep=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dep);me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dep)
for tag,m in [('source',o.data),('evaluated',me)]:
 print(tag,'ATTR',[(a.name,a.domain,a.data_type,len(a.data)) for a in m.attributes],flush=True)
 for a in m.attributes:
  if a.data_type in ['FLOAT','INT','BOOLEAN'] and not a.name.startswith('.'):
   vals=[p.value for p in a.data];print(a.name,min(vals),max(vals),sum(vals),flush=True)
print('OBJPROPS',dict(o.items()),flush=True)
for mat in me.materials:
 for n in mat.node_tree.nodes:
  if n.type=='ATTRIBUTE':print('ATTRIBUTE',mat.name,n.attribute_name,n.attribute_type,flush=True)
