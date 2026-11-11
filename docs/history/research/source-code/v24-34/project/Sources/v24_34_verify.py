from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_34';O=Path('E:/jz/JIA/Rebuild_V24_34');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_34.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));after=snapshot(bpy);checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('CHECK',n,bool(p),kw,flush=True)
allowed={'V24_21_Navigation_Collision'};delta=[n for n,v in before['objects'].items()if after['objects'].get(n)!=v and n not in allowed]
ck('All 1401 original objects except collision cache are unchanged',not delta,changed_originals=delta)
mdiff=[n for n,v in before['materials'].items()if after['materials'].get(n,{}).get('hash')!=v['hash']];used={m.name for o in bpy.data.objects if o.name in before['objects']and o.type=='MESH'for m in o.data.materials if m};ck('All original material shader hashes are unchanged',not mdiff,unused_materials_discarded_by_save=[n for n in mdiff if n not in after['materials']],changed_shaders=[n for n in mdiff if n in after['materials']])
ck('All original packed photographs are unchanged',all(after['images'].get(n)==v for n,v in before['images'].items()))
ck('All original door and window animations and 1 20 40 poses are unchanged',after['actions']==before['actions']and after['door_poses']==before['door_poses'])
source=json.loads((D/'Source.json').read_text());ck('V24.33 source file remains byte-identical',sha(source['model'])==source['sha256'],source_sha256=source['sha256'])
rows=json.loads((D/'Missing_Exterior_Index.json').read_text());final=json.loads((D/'Final_Exterior_Index.json').read_text());invalid=[];uvbad=[];packbad=[];degen=0;maxdelta=0.;actualv=0;actualf=0
for r,fr in zip(rows,final):
 ob=bpy.data.objects[fr['name']];me=ob.data;v=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);f=np.empty(len(me.polygons)*3,dtype=np.int32);me.loops.foreach_get('vertex_index',f);f=f.reshape(-1,3);a=np.load(D/fr['file']);maxdelta=max(maxdelta,float(np.max(abs(v-a['v']))));uv=np.empty(len(me.loops)*2,dtype=np.float32);me.uv_layers.active.data.foreach_get('uv',uv)
 if not np.array_equal(uv,a['uv'].astype(np.float32).ravel()):uvbad.append(ob.name)
 if not np.isfinite(v).all()or len(f)!=fr['triangles']or not np.array_equal(f,a['f']):invalid.append(ob.name)
 tri=v[f].astype(float);degen+=int((np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)<1e-10).sum());actualv+=len(v);actualf+=len(f)
 for mat,tx in zip(me.materials,r['textures']):
  im=next(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE');h=hashlib.sha256(bytes(im.packed_file.data)).hexdigest()if im.packed_file else None
  if h!=tx['sha256']:packbad.append(im.name)
ck('All 154 clipped exterior tiles read back with finite original indexed geometry',not invalid,triangles=actualf,vertices=actualv,invalid=invalid,maximum_float32_rounding_m=maxdelta)
ck('Every new exterior face retains its barycentric original photo UV',not uvbad,invalid=uvbad)
ck('Every new original JPEG is packed byte-for-byte',not packbad,invalid=packbad)
ck('No visible zero-area imported triangles',degen==0,degenerate_triangles=degen)
cache=bpy.data.objects['V24_21_Navigation_Collision'];me=cache.data;me.calc_loop_triangles();v=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);f=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',f);f=f.reshape(-1,3);np.savez_compressed(D/'Final_Collision.npz',v=v,f=f);ck('Collision extends beyond the former architectural-only bounds',v[:,1].min()<-40 and v[:,0].min()<-40 and v[:,0].max()>60,bounds=[v.min(0).tolist(),v.max(0).tolist()],triangles=len(f))
ci=json.loads((R/'V24_34_Collision_Index.json').read_text());ck('Every old exterior and every added exterior has a collision proxy',len(ci['exterior_sources'])==159 and all(x['proxy_triangles']>0 for x in ci['exterior_sources']))
for tx,fn in [('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_启动漫游.py','start_roam.py'),('V24_25_测量工具.py','measure_tools.py')]:ck('Embedded runtime matches launcher file '+fn,bpy.data.texts[tx].as_string()==(O/'Roam'/fn).read_text('utf8'))
ck('Saved model keeps safety runtime and original measurement integration','last_safe'in bpy.data.texts['V24_21_碰撞控制.py'].as_string()and'recover()'in bpy.data.texts['V24_21_漫游控制器.py'].as_string())
fail=[r for r in checks if not r['pass']];(R/'V24_34_Native_QA.json').write_text(json.dumps({'status':'PASS_NATIVE_PRESERVATION_AND_MB7_IMPORT'if not fail else'FAIL','model_sha256':sha(P),'checks':checks,'failures':fail},ensure_ascii=False,indent=2));print('V34_NATIVE',len(checks),'FAIL',len(fail),flush=True)
