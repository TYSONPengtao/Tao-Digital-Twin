import bpy,numpy as np,json
from pathlib import Path
D=Path(__file__).parent/'v24_20';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_17/Blender/Architecture_Complete_V24_17.blend');rows=[]
for i in range(2):
 n=f'SITE_PERIMETER_JOINED_RETAINING_WALL_{i}_Geometry';o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],float);f=np.array([t.vertices[:]for t in me.loop_triangles]);fn=f'Pre18_Wall_{i}.npz';np.savez_compressed(D/fn,v=v,f=f);rows.append({'name':n,'file':fn,'bounds':[v.min(0).tolist(),v.max(0).tolist()]})
(D/'Pre18_Walls.json').write_text(json.dumps(rows,indent=2));print('PRE18_WALLS_EXPORTED',flush=True)
