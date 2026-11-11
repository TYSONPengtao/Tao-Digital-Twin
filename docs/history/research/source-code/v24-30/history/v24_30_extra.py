import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_30';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_29/Blender/Architecture_Complete_V24_29.blend');bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
rows=[]
for n in ['SLAB_JOINED_F1_Geometry','SITE_GAZEBO_FLOOR_Geometry','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry']:
 o=bpy.data.objects.get(n)
 if not o:continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@q.co for q in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);fn='EXTRA_'+str(len(rows))+'.npz';np.savez_compressed(D/fn,v=v,f=f);rows.append({'name':n,'file':fn});print(n,len(v),v.min(0).tolist(),v.max(0).tolist(),flush=True)
(D/'Extra_Index.json').write_text(json.dumps(rows),encoding='utf8')
for n in ['M_V22_Courtyard_Stone_0','M_V22_Courtyard_Filled_Joint','M_V12_Court_Stone']:
 m=bpy.data.materials[n];print('MAT',n,[(a.type,a.name)for a in m.node_tree.nodes],[(l.from_node.type,l.from_socket.name,l.to_node.type,l.to_socket.name)for l in m.node_tree.links],flush=True)
