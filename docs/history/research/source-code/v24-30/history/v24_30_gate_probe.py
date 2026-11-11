import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_30';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_29/Blender/Architecture_Complete_V24_29.blend');rows=[];allp=[]
for frame in range(1,41,2):
 bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();pts=[]
 for i in [1,2]:
  o=bpy.data.objects[f'SITE_SW_METAL_ENTRY_GATE_V11__LEAF_{i}_Geometry'];v=np.array([o.matrix_world@q.co for q in o.data.vertices]);p=v[v[:,2]<-.58];pts.extend(p.tolist());allp.extend(p.tolist())
 p=np.array(pts);rows.append({'frame':frame,'bounds':[p.min(0).tolist(),p.max(0).tolist()]})
(D/'Gate_Sweep.json').write_text(json.dumps(rows),encoding='utf8');np.savez_compressed(D/'Gate_Sweep.npz',v=np.array(allp));print(json.dumps(rows),flush=True)
