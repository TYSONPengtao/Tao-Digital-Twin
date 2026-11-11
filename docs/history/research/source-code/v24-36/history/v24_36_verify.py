from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_36';O=Path('E:/jz/JIA/Rebuild_V24_36');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_36.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));before=json.loads((D/'Before_Snapshot.json').read_text());after=snapshot(bpy);checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('CHECK',n,bool(p),kw,flush=True)
delta=[n for n,v in before['objects'].items()if n!='V24_21_Navigation_Collision'and after['objects'].get(n)!=v];ck('Entire repaired architecture and existing MB7 context remain unchanged',not delta,unexpected_changes=delta)
used={m.name for o in bpy.data.objects if o.name in before['objects']and o.type=='MESH'and o.name!='V24_21_Navigation_Collision'for m in o.data.materials if m};bad=[n for n in used if after['materials'].get(n,{}).get('hash')!=before['materials'][n]['hash']];ck('All existing material shader hashes in use are unchanged',not bad,changed=bad,unused_materials_discarded_by_save=[n for n in before['materials']if n not in after['materials']])
ck('All existing packed photo images are unchanged',all(after['images'].get(n)==v for n,v in before['images'].items()))
ck('All existing door and window poses and actions are unchanged',before['actions']==after['actions']and before['door_poses']==after['door_poses'])
rows=json.loads((D/'Missing_Exterior_Index.json').read_text());fr=json.loads((D/'Final_Exterior_Index.json').read_text());uvbad=[];gbad=[];pb=[];degen=0;maxround=0.;total=0
for i,(r,q)in enumerate(zip(rows,fr)):
 o=bpy.data.objects[q['name']];me=o.data;v=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);f=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',f);f=f.reshape(-1,3);a=np.load(D/q['file']);maxround=max(maxround,float(np.max(abs(v-a['v']))));uv=np.empty(len(me.loops)*2,np.float32);me.uv_layers.active.data.foreach_get('uv',uv)
 if not np.array_equal(uv,a['uv'].astype(np.float32).ravel()):uvbad.append(o.name)
 if not np.isfinite(v).all()or not np.array_equal(f,a['f']):gbad.append(o.name)
 tri=v[f].astype(float);degen+=int((np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)<1e-10).sum());total+=len(f)
 for mat,tx in zip(me.materials,r['textures']):
  im=next(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE');h=hashlib.sha256(bytes(im.packed_file.data)).hexdigest()if im.packed_file else None
  if h!=tx['sha256']:pb.append(im.name)
 if i%500==0:print('VERIFY_PTJIA6',i,len(rows),flush=True)
ck('Every PTJIA6 exterior mesh reads back with finite expected indexed coordinates',not gbad,invalid=gbad,triangles=total,meshes=len(rows),maximum_float32_rounding_m=maxround)
ck('Every PTJIA6 source face preserves original or barycentric photo UV',not uvbad,invalid=uvbad)
ck('Every PTJIA6 source JPEG is packed byte-for-byte',not pb,invalid=pb)
ck('No zero-area visible imported faces remain',degen==0,degenerate_faces=degen)
a=np.load(D/'Final_Collision.npz');old=np.load(W/'v24_35/Final_Collision.npz');ck('Every previous architectural and MB7 collision triangle is preserved',np.array_equal(a['v'][:len(old['v'])],old['v'])and np.array_equal(a['f'][:len(old['f'])],old['f']))
ci=json.loads((R/'V24_36_Collision_Index.json').read_text());ck('PTJIA6 adds collision throughout the expanded context',len(a['f'])>len(old['f'])and sum(x['source_meshes']for x in ci['PTJIA6_batches'])==len(rows),collision_triangles=len(a['f']),batches=len(ci['PTJIA6_batches']),bounds=ci['all_bounds'])
for text,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:ck('Embedded runtime matches external launcher '+fn,bpy.data.texts[text].as_string()==(O/'Roam'/fn).read_text('utf8'))
src=json.loads((D/'Source.json').read_text());ck('V24.35 repaired source is not overwritten',sha(src['model'])==src['sha256'])
fail=[q for q in checks if not q['pass']];(R/'V24_36_Native_QA.json').write_text(json.dumps({'status':'PASS_NATIVE_PRESERVATION_PTJIA6_IMPORT_AND_COLLISION'if not fail else'FAIL','model_sha256':sha(P),'checks':checks,'failures':fail},indent=2));print('V36_NATIVE',len(checks),'FAIL',len(fail),flush=True)
