import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_19';D.mkdir(exist_ok=True)
P=Path('E:/jz/JIA/Rebuild_V24_18/Blender/Architecture_Complete_V24_18.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8')
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 n=o.name;me=o.data;v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64)
 take=any(k in n for k in ['Gable','Sealed_Gable','Inner_Gable','Storage_RIDGE','Storage_Ridge','INNER_STORAGE_GABLE_ROOF','INNER_STORAGE_INDIVIDUAL_TILE','INNER_STORAGE_RIDGE','KITCHEN_CHINESE_TILE_ROOF','GRADED_INTERIOR_SOIL','REBUILT_COURT','SLAB_JOINED_F1','ENTRY_STEP_AND_PORCH','V24_XIESHAN_','Continuous_Grade_Plinth'])
 if not take:continue
 me.calc_loop_triangles();f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[k].uv[:]for k in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));fn=f'SRC_{len(rows):03d}.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv)
 row={'name':n,'file':fn,'materials':[m.name for m in me.materials],'bounds':[v.min(0).tolist(),v.max(0).tolist()]};rows.append(row);print(n,row['bounds'],flush=True)
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Source.json').write_text(json.dumps({'model':str(P),'sha256':h},indent=2),encoding='utf8')
print('V19_PROBE_COMPLETE',len(rows),flush=True)
