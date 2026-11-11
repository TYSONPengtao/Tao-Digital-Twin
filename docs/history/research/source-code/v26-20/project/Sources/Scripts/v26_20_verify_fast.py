from pathlib import Path
import bpy,json,sys,hashlib
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
O=Path('E:/jz/JIA/Rebuild_V26_20');D=W/'v26_20_perf';P=O/'Blender/Architecture_Complete_V26_20_Fast.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));before=json.loads((D/'Preservation_Before.json').read_text('utf8'));after=json.loads(json.dumps(snapshot(bpy),ensure_ascii=False));checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('FAST_QA',n,bool(p),kw if not p else'',flush=True)
for group,label in [('objects','All meshes, transforms, parents, material slots, UV and visibility retained'),('materials','All original shared material graphs retained'),('images','All original packed image bytes and pixels retained'),('actions','All original and new sliding actions retained'),('door_poses','Original door poses retained at1,20,40')]:
 bad=[n for n,v in before[group].items()if after[group].get(n)!=v];ck(label,not bad,invalid=bad)
master=O/'Blender/Architecture_Complete_V26_20.blend';build=json.loads((O/'Reports/V26_20_Build.json').read_text('utf8'));sc=bpy.context.scene
ck('Corrected master remains byte-identical to verified build',sha(master)==build['sha256'])
ck('Geometry collision cache is identical to master',before['objects']['V24_21_Navigation_Collision']==after['objects']['V24_21_Navigation_Collision'])
ck('Eevee8samples, half-resolution preview and local AO saved',sc.render.engine=='BLENDER_EEVEE'and sc.eevee.taa_samples==8 and sc.render.preview_pixel_size=='2'and sc.eevee.use_raytracing and sc.eevee.use_fast_gi and sc.eevee.fast_gi_method=='AMBIENT_OCCLUSION_ONLY'and sc.eevee.fast_gi_resolution=='2'and sc.eevee.ray_tracing_options.trace_max_roughness==0)
ck('Neutral overcast and direct sun off retained',sc.world.name=='V26_8_Overcast_Soft_Even_Daylight'and all(o.data.energy==0 for o in sc.objects if o.type=='LIGHT'and o.data.type=='SUN'))
ck('Fast controller matches embedded runtime',bpy.data.texts['V24_21_漫游控制器.py'].as_string()==(O/'Roam/roam_controller_fast.py').read_text('utf8'))
ck('Physics engine unchanged from master',bpy.data.texts['V24_21_碰撞控制.py'].as_string()==(O/'Roam/roam_physics.py').read_text('utf8'))
cmd=(O/'启动漫游.cmd').read_text('utf8');ck('Single launcher opens the new Fast model',sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd']and'Architecture_Complete_V26_20_Fast.blend'in cmd and'start_roam_fast.py'in cmd)
fail=[q for q in checks if not q['pass']];(O/'Reports/V26_20_Fast_Display_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':sha(P),'source_sha256':sha(master),'checks':checks,'failures':fail,'performance_scope':'Uses the V26.8 verified idle/focus skipping controller and fast display profile. No new FPS benchmark is claimed for V26.20.'},ensure_ascii=False,indent=2),'utf8');print('FAST_QA_DONE',len(checks),len(fail),flush=True)
