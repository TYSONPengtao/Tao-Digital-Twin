from pathlib import Path
import bpy,numpy as np,json,sys,hashlib
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v26_1';FD=D/'Final';FD.mkdir(exist_ok=True);O=Path('E:/jz/JIA/Rebuild_V26_1');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_1.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));after=snapshot(bpy);sc.frame_set(40);bpy.context.view_layer.update();ch=json.loads((R/'V26_1_Changes.json').read_text('utf8'));allowed=set(ch['changed']);checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw,flush=True)
diff=[n for n,v in before['objects'].items()if n not in allowed and after['objects'].get(n)!=v];ck('Unrelated source objects retain meshes, transforms, UVs, materials and visibility',not diff,checked=len(before['objects'])-len(allowed),mismatches=diff)
ck('Original V26 input file remains byte identical',sha(ch['source'])==ch['source_sha256']);ck('Every original object is retained',all(n in after['objects']for n in before['objects']))
md=[n for n,v in before['materials'].items()if after['materials'].get(n,{}).get('hash')!=v['hash']];ck('Original shared material graphs remain unchanged',not md,changed_original_shaders=md)
im=[n for n,v in before['images'].items()if after['images'].get(n)!=v];ck('All packed photographs remain byte identical',not im,changed_images=im)
ck('All door/window animations and poses at frames 1 20 40 remain unchanged',before['actions']==after['actions']and before['door_poses']==after['door_poses'])
ck('All archived originals are invisible to rendering and ordinary viewport',all(bpy.data.objects[n].hide_render and bpy.data.objects[n].hide_get()for n in ch['archived']),count=len(ch['archived']))
ci=json.loads((R/'V26_1_Collision_Index.json').read_text('utf8'));cn={r['name']for r in ci['objects']};ck('No archived source component survives as an independent collision surface',not(cn&set(ch['archived'])),invalid=sorted(cn&set(ch['archived'])))
for n in ['V26_1_House_Continuous_Opaque_Shell','V26_1_Photo_Referenced_Continuous_Wood_Railing','V26_1_Continuous_Court_Road_And_Floor_Surfaces','V26_Original_Site_Entrance_Ramp_0']:ck('Current collision includes '+n,n in cn)
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:ck('Embedded runtime matches '+fn,bpy.data.texts[txt].as_string()==(O/'Roam'/fn).read_text('utf8'))
rows=[];invalid=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render or(o.name.startswith('V24_21_')and not o.name.startswith('V24_21_Exterior_')):continue
 if any(k in o.name for k in ['ORIGINAL_EXTERIOR_','V24_34_MB7_','V24_Gate_Reference_Relief_','V24_Gate_Waist_Carving_']):continue
 if len(o.data.polygons)>100000 and not o.name.startswith('V26_1_'):continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles],np.float32)if me.uv_layers.active else np.zeros((len(f),3,2),np.float32);fn='FINAL_'+str(len(rows))+'.npz';np.savez_compressed(FD/fn,v=v,f=f,mi=mi,uv=uv);rows.append({'name':o.name,'file':fn,'materials':[m.name for m in me.materials],'triangles':len(f),'bounds':[v.min(0).tolist(),v.max(0).tolist()]})
 if not np.isfinite(v).all():invalid.append(o.name)
ck('All exported actual saved visible geometry is finite',not invalid,invalid=invalid)
ck('Original entrance-ramp object is unchanged',before['objects']['V26_Original_Site_Entrance_Ramp_0']==after['objects']['V26_Original_Site_Entrance_Ramp_0'])
ck('No Rhino export is created',not list(O.rglob('*.3dm')))
(FD/'Geometry_Index.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8');fail=[r for r in checks if not r['pass']];(R/'V26_1_Native_Readback_QA.json').write_text(json.dumps({'model_sha256':sha(P),'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8');print('READBACK_DONE',len(checks),len(fail),flush=True)
