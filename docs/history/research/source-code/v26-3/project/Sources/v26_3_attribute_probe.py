from pathlib import Path
import bpy,json
P=Path('E:/jz/JIA/Rebuild_V26_3/Blender/Architecture_Complete_V26_3.blend');bpy.ops.wm.open_mainfile(filepath=str(P))
def walk(nt,seen):
 if nt.name in seen:return
 seen.add(nt.name)
 print('TREE',nt.name,[(n.type,n.name,getattr(n,'attribute_name',None),getattr(n,'uv_map',None))for n in nt.nodes])
 for n in nt.nodes:
  if n.type=='GROUP'and n.node_tree:walk(n.node_tree,seen)
walk(bpy.data.materials['M_V24_20_Continuous_AsBuilt_Perimeter'].node_tree,set())
for g in [bpy.data.materials['M_V24_20_Continuous_AsBuilt_Perimeter'].node_tree]+list(bpy.data.node_groups):
 if not(g.name.startswith(('M_V24_20_Continuous','V26_1_Source_M_V24_20_Continuous'))):continue
 print('GRAPH',g.name,[(n.type,n.name,getattr(n,'attribute_name',None),getattr(n,'layer_name',None))for n in g.nodes if n.type in ['ATTRIBUTE','VERTEX_COLOR','UVMAP']])
for name in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','V26_2_Continuous_Ground_And_Perimeter_Shell']:
 o=bpy.data.objects[name];me=o.data;print('ATTR',name,[(a.name,a.domain,a.data_type)for a in me.attributes]);print('MATRIX',list(o.matrix_world))
 for a in me.attributes:
  if a.name.startswith('V24'):
   print(a.name,'SAMPLE',[(getattr(d,'value',None),tuple(d.vector)if hasattr(d,'vector')else None,tuple(d.color)if hasattr(d,'color')else None)for d in list(a.data)[:4]])
