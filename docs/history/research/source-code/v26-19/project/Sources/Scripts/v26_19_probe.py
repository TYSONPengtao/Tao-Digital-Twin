import bpy,sys,json,hashlib,shutil,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as q
D=W/'v26_19';I=D/'Input';I.mkdir(parents=True,exist_ok=True);P=Path('E:/jz/JIA/Rebuild_V26_18/Blender/Architecture_Complete_V26_18.blend')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
mh=sha(P);assert mh==(W/'v26_18/Native_Snapshot_Source_SHA256.txt').read_text('utf8');shutil.copy2(W/'v26_18/Native_After_Snapshot.json',D/'Before_Snapshot.json')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();rows=[]
for o in sc.objects:
 if o.type!='MESH'or not o.visible_get()or o.hide_render or not len(o.data.polygons):continue
 me=o.data;me.calc_loop_triangles();bb=np.asarray([o.matrix_world@Vector(p)for p in o.bound_box]);lo,hi=bb.min(0),bb.max(0);r={'name':o.name,'bounds':[lo.tolist(),hi.tolist()],'triangles':len(me.loop_triangles),'materials':[m.name for m in me.materials],'mesh_hash':q._mesh_hash(me),'matrix':q._matrix(o.matrix_world)}
 select=o.name=='V26_3_House_Connected_Walls_And_Stairs'or o.name.startswith(('CONSTRUCTION_','SITE_PLANTER_','ROMAN_COLUMN_','PORCH_ARCH_','V24_21_Exterior_Stepped_Cornices','V24_22_Porch_Single_Cross_Beams'))
 if select:
  f=np.asarray([t.vertices[:]for t in me.loop_triangles],np.int64);v=q._world(me,o.matrix_world);mi=np.asarray([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.asarray([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));r['file']=o.name+'.npz';np.savez_compressed(I/r['file'],v=v,f=f,mi=mi,uv=uv)
  print('TARGET',o.name,np.round([lo,hi],5).tolist(),r['materials']if len(r['materials'])<8 else['many existing materials'],flush=True)
 rows.append(r)
cams=[{'name':o.name,'matrix':q._matrix(o.matrix_world),'lens':o.data.lens}for o in sc.objects if o.type=='CAMERA'and any(k in o.name for k in['Stair','Head','Jamb','Room','Corner'])]
(I/'Source_Index.json').write_text(json.dumps({'model':str(P),'sha256':mh,'objects':rows,'cameras':cams},ensure_ascii=False,indent=2),'utf8');print('PROBED',len(rows),flush=True)
