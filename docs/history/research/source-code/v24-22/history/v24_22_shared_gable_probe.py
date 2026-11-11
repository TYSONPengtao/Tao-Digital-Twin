import bpy,json,numpy as np
from pathlib import Path
D=Path(__file__).parent/'v24_22';bpy.ops.wm.open_mainfile(filepath=json.loads((D/'Source.json').read_text())['model']);bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
n='V24_14_Storage_West_Sealed_Gable';o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[j].uv[:]for j in t.loops]for t in me.loop_triangles]);fn='SRC_Shared_Gable.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv)
rows=json.loads((D/'Inventory.json').read_text(encoding='utf8'))
for row in rows:
 if row['name']==n:row['file']=fn
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print('SHARED_GABLE_EXPORTED',flush=True)
