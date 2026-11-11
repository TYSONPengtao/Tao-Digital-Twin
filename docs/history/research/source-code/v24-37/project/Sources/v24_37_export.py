from pathlib import Path
import bpy,sys,json,hashlib,time,numpy as np
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_06_common import snapshot
D=W/'v24_37';(D/'Source').mkdir(parents=True,exist_ok=True)
P=Path('E:/jz/JIA/Rebuild_V24_36/Blender/Architecture_Complete_V24_36.blend')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
(D/'Source.json').write_text(json.dumps({'model':str(P),'sha256':sha(P)}))
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8')
rows=[];start=time.perf_counter()
for o in list(bpy.data.objects):
 if o.type!='MESH'or o.hide_render or not('ORIGINAL_EXTERIOR_'in o.name or o.name.startswith(('V24_34_MB7_','V24_36_PTJIA6_'))):continue
 me=o.data;me.calc_loop_triangles();v=np.empty(len(me.vertices)*3,np.float64);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);M=np.array(o.matrix_world);v=v@M[:3,:3].T+M[:3,3]
 f=np.empty(len(me.loop_triangles)*3,np.int32);me.loop_triangles.foreach_get('vertices',f);f=f.reshape(-1,3)
 loops=np.empty(len(me.loop_triangles)*3,np.int32);me.loop_triangles.foreach_get('loops',loops);loops=loops.reshape(-1,3)
 mi=np.array([t.material_index for t in me.loop_triangles],np.int32);uv=np.zeros((len(f),3,2))
 if me.uv_layers.active:
  u=np.empty(len(me.loops)*2,np.float64);me.uv_layers.active.data.foreach_get('uv',u);uv=u.reshape(-1,2)[loops]
 fn='Source/'+str(len(rows)).zfill(4)+'.npz';np.savez_compressed(D/fn,v=v,f=f,uv=uv,mi=mi)
 rows.append({'name':o.name,'file':fn,'vertices':len(v),'triangles':len(f),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'matrix':M.tolist(),'materials':[m.name if m else None for m in me.materials],'has_uv':bool(me.uv_layers.active),'uv_name':me.uv_layers.active.name if me.uv_layers.active else ''})
 if len(rows)%200==0:print('EXPORTED_SCAN',len(rows),'seconds',time.perf_counter()-start,flush=True)
(D/'Source_Scan_Index.json').write_text(json.dumps(rows,indent=2));print('EXPORT_DONE',len(rows),sum(r['triangles']for r in rows),flush=True)
