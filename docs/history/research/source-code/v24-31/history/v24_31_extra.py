import bpy,json,numpy as np
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_31'
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_30/Blender/Architecture_Complete_V24_30.blend');bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
idx=json.loads((D/'Geometry_Index.json').read_text('utf8'));taken={r['name'] for r in idx};inv={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))}
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render or o.name in taken or o.name.startswith('V24_21_'):continue
 if not any(t in o.name for t in ['HOUSE_V21_','KZ_2_','V24_18_House_Continuous_Grade_Plinth','V24_25_Storage_Entrance','V24_20_Continuous_Graded_Road_Edge','SITE_V15_PERIMETER','SITE_V16_CONTINUOUS']):continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:] for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:] for i in t.loops] for t in me.loop_triangles]) if me.uv_layers.active else np.zeros((len(f),3,2));fn='SRC_'+str(len(idx))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);idx.append(dict(inv[o.name],file=fn,vertices=len(v),triangles=len(f)));print(o.name,inv[o.name]['bounds'],flush=True)
(D/'Geometry_Index.json').write_text(json.dumps(idx,ensure_ascii=False),encoding='utf8')
