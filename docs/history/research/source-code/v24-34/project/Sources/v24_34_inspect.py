import bpy,json,numpy as np,hashlib,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_34';D.mkdir(exist_ok=True);sys.path.insert(0,str(W));from v24_06_common import snapshot
P=Path('E:/jz/JIA/Rebuild_V24_33/Blender/Architecture_Complete_V24_33.blend');bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;before=snapshot(bpy);(D/'Before_Snapshot.json').write_text(json.dumps(before,ensure_ascii=False),encoding='utf8');sc.frame_set(40);bpy.context.view_layer.update();rows=[];exports=[]
terms=['ORIGINAL_EXTERIOR','GROUND','SOIL','ROAD','PAD','RUNNING_BOND','JOINT_BASE','FLOOR','SLAB_JOINED','FACADE_CONTINUOUS','STAIR_F','PARTITIONS_JOINED','CONNECTED_KITCHEN_STORAGE_MASONRY','STORAGE_STONE_BASE','Navigation_Collision','ROOF_MAIN','CURB','CONTINUOUS_STORAGE_STONE_GUARD']
for o in bpy.data.objects:
 pts=[o.matrix_world@Vector(p)for p in o.bound_box] if o.type=='MESH' else [];row={'name':o.name,'type':o.type,'matrix':[list(r)for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'hide_render':o.hide_render,'collections':[c.name for c in o.users_collection],'bounds':[[min(p[k]for p in pts)for k in range(3)],[max(p[k]for p in pts)for k in range(3)]] if pts else None,'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'props':{k:str(v)for k,v in o.items()}};rows.append(row)
 if o.type!='MESH' or (o.hide_render and o.name!='V24_21_Navigation_Collision') or not any(t.upper() in o.name.upper() for t in terms):continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles],dtype=np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles]) if me.uv_layers.active else np.zeros((len(f),3,2));fn='SRC_'+str(len(exports))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);exports.append(dict(row,file=fn,vertices=len(v),triangles=len(f)))
 if 'ORIGINAL_EXTERIOR' in o.name:print('CONTEXT',o.name,len(v),len(f),row['bounds'],flush=True)
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8');(D/'Geometry_Index.json').write_text(json.dumps(exports,ensure_ascii=False),encoding='utf8')
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Source.json').write_text(json.dumps({'model':str(P),'sha256':h}),encoding='utf8');print('BASELINE_EXPORTED',len(rows),len(exports),flush=True)
