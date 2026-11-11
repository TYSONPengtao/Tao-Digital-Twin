from pathlib import Path
import bpy,numpy as np,json,sys,hashlib
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_11';FD=D/'Final';FD.mkdir(exist_ok=True);O=Path('E:/jz/JIA/Rebuild_V26_11');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_11.blend';sys.path.insert(0,str(W));from v24_06_common import snapshot
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));after=json.loads(json.dumps(snapshot(bpy),ensure_ascii=False));sc.frame_set(40);bpy.context.view_layer.update();ch=json.loads((R/'V26_11_Changes.json').read_text('utf8'));allowed=set(ch['changed']);checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw,flush=True)
diff=[n for n,v in before['objects'].items()if n not in allowed and after['objects'].get(n)!=v];ck('Unrelated source meshes transforms UVs materials and visibility retained',not diff,checked=len(before['objects'])-len(allowed),mismatches=diff)
ck('V26.10 source remains byte identical',sha(ch['source'])==ch['source_sha256']);ck('All original objects remain in the editable file',all(n in after['objects']for n in before['objects']))
md=[n for n,v in before['materials'].items()if after['materials'].get(n,{}).get('hash')!=v['hash']];ck('Original shared shader graphs unchanged',not md,changed=md)
im=[n for n,v in before['images'].items()if after['images'].get(n)!=v];ck('Original packed photo bytes unchanged',not im,changed=im);ck('All original animation curves unchanged',all(after['actions'].get(k)==v for k,v in before['actions'].items()))
posebad=[]
for fr,old in before['door_poses'].items():
 for n,m in old.items():
  want=np.array(m)
  got=np.array(after['door_poses'].get(fr,{}).get(n,[]))
  if got.shape!=(4,4)or np.max(abs(want-got))>3e-6:posebad.append([fr,n])
ck('All original evaluated door poses retained',not posebad,mismatches=posebad,frames=[1,20,40])
ck('Archived previous components excluded from rendering and viewport',all(bpy.data.objects[n].hide_render and bpy.data.objects[n].hide_get()for n in ch['archived']))
ci=json.loads((R/'V26_11_Collision_Index.json').read_text('utf8'));cn={r['name']for r in ci['objects']};ck('Archived sources excluded from collision',not(cn&set(ch['archived'])))
for n in ['V26_3_House_Connected_Walls_And_Stairs','V26_2_Continuous_Ground_And_Perimeter_Shell','V26_1_Photo_Referenced_Continuous_Wood_Railing','V26_Original_Site_Entrance_Ramp_0']:ck('Saved collision contains '+n,n in cn)
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:ck('Embedded runtime matches '+fn,bpy.data.texts[txt].as_string()==(O/'Roam'/fn).read_text('utf8'))
protection=(W/'v26_11_protection_qa.py').read_text('utf8').replace("bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(40);bpy.context.view_layer.update()",'')
exec(compile(protection,str(W/'v26_11_protection_qa.py'),'exec'),{'__file__':str(W/'v26_11_protection_qa.py')})
rows=[];invalid=[]
for o in bpy.data.objects:
 if o.type!='MESH'or not len(o.data.polygons)or o.hide_render or any(c.hide_render for c in o.users_collection):continue
 if any(k in o.name for k in ['ORIGINAL_EXTERIOR_','V24_34_MB7_','Navigation_Collision','Avatar_','Roam_Person','V24_Gate_Reference_Relief_','V24_Gate_Waist_Carving_']):continue
 if len(o.data.polygons)>100000 and not o.name.startswith('V26_'):continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles],np.float32)if me.uv_layers.active else np.zeros((len(f),3,2),np.float32);fn='FINAL_'+str(len(rows))+'.npz';np.savez_compressed(FD/fn,v=v,f=f,mi=mi,uv=uv);rows.append({'name':o.name,'file':fn,'materials':[m.name for m in me.materials],'triangles':len(f),'bounds':[v.min(0).tolist(),v.max(0).tolist()]})
 if not np.isfinite(v).all():invalid.append(o.name)
ck('Actual saved visible native geometry finite',not invalid,invalid=invalid);ck('Original photographed entrance ramp fully unchanged',before['objects']['V26_Original_Site_Entrance_Ramp_0']==after['objects']['V26_Original_Site_Entrance_Ramp_0']);ck('No Rhino model exported',not list(O.rglob('*.3dm')))

# Export actual evaluated hinge matrices, including intermediate animated poses.
leaves=[o for o in bpy.data.objects if o.type=='MESH'and o.name.endswith('__LEAF_Geometry')and o.name.startswith(('DOOR_BATH_','DOOR_BED_','DOOR_KITCHEN_F1','DOOR_STUDY_'))];motion={}
for o in leaves:
 me=o.data;me.calc_loop_triangles();fn='LEAF_LOCAL_'+str(len(motion))+'.npz';np.savez_compressed(FD/fn,v=np.array([p.co[:]for p in me.vertices]),f=np.array([t.vertices[:]for t in me.loop_triangles]));motion[o.name]={'file':fn,'matrices':{}}
for fr in list(range(1,41,3))+[40]:
 sc.frame_set(fr);bpy.context.view_layer.update()
 for o in leaves:motion[o.name]['matrices'][str(fr)]=[list(r)for r in o.matrix_world]
(FD/'Door_Motion.json').write_text(json.dumps(motion),encoding='utf8');(FD/'Geometry_Index.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8');fail=[c for c in checks if not c['pass']];(R/'V26_11_Native_Readback_QA.json').write_text(json.dumps({'model_sha256':sha(P),'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8');print('READBACK_DONE',len(checks),len(fail),flush=True)
