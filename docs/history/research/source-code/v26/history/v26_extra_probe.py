from pathlib import Path
import bpy,numpy as np,json
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26'
I=json.loads((D/'Geometry_Index.json').read_text('utf8')); seen={r['name'] for r in I}
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_34/Blender/Architecture_Complete_V24_34.blend');bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render or o.name in seen:continue
 lineage=' '.join([o.name]+[a.name for a in [o.parent] if a])
 if not any(s in lineage for s in ['ORIGINAL_EXTERIOR','SCORED_CONCRETE_RAMP','Swing_Clearance','WHITE_INSIDE_FINISH','ROOF_MAIN','FLOOR_FASCIA','Continuous_Gray_Road_And_Storage_Approach','Individual_Roadside_Curb','Graded_Approach','Gate_Swing']):continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],np.float64);f=np.array([t.vertices[:] for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32)
 uv=np.array([[me.uv_layers.active.data[l].uv[:] for l in t.loops] for t in me.loop_triangles],np.float32) if me.uv_layers.active else np.zeros((len(f),3,2),np.float32)
 fn='EXTRA_'+str(len(I))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv)
 row={'name':o.name,'file':fn,'materials':[m.name for m in me.materials],'bounds':[v.min(0).tolist(),v.max(0).tolist()],'triangles':len(f),'parent':o.parent.name if o.parent else None};I.append(row);print(row,flush=True)
(D/'Geometry_Index.json').write_text(json.dumps(I,ensure_ascii=False),encoding='utf8')
