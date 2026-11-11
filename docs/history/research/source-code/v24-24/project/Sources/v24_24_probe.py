import bpy,json,sys,hashlib,numpy as np
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_24';D.mkdir(exist_ok=True);P=Path('E:/jz/JIA/Rebuild_V24_23/Blender/Architecture_Complete_V24_23.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8');sc.frame_set(40);bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 n=o.name;me=o.data;v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64)
 row={'name':n,'bounds':[v.min(0).tolist(),v.max(0).tolist()],'vertices':len(v),'polygons':len(me.polygons),'materials':[m.name if m else None for m in me.materials],'parent':o.parent.name if o.parent else None,'matrix':list(map(list,o.matrix_world)),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport}
 take=any(k in n.upper()for k in ['KITCHEN','STORAGE','GATE','V24_22_','V24_23_','COURT','FLOOR','GALLERY','PAVEMENT','THRESHOLD','HOUSE_V24','BAY','PLINTH'])and not any(k in n.upper()for k in ['UNIFIED_PAN_BARREL','INDIVIDUAL_TILE_COURSES','NAVIGATION','OLD_REFERENCE','_WALL_V10_','_BRICKS','_FASCIA_'])
 if take:
  me.calc_loop_triangles();f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[j].uv[:]for j in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));fn=f'SRC_{len(rows):04d}.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);row['file']=fn
 rows.append(row)
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Source.json').write_text(json.dumps({'model':str(P),'sha256':h},indent=2),encoding='utf8')
print('V24_PROBE_COMPLETE',len(rows),h,flush=True)
