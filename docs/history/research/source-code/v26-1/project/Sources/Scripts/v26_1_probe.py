from pathlib import Path
import bpy,numpy as np,json,sys,hashlib
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_1';D.mkdir(exist_ok=True);sys.path.insert(0,str(W));from v24_06_common import snapshot
P=Path('E:/jz/JIA/Rebuild_V26/Blender/Architecture_Complete_V26.blend');bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8');sc.frame_set(40);bpy.context.view_layer.update();rows=[];exports=[]
for o in bpy.data.objects:
 pts=[o.matrix_world@Vector(p)for p in o.bound_box]if o.type=='MESH'else[];r={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'bounds':[[min(p[k]for p in pts)for k in range(3)],[max(p[k]for p in pts)for k in range(3)]]if pts else None,'hide_render':o.hide_render,'hidden':o.hide_get(),'collections':[c.name for c in o.users_collection],'materials':[m.name if m else None for m in o.data.materials]if o.type=='MESH'else[],'polygons':len(o.data.polygons)if o.type=='MESH'else 0,'props':{k:str(v)for k,v in o.items()}};rows.append(r)
 if o.type!='MESH' or o.hide_render or any(k in o.name for k in ['ORIGINAL_EXTERIOR_','V24_34_MB7_','V24_21_','V24_Gate_Reference_Relief_','V24_Gate_Waist_Carving_']):continue
 if len(o.data.polygons)>100000:continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles],np.float32)if me.uv_layers.active else np.zeros((len(f),3,2),np.float32);fn='SRC_'+str(len(exports))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);exports.append(dict(r,file=fn,triangles=len(f)))
 if len(exports)%100==0:print('EXPORTED',len(exports),o.name,flush=True)
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8');(D/'Geometry_Index.json').write_text(json.dumps(exports,ensure_ascii=False),encoding='utf8')
with P.open('rb')as fp:h=hashlib.file_digest(fp,'sha256').hexdigest()
(D/'Base.json').write_text(json.dumps({'model':str(P),'sha256':h,'blender':bpy.app.version_string,'objects':len(rows),'exports':len(exports)},indent=2),encoding='utf8');print('V26_1_PROBE_DONE',len(exports),sum(r['triangles']for r in exports),h,flush=True)
