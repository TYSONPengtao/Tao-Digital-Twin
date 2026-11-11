import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as q
from v24_06_common import snapshot
D=W/'v26_20';I=D/'Input';I.mkdir(parents=True,exist_ok=True);P=Path('E:/jz/JIA/Rebuild_V26_19/Blender/Architecture_Complete_V26_19.blend')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
mh=sha(P);assert mh==json.loads(Path('E:/jz/JIA/Rebuild_V26_19/Reports/V26_19_Build.json').read_text('utf8'))['sha256']
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();rows=[]
for o in sc.objects:
 if o.type!='MESH'or not o.visible_get()or o.hide_render or not len(o.data.polygons):continue
 me=o.data;me.calc_loop_triangles();bb=np.asarray([o.matrix_world@Vector(p)for p in o.bound_box]);lo,hi=bb.min(0),bb.max(0);r={'name':o.name,'bounds':[lo.tolist(),hi.tolist()],'triangles':len(me.loop_triangles),'materials':[m.name for m in me.materials],'mesh_hash':q._mesh_hash(me),'matrix':q._matrix(o.matrix_world)}
 if o.name=='V26_2_Continuous_Ground_And_Perimeter_Shell'or('STORAGE'in o.name.upper())or('KITCHEN'in o.name.upper()):
  f=np.asarray([t.vertices[:]for t in me.loop_triangles],np.int64);v=q._world(me,o.matrix_world);mi=np.asarray([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.asarray([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));r['file']=o.name+'.npz';np.savez_compressed(I/r['file'],v=v,f=f,mi=mi,uv=uv)
  if 'FLOOR'in o.name or 'MASONRY'in o.name or o.name.startswith('DOOR_STORAGE'):print('TARGET',o.name,np.round([lo,hi],5).tolist(),flush=True)
 rows.append(r)
(I/'Source_Index.json').write_text(json.dumps({'model':str(P),'sha256':mh,'objects':rows},ensure_ascii=False,indent=2),'utf8')
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),'utf8')
protection={o.name:{'hide_viewport':o.hide_viewport,'hide_render':o.hide_render,'hide_set':o.hide_get(),'modifiers':[(m.name,m.type,m.show_viewport,m.show_render)for m in o.modifiers],'collections':sorted(c.name for c in o.users_collection)}for o in sc.objects if o.type=='MESH'and('KITCHEN'in o.name.upper()or 'MASONRY'in o.name.upper()or'WALL'in o.name.upper())}
(D/'Protected_Object_State.json').write_text(json.dumps(protection,ensure_ascii=False),'utf8');print('PROBED',len(rows),mh,flush=True)
