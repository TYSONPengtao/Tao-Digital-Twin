import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as q
D=W/'v26_14';D.mkdir(exist_ok=True);P=Path('E:/jz/JIA/Rebuild_V26_13/Blender/Architecture_Complete_V26_13.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
rows=[]
for o in sc.objects:
 if o.type!='MESH'or not len(o.data.polygons)or o.hide_render or not o.visible_get():continue
 pts=np.asarray([o.matrix_world@__import__('mathutils').Vector(v)for v in o.bound_box]);lo=pts.min(0);hi=pts.max(0)
 if np.any(hi<[0,6.6,-.6])or np.any(lo>[13.1,10.6,10.5]):continue
 me=o.data;me.calc_loop_triangles();r={'name':o.name,'bounds':[lo.tolist(),hi.tolist()],'triangles':len(me.loop_triangles),'materials':[m.name for m in me.materials],'matrix':q._matrix(o.matrix_world),'mesh_hash':q._mesh_hash(me)}
 if o.name=='V26_3_House_Connected_Walls_And_Stairs'or o.name.startswith(('DOOR_BATH_','DOOR_BED_','DOOR_KITCHEN_F1','DOOR_STUDY_')):
  v=q._world(me,o.matrix_world);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);fn='Source_'+o.name+'.npz';np.savez_compressed(D/fn,v=v,f=f,uv=uv,mi=mi);r['file']=fn
 rows.append(r)
out={'model':str(P),'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'objects':rows}
(D/'Source_Index.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
print('PROBE_SAVED',len(rows),flush=True)
for r in rows:
 if r['name'].startswith(('COLUMN','V26_3_','V26_9_','DOOR_BATH_')):print(r['name'],r['bounds'],flush=True)
