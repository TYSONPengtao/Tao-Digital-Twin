"""Read the saved native gate carvings, rigid transforms, light and leaf poses."""
import bpy,json,numpy as np,hashlib,sys
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));import v24_qa_blender as q
D=W/'v26_10';FD=D/'Final';O=Path('E:/jz/JIA/Rebuild_V26_10');P=O/'Blender/Architecture_Complete_V26_10.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
checks=[];before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));ch=json.loads((O/'Reports/V26_10_Changes.json').read_text('utf8'))
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('NATIVE_SPECIFIC',n,bool(p),kw if not p else'',flush=True)
carved=[n for n in before['objects']if n.startswith(('V24_Gate_Reference_Relief_','V24_Gate_Waist_Carving_'))];bad=[]
for n in carved:
 o=bpy.data.objects[n]
 if q._mesh_hash(o.data)!=before['objects'][n]['mesh_hash'] or o.hide_render or o.hide_get():bad.append(n)
ck('Every original stone picture retains exact native vertices, UV, material, smoothing and visible state',not bad,original_sculpted_objects=len(carved),invalid=bad)
rigid={r['name']:r for r in ch['rigid_transforms']};bad=[]
for n in carved:
 old=np.asarray(before['objects'][n]['matrix']);want=np.asarray(rigid[n]['matrix_world_left_multiply'])@old if n in rigid else old
 if np.max(abs(np.asarray(bpy.data.objects[n].matrix_world)-want))>2e-6:bad.append(n)
ck('Front, waist and header pictures stay in place; eight side pictures move rigidly without stretching',not bad and len(rigid)==8,rigid_side_pictures=len(rigid),invalid=bad)
reliefs=[bpy.data.objects[n]for n in ch['added']if 'Upper_Relief'in n];ck('Six added floral and leaf relief panels are native meshes with no live subdivision',len(reliefs)==6 and all(len(o.data.polygons)>8000 and not len(o.modifiers)for o in reliefs),triangles=sum(len(o.data.polygons)for o in reliefs))
bad=[]
for n in ch['geometry_changed']:
 o=bpy.data.objects[n];uv=o.data.uv_layers.active
 if uv and not np.isfinite(q._bulk(uv.data,'uv',2)).all():bad.append(n)
ck('All changed native meshes have finite UV coordinates',not bad,invalid=bad)
ck('Neutral overcast world, soft saved lighting and direct sun off inherited',sc.world.name=='V26_8_Overcast_Soft_Even_Daylight'and all(o.data.energy==0 for o in sc.objects if o.type=='LIGHT'and o.data.type=='SUN'))
motion={}
for n in ['SITE_V20_INNER_GATE__LEAF_L_Geometry','SITE_V20_INNER_GATE__LEAF_R_Geometry']:
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();fn='GATE_LOCAL_'+str(len(motion))+'.npz';np.savez_compressed(FD/fn,v=q._bulk(me.vertices,'co',3).reshape(-1,3),f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32));motion[n]={'file':fn,'matrices':{}}
for fr in range(1,41):
 sc.frame_set(fr);bpy.context.view_layer.update()
 for n,r in motion.items():r['matrices'][str(fr)]=q._matrix(bpy.data.objects[n].matrix_world)
(FD/'Gate_Leaf_Motion.json').write_text(json.dumps(motion),'utf8')
sc.frame_set(40);bpy.context.view_layer.update()
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[r for r in checks if not r['pass']];(O/'Reports/V26_10_Native_Specific_QA.json').write_text(json.dumps({'model_sha256':h,'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail},indent=2),'utf8');print('NATIVE_SPECIFIC_DONE',len(checks),len(fail),flush=True)
