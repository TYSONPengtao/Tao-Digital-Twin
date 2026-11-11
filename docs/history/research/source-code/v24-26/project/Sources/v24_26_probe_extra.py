import bpy,sys,json,numpy as np
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_26';rows=json.loads((D/'Inventory.json').read_text('utf8'));idx={r['name']:r for r in rows}
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_25/Blender/Architecture_Complete_V24_25.blend');bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
for n in ['V24_20_Two_Rooms_Continuous_Valley_Roof_Bed','SITE_V21_GATE_REFERENCE_LAYER_02_Geometry','SITE_V21_GATE_REFERENCE_LAYER_03_Geometry']:
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],float);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[j].uv[:]for j in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));fn='EXTRA_'+n+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);idx[n]['file']=fn
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');print('V26_EXTRA_COMPLETE',flush=True)
