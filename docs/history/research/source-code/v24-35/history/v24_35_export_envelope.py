from pathlib import Path
import bpy,json,numpy as np
W=Path(__file__).parent;D=W/'v24_35';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_34/Blender/Architecture_Complete_V24_34.blend');bpy.context.scene.frame_set(40);bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type!='MESH'or o.hide_render or o.name.startswith('V24_34_MB7_'):continue
 n=o.name.upper();roof=('KITCHEN'in n or'STORAGE'in n)and any(k in n for k in ['ROOF','PAN_BARREL','INDIVIDUAL_TILE_COURSES','UNIFIED_PAN','WOOD_BOARDING','VISIBLE_SHEATHING'])
 wall=('COURTYARD_WALL'in n or'PERIMETER_WALL'in n or'CONTINUOUS_PERIMETER'in n or'WALL_FACE'in n)
 if not(roof or wall):continue
 me=o.data;me.calc_loop_triangles();v=np.array([tuple(o.matrix_world@q.co)for q in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);fn='ENVELOPE_'+str(len(rows))+'.npz';np.savez_compressed(D/fn,v=v,f=f);rows.append({'name':o.name,'file':fn,'roof':roof,'wall':wall})
(D/'Envelope_Index.json').write_text(json.dumps(rows,indent=2));print('ENVELOPE_OBJECTS',len(rows),flush=True)
