import bpy,numpy as np,json
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_28'
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_26/Blender/Architecture_Complete_V24_26.blend')
bpy.context.scene.frame_set(40);bpy.context.view_layer.update();rows=[]
for n in ['V24_22_North_Verge','V24_22_North_Verge_Bead','V24_21_Exterior_Continuous_White_Frieze','V24_21_Exterior_Stepped_Cornices']:
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles()
 v=np.array([o.matrix_world@p.co for p in me.vertices],float);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[j].uv[:]for j in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2))
 fn='EXTRA_'+n+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);rows.append({'name':n,'file':str((D/fn).resolve())})
(D/'Extra_Files.json').write_text(json.dumps(rows),encoding='utf8');print('EXTRAS_SAVED',len(rows),flush=True)
