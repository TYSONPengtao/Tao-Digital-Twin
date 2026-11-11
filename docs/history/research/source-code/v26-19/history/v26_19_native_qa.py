import bpy,sys,json,numpy as np,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
import v24_qa_blender as q
D=W/'v26_19';F=D/'Final';F.mkdir(exist_ok=True);O=Path('E:/jz/JIA/Rebuild_V26_19');P=O/'Blender/Architecture_Complete_V26_19.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
ch=json.loads((O/'Reports/V26_19_Changes.json').read_text('utf8'));before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));after=json.loads(json.dumps(snapshot(bpy),ensure_ascii=False));checks=[]
def ck(n,yes,**data):checks.append({'check':n,'pass':bool(yes),**data});print('NATIVE_QA',n,bool(yes),data if not yes else'',flush=True)
bad=[n for n,r in before['objects'].items()if n not in ch['changed']and after['objects'].get(n)!=r];ck('All unrelated objects, window frames, stair railing, doors and front stone reliefs are exact',not bad,invalid=bad)
for key in['materials','images','actions','door_poses']:
 bad=[n for n,r in before[key].items()if after[key].get(n)!=r];ck('Original '+key+' remain exact',not bad,invalid=bad)
for name,archive in ch['archive_map'].items():
 ob=bpy.data.objects[archive];ck('Exact original is recoverable and hidden: '+name,q._mesh_hash(ob.data)==before['objects'][name]['mesh_hash']and ob.hide_render and not ob.visible_get())
rows=[]
for name in ch['geometry_changed']:
 ob=bpy.data.objects[name];me=ob.data;me.calc_loop_triangles();v=q._world(me,ob.matrix_world);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int64);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles]);np.savez_compressed(F/(name+'.npz'),v=v,f=f,mi=mi,uv=uv)
 tr=v[f];area=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1)/2;edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),1);_,cnt=np.unique(edges,axis=0,return_counts=True);ck('Saved house mesh is closed, has no zero faces, and has finite UVs',np.all(cnt==2)and np.isfinite(v).all()and np.isfinite(uv).all()and area.min()>1e-18,minimum_face_area_m2=float(area.min()))
 rows.append({'name':name,'file':name+'.npz','materials':[m.name for m in me.materials],'mesh_hash':q._mesh_hash(me),'triangles':len(f)})
(F/'Geometry_Index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
previous=D/'Before_Planter_Removal_Index.json'
if previous.exists():
 prev={r['name']:r for r in json.loads(previous.read_text('utf8'))};ck('Beam and window corrections remain exact after the planter removal',all(r['mesh_hash']==prev[r['name']]['mesh_hash']for r in rows))
ci=json.loads((O/'Reports/V26_19_Collision_Index.json').read_text('utf8'))['objects'];names={r['name']for r in ci};ck('Current collision contains corrected meshes and excludes the archived original fixtures',set(ch['geometry_changed']).issubset(names)and not any(n in names for n in ch['archived']))
pot=bpy.data.objects['SITE_PLANTER_1_Geometry'];ck('The annotated planter has no visible or rendered surface and no collision',pot.hide_render and not pot.visible_get()and pot.name not in names and not any(o.visible_get()and o.name.startswith('V26_19_Previous_SITE_PLANTER_1')for o in sc.objects))
cn='GATE_V22_REAR_FIXED_TIMBER_SIDE_PANELS_Geometry';ck('Previously removed rear gate panels remain hidden',not bpy.data.objects[cn].visible_get()and bpy.data.objects[cn].hide_render)
ck('Overcast world, local AO and direct sun off are preserved',sc.world.name=='V26_8_Overcast_Soft_Even_Daylight'and sc.eevee.fast_gi_method=='AMBIENT_OCCLUSION_ONLY'and all(o.data.energy==0 for o in sc.objects if o.type=='LIGHT'and o.data.type=='SUN'))
ck('Source V26.18 file is unchanged',hashlib.sha256(Path(ch['source']).read_bytes()).hexdigest()==ch['source_sha256'])
mh=hashlib.sha256(P.read_bytes()).hexdigest();(D/'Native_After_Snapshot.json').write_text(json.dumps(after,ensure_ascii=False),'utf8');(D/'Native_Snapshot_Source_SHA256.txt').write_text(mh,'utf8');fail=[c for c in checks if not c['pass']];(O/'Reports/V26_19_Native_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':mh,'checks':checks,'failures':fail},ensure_ascii=False,indent=2),'utf8');print('NATIVE_QA_DONE',len(checks),len(fail),flush=True)
if fail:raise AssertionError([c['check']for c in fail])
