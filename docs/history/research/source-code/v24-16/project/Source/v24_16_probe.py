import bpy,sys,json,numpy as np
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));D=W/'v24_16';D.mkdir(exist_ok=True)
from v24_06_common import snapshot
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_15/Blender/Architecture_Complete_V24_15.blend')
bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False,indent=2),encoding='utf8')
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 n=o.name
 if not any(s in n for s in ['Screenwall','SCREENWALL','STORAGE','Storage','PERIMETER_JOINED_RETAINING_WALL_0_Geometry','PERIMETER_WHITE_INSIDE','PERIMETER_EAVE_BANDS']):continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[k].uv[:]for k in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2))
 fn='SRC_%03d.npz'%len(rows);np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv)
 rows.append({'name':n,'file':fn,'bounds':[v.min(0).tolist(),v.max(0).tolist()],'vertices':len(v),'faces':len(f),'materials':[m.name if m else None for m in me.materials]})
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:
 if any(s in r['name']for s in ['Screenwall','SCREENWALL','MASONRY','LIMEWASH','Column_','SEALED','Sealed','PERIMETER_WHITE','PERIMETER_JOINED']):print(r,flush=True)
print('EXPORTED',len(rows),flush=True)
