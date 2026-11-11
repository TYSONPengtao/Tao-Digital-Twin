import bpy,sys,json,hashlib,numpy as np,types
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_21';O=Path('E:/jz/JIA/Rebuild_V24_21');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_21.blend';before=json.loads((D/'Before_Snapshot.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());changes=json.loads((R/'V24_21_Changes.json').read_text());checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw})
bpy.ops.wm.open_mainfile(filepath=str(P));after=json.loads(json.dumps(snapshot(bpy)))
for n,a in before['objects'].items():
 b=after['objects'].get(n);ck('Original object completely preserved / '+n,b==a)
for kind in ['materials','actions','images']:
 for n,a in before[kind].items():ck('Original '+kind+' preserved / '+n,after[kind].get(n)==a)
ck('26 original door interactions retained',len(after['doors'])==26 and after['door_poses']==before['door_poses'])
ck('No original objects removed',set(before['objects']).issubset(after['objects']))
ck('All additions declared',set(after['objects'])-set(before['objects'])==set(changes['added']))
ck('Original perimeter tile coping retained exactly',all(after['objects'][n]==before['objects'][n]for n in before['objects']if 'PERIMETER_JOINED_RETAINING_WALL'in n and'TILE_COPING'in n))
exports=[]
for row in prep['objects']:
 o=bpy.data.objects[row['name']];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles]);fn=f'DETAIL_{len(exports):02d}.npz';np.savez_compressed(D/fn,v=v,f=f);exports.append({'name':o.name,'file':fn,'prepared_volume_m3':row['volume_m3']});expected=np.array(row['v']);ck('Actual relief vertices saved / '+o.name,len(v)==len(expected)and np.max(np.linalg.norm(v-expected,axis=1))<3e-5)
ck('All external reference images packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
for n in ['V24_21_碰撞控制.py','V24_21_漫游控制器.py','V24_21_启动漫游.py']:ck('Navigation script embedded / '+n,n in bpy.data.texts and len(bpy.data.texts[n].as_string())>300)
ck('Navigation cache hidden from rendering',bpy.data.objects['V24_21_Navigation_Collision'].hide_render)
for module,text in [('architecture_roam_physics','V24_21_碰撞控制.py'),('architecture_roam_controller','V24_21_漫游控制器.py')]:
 m=types.ModuleType(module);sys.modules[module]=m;exec(compile(bpy.data.texts[text].as_string(),text,'exec'),m.__dict__)
control=sys.modules['architecture_roam_controller'];control.register();ck('Actual embedded controller registers',hasattr(bpy.types.Scene,'arch_roam'));control.unregister();ck('Actual embedded controller unregisters cleanly',not hasattr(bpy.types.Scene,'arch_roam'))
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Saved_Detail_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2));fail=[r for r in checks if not r['pass']];out={'status':'PASS_FRESH_NATIVE_PRESERVATION_AND_CONTROLLER'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail};(R/'V24_21_Native_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('V21_NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
for r in fail:print('FAIL',r,flush=True)
