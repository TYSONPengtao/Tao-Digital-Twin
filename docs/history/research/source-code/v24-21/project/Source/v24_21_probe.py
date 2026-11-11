import bpy,json,sys,hashlib,numpy as np
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_21';D.mkdir(exist_ok=True);P=Path('E:/jz/JIA/Rebuild_V24_20/Blender/Architecture_Complete_V24_20.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8');sc.frame_set(40);bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 n=o.name;me=o.data;v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64);row={'name':n,'bounds':[v.min(0).tolist(),v.max(0).tolist()],'vertices':len(v),'polygons':len(me.polygons),'materials':[m.name if m else None for m in me.materials],'parent':o.parent.name if o.parent else None,'matrix':list(map(list,o.matrix_world)),'hide_render':o.hide_render,'hide_viewport':o.hide_viewport,'visible':o.visible_get()}
 if any(k in n for k in ['PERIMETER_JOINED_RETAINING_WALL','PERIMETER_EAVE_BANDS','STAIR','SLAB_JOINED']):
  me.calc_loop_triangles();f=np.array([t.vertices[:]for t in me.loop_triangles]);fn=f'SRC_{len(rows):04d}.npz';np.savez_compressed(D/fn,v=v,f=f);row['file']=fn
 rows.append(row)
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Source.json').write_text(json.dumps({'model':str(P),'sha256':h},indent=2))
print('TOTAL',len(rows),'POLYGONS',sum(r['polygons']for r in rows),flush=True)
for r in sorted(rows,key=lambda r:-r['polygons'])[:18]:print('HEAVY',r['name'],r['polygons'],r['bounds'],flush=True)
print('PROBE_DONE',h,flush=True)
