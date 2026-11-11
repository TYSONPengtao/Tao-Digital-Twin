from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_37';O=Path('E:/jz/JIA/Rebuild_V24_37');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_37.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));before=json.loads((D/'Before_Snapshot.json').read_text());after=snapshot(bpy);plan=json.loads((D/'Cleanup_Report.json').read_text());allowed=set(plan['changed'])|set(plan['removed'])|{'V24_21_Navigation_Collision'};checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('CHECK',n,bool(p),kw,flush=True)
delta=[n for n,v in before['objects'].items()if n not in allowed and after['objects'].get(n)!=v];ck('Every original object outside the declared scan cleanup remains identical',not delta,unexpected=delta,protected_objects=len(before['objects'])-len(allowed))
ck('Only explicitly listed photographic fragments are removed',all(n not in after['objects']for n in plan['removed']),removed_count=len(plan['removed']))
used={m.name for o in bpy.data.objects if o.name in before['objects']and o.type=='MESH'and o.name!='V24_21_Navigation_Collision'for m in o.data.materials if m};bad=[n for n in used if after['materials'].get(n,{}).get('hash')!=before['materials'][n]['hash']];ck('Every used material shader is unchanged',not bad,changed=bad,materials=len(used))
images={n.image.name for mat in bpy.data.materials if mat.name in used and mat.use_nodes for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'and n.image};bad=[n for n in images if after['images'][n]['packed_hashes']!=before['images'][n]['packed_hashes']or not after['images'][n]['packed_hashes']];ck('Every used original photo remains packed byte-for-byte',not bad,changed=bad,images=len(images),unused_images_not_in_use=len(set(before['images'])-images))
ck('All door and window poses and actions remain unchanged',before['actions']==after['actions']and before['door_poses']==after['door_poses'])
rows=json.loads((D/'Final_Scan_Index.json').read_text());gbad=[];uvbad=[];degen=0;maxround=0.;total=0
for i,r in enumerate(rows):
 o=bpy.data.objects[r['name']];me=o.data;v=np.empty(len(me.vertices)*3,np.float64);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);M=np.array(o.matrix_world);v=v@M[:3,:3].T+M[:3,3];me.calc_loop_triangles();f=np.empty(len(me.loop_triangles)*3,np.int32);me.loop_triangles.foreach_get('vertices',f);f=f.reshape(-1,3);a=np.load(D/r['file']);err=float(np.max(abs(v-a['v'])));maxround=max(maxround,err)
 if not np.isfinite(v).all()or not np.array_equal(f,a['f'])or err>8e-5:gbad.append(o.name)
 if r['has_uv']:
  u=np.empty(len(me.loops)*2,np.float32);me.uv_layers.active.data.foreach_get('uv',u)
  if not np.array_equal(u,a['uv'].astype(np.float32).ravel()):uvbad.append(o.name)
 t=v[f];degen+=int((np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)<1e-10).sum());total+=len(f)
 if i%600==0:print('VERIFY_SCAN',i,len(rows),flush=True)
ck('Cleaned exterior reads back with exactly indexed finite geometry',not gbad,invalid=gbad,maximum_coordinate_rounding_m=maxround,meshes=len(rows),triangles=total)
ck('Every retained face has its original or barycentric source photo UV',not uvbad,invalid=uvbad)
ck('No zero-area display faces remain in scanned exterior',degen==0,degenerate_faces=degen)
a=np.load(D/'Final_Collision.npz');base=np.load(W/'v24_35/Final_Collision.npz');ci=json.loads((R/'V24_37_Collision_Index.json').read_text());nb=ci['architectural_triangles_preserved'];nv=ci['architectural_vertices_preserved'];ck('All original architectural collision triangles and vertices are preserved exactly',np.array_equal(a['v'][:nv],base['v'][:nv])and np.array_equal(a['f'][:nb],base['f'][:nb]),triangles=nb)
cache=bpy.data.objects['V24_21_Navigation_Collision'];me=cache.data;v=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',v);f=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',f);ck('Native collision exactly matches the cleaned geometry cache',np.array_equal(v,a['v'].ravel())and np.array_equal(f,a['f'].ravel()),triangles=len(a['f']))
names=[n for row in ci['photo_batches']for n in row['source_meshes']];ck('Every retained scan contributes collision and every removed scan is excluded',set(names)=={r['name']for r in rows}and len(names)==len(rows)and not(set(names)&set(plan['removed'])),retained_sources=len(names),batches=len(ci['photo_batches']))
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:ck('Embedded runtime matches external '+fn,bpy.data.texts[txt].as_string()==(O/'Roam'/fn).read_text('utf8'))
# Recheck the six annotated wall/eave pixels after both extensions and cleanup.
sc=bpy.context.scene;sc.render.resolution_x=1500;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;c=bpy.data.objects['V24_35_01_Kitchen_East'];corners=c.data.view_frame(scene=sc);lo=Vector((min(v.x for v in corners),min(v.y for v in corners),corners[0].z));hi=Vector((max(v.x for v in corners),max(v.y for v in corners),corners[0].z));deps=bpy.context.evaluated_depsgraph_get();rays=[]
for row in json.loads((W/'v24_35/Visible_Artifact_Rays.json').read_text()):
 if not row['object'].startswith('V24_34_MB7_'):continue
 x,y=row['pixel'];local=Vector((lo.x+(hi.x-lo.x)*x/1500,hi.y-(hi.y-lo.y)*y/1100,lo.z));direction=(c.matrix_world.to_3x3()@local).normalized();origin=c.location.copy();ob=None
 for _ in range(16):
  hit,p,no,face,o,mat=sc.ray_cast(deps,origin,direction,distance=100)
  if not hit:break
  if not o.hide_render:ob=o.name;break
  origin=p+direction*.001
 rays.append({'pixel':[x,y],'visible_object':ob});ck('Annotated wall and eave has no scan overlay at '+str([x,y]),ob is not None and'ORIGINAL_EXTERIOR_'not in ob and not ob.startswith(('V24_34_MB7_','V24_36_PTJIA6_')),visible_object=ob)
source=json.loads((D/'Source.json').read_text());ck('Pre-cleanup V24.36 source remains byte-identical',sha(source['model'])==source['sha256'])
fail=[q for q in checks if not q['pass']];(R/'V24_37_Native_QA.json').write_text(json.dumps({'status':'PASS_NATIVE_PRESERVATION_CLEANED_EXTERIOR_AND_ANNOTATED_REPAIR'if not fail else'FAIL','model_sha256':sha(P),'checks':checks,'failures':fail,'annotated_rays':rays},ensure_ascii=False,indent=2),encoding='utf8');print('NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
