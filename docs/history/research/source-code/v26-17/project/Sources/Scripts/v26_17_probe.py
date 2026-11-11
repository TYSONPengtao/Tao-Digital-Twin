"""Read the saved V26.16, export facade solids and the complete preservation snapshot."""
import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as q
from v24_06_common import snapshot
D=W/'v26_17';I=D/'Input';I.mkdir(parents=True,exist_ok=True)
P=Path('E:/jz/JIA/Rebuild_V26_16/Blender/Architecture_Complete_V26_16.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();rows=[]
regions={'front_left':([-.5,.5,-.61],[4.5,2.8,7.2]),'front_right':([8.5,.5,-.61],[13.5,2.8,10.6])}
for o in sc.objects:
 if o.type!='MESH'or not len(o.data.polygons)or o.hide_render or not o.visible_get():continue
 bb=np.asarray([o.matrix_world@Vector(p)for p in o.bound_box]);lo,hi=bb.min(0),bb.max(0);hits=[label for label,(a,b)in regions.items()if np.all(hi>=a)and np.all(lo<=b)]
 if not hits:continue
 me=o.data;me.calc_loop_triangles();row={'name':o.name,'regions':hits,'bounds':[lo.tolist(),hi.tolist()],'triangles':len(me.loop_triangles),'materials':[m.name for m in me.materials],'matrix':q._matrix(o.matrix_world),'mesh_hash':q._mesh_hash(me),'modifiers':[m.type for m in o.modifiers]}
 if not any(k in o.name for k in['ORIGINAL_EXTERIOR','V24_34_MB7','Roam_Person','Avatar_','Navigation_Collision'])and len(me.loop_triangles)<400000:
  v=q._world(me,o.matrix_world);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int64);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));fn='Source_'+o.name+'.npz';np.savez_compressed(I/fn,v=v,f=f,mi=mi,uv=uv);row['file']=fn
 rows.append(row)
(I/'Source_Index.json').write_text(json.dumps({'model':str(P),'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'objects':rows,'regions':regions},ensure_ascii=False,indent=2),'utf8')
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')
for r in rows:
 if any(k in r['name']for k in['BAY_WINDOW','House_Connected','BALCONY_EDGE','Porch','PORCH','DOOR','SLAB']):print('OBJECT',r['name'],r['triangles'],np.round(r['bounds'],5).tolist(),flush=True)
print('PROBED',len(rows),flush=True)
