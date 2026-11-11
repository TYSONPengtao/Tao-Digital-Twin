import bpy,json
from pathlib import Path
W=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_37/Blender/Architecture_Complete_V24_37.blend');sc=bpy.context.scene;sc.frame_set(40);rows=[]
for o in sc.objects:
 if o.type!='MESH' or o.hide_render:continue
 d=[m.name if m else None for m in o.data.materials];a=[s.material.name if s.material else None for s in o.material_slots]
 if d!=a:rows.append({'object':o.name,'data':d,'effective':a,'link':[s.link for s in o.material_slots]})
(W/'v25/Object_Material_Overrides.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');print('EFFECTIVE_OVERRIDES',len(rows),flush=True)
for row in rows:print(json.dumps(row,ensure_ascii=False),flush=True)
m=bpy.data.materials['M_V24_18_Continuous_Blue_Brick'];print('BRICK_NODES',[(n.type,n.name)for n in m.node_tree.nodes],flush=True);print('BRICK_LINKS',[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in m.node_tree.links],flush=True)
