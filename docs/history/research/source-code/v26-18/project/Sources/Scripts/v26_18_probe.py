"""Read-only diagnosis of the supplied stair/slab and rear gate annotations."""
import bpy,sys,json,hashlib,shutil,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as q
D=W/'v26_18';I=D/'Input';I.mkdir(parents=True,exist_ok=True)
P=Path('E:/jz/JIA/Rebuild_V26_17/Blender/Architecture_Complete_V26_17.blend')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
mh=sha(P);assert mh==(W/'v26_17/Native_Snapshot_Source_SHA256.txt').read_text('utf8')
shutil.copy2(W/'v26_17/Native_After_Snapshot.json',D/'Before_Snapshot.json')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
regions={'stairs':([3.6,6.8,-.7],[9.5,10.,7.25]),'inner_gate':([5.2,-14.,-.8],[10.,-10.,4.8])};rows=[]
for o in sc.objects:
 if o.type!='MESH'or not o.visible_get()or o.hide_render or not len(o.data.polygons):continue
 bb=np.asarray([o.matrix_world@Vector(v)for v in o.bound_box]);lo,hi=bb.min(0),bb.max(0);hits=[n for n,(a,b)in regions.items()if np.all(hi>=a)and np.all(lo<=b)]
 if not hits:continue
 me=o.data;me.calc_loop_triangles();r={'name':o.name,'bounds':[lo.tolist(),hi.tolist()],'triangles':len(me.loop_triangles),'materials':[m.name for m in me.materials],'regions':hits,'mesh_hash':q._mesh_hash(me),'matrix':q._matrix(o.matrix_world)}
 if o.name in ['V26_3_House_Connected_Walls_And_Stairs','GATE_V22_REAR_FIXED_TIMBER_SIDE_PANELS_Geometry','V26_10_Inner_Gate_Rectangular_Stone_Piers','SITE_V21_GATE_REFERENCE_LAYER_01_Geometry']:
  f=np.asarray([t.vertices[:]for t in me.loop_triangles],np.int64);v=q._world(me,o.matrix_world);mi=np.asarray([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.asarray([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));r['file']=o.name+'.npz';np.savez_compressed(I/r['file'],v=v,f=f,mi=mi,uv=uv)
 rows.append(r)
 if 'REAR_FIXED_TIMBER'in o.name or o.name=='V26_3_House_Connected_Walls_And_Stairs':print('TARGET',r['name'],r['bounds'],r['materials'],flush=True)
cams=[]
for o in sc.objects:
 if o.type=='CAMERA'and any(n in o.name for n in ['Stair','Gate_Rear','Gate_Back','Underside','Stair_Landing']):cams.append({'name':o.name,'matrix':q._matrix(o.matrix_world),'lens':o.data.lens})
(I/'Source_Index.json').write_text(json.dumps({'model':str(P),'sha256':mh,'objects':rows,'cameras':cams,'regions':regions},ensure_ascii=False,indent=2),'utf8')
print('PROBED',len(rows),'cameras',len(cams),flush=True)
