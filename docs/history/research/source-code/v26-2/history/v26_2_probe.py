from pathlib import Path
import bpy,numpy as np,json,sys,hashlib
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_2';D.mkdir(exist_ok=True);sys.path.insert(0,str(W))
from v24_06_common import snapshot
P=Path('E:/jz/JIA/Rebuild_V26_1/Blender/Architecture_Complete_V26_1.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8')
sc.frame_set(40);bpy.context.view_layer.update();rows=[];exports=[]
for o in bpy.data.objects:
 pts=[o.matrix_world@Vector(p)for p in o.bound_box]if o.type=='MESH'and len(o.data.vertices)else[]
 r={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'bounds':[[min(p[k]for p in pts)for k in range(3)],[max(p[k]for p in pts)for k in range(3)]]if pts else None,'hide_render':o.hide_render,'hidden':o.hide_get(),'collections':[c.name for c in o.users_collection],'materials':[m.name if m else None for m in o.data.materials]if o.type=='MESH'else[],'polygons':len(o.data.polygons)if o.type=='MESH'else 0,'props':{k:str(v)for k,v in o.items()},'location':list(o.location),'rotation':list(o.rotation_euler),'matrix_world':[list(p)for p in o.matrix_world]}
 rows.append(r)
 if o.type!='MESH' or not len(o.data.polygons) or o.hide_render or any(c.hide_render for c in o.users_collection):continue
 if any(k in o.name for k in ['ORIGINAL_EXTERIOR_','V24_34_MB7_','Navigation_Collision','Avatar_','Roam_Person','V24_Gate_Reference_Relief_','V24_Gate_Waist_Carving_']):continue
 if len(o.data.polygons)>500000:continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32)
 uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles],np.float32)if me.uv_layers.active else np.zeros((len(f),3,2),np.float32)
 fn='SRC_'+str(len(exports))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);exports.append(dict(r,file=fn,triangles=len(f),attributes=[{'name':a.name,'domain':a.domain,'type':a.data_type}for a in me.attributes]))
 if len(exports)%100==0:print('EXPORTED',len(exports),o.name,flush=True)
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8');(D/'Geometry_Index.json').write_text(json.dumps(exports,ensure_ascii=False),encoding='utf8')
poses={}
for frame in [1,20,40]:
 sc.frame_set(frame);bpy.context.view_layer.update();poses[str(frame)]={}
 for o in bpy.data.objects:
  if o.type=='MESH'and o.name.startswith('DOOR_'):
   poses[str(frame)][o.name]={'matrix':[list(v)for v in o.matrix_world],'bounds':[[min((o.matrix_world@Vector(p))[k]for p in o.bound_box)for k in range(3)],[max((o.matrix_world@Vector(p))[k]for p in o.bound_box)for k in range(3)]]}
(D/'Door_Poses.json').write_text(json.dumps(poses,ensure_ascii=False),encoding='utf8')
with P.open('rb')as fp:h=hashlib.file_digest(fp,'sha256').hexdigest()
(D/'Base.json').write_text(json.dumps({'model':str(P),'sha256':h,'blender':bpy.app.version_string,'objects':len(rows),'exports':len(exports)},indent=2),encoding='utf8');print('V26_2_PROBE_DONE',len(exports),sum(r['triangles']for r in exports),h,flush=True)
