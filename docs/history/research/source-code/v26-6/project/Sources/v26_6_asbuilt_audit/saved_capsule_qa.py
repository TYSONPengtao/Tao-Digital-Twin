import bpy,sys,json,types,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).resolve().parent.parent;O=Path('E:/jz/JIA/Rebuild_V26_6');P=O/'Blender/Architecture_Complete_V26_6.blend';R=O/'Reports';bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
mod=types.ModuleType('architecture_terrace_regression_physics');sys.modules[mod.__name__]=mod;exec(compile(bpy.data.texts['V24_21_碰撞控制.py'].as_string(),'saved embedded capsule physics','exec'),mod.__dict__)
o=bpy.data.objects['V24_21_Navigation_Collision'];me=o.data;me.calc_loop_triangles();world=mod.World([o.matrix_world@v.co for v in me.vertices],[t.vertices[:]for t in me.loop_triangles]);checks=[];traces={}
def go(w,xy,seconds=7.):
 trace=[]
 for i in range(int(seconds*60)):
  d=Vector((xy[0]-w.p.x,xy[1]-w.p.y,0))
  if d.length<.045:return True,trace
  w.update(d.normalized(),1/60)
  if i%6==0:trace.append([*w.p,w.grounded,w.recoveries])
 return False,trace
for x in [.6,1.2,1.8,2.5,3.2]:
 w=mod.Walker(world,(x,6.7,7.05));initial_recoveries=w.recoveries
 for label,target in [('enter',(x,8.7)),('return',(x,6.7))]:
  ok,tr=go(w,target);traces[f'{x}_{label}']=tr;yes=ok and w.grounded and w.recoveries==initial_recoveries and all(abs(q[2]-7.05)<.01 for q in tr)
  checks.append({'check':f'Actual human capsule {label} F3 photographed terrace opening at X{x}','pass':bool(yes),'target_xy_m':target,'end_position_m':list(w.p),'trajectory_samples':len(tr),'foot_level_error_m':max([abs(q[2]-7.05)for q in tr]+[0]),'recoveries':w.recoveries,'capsule_height_m':mod.HEIGHT,'capsule_radius_m':mod.RADIUS});print('CAPSULE',x,label,yes,list(w.p),flush=True)
with P.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
path=R/'V26_6_AsBuilt_Terrace_Regression_QA.json';out=json.loads(path.read_text('utf8'));assert out['model_sha256']==sha,'Geometry QA stale'
out['checks']=[c for c in out['checks']if not c['check'].startswith('Actual human capsule')]+checks;out['evidence']['capsule_trajectories']=traces;out['failures']=[c for c in out['checks']if not c['pass']];out['status']='PASS'if not out['failures']else'FAIL';path.write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('TERRACE_PHYSICS_DONE',len(checks),'FAIL',sum(not c['pass']for c in checks),'OVERALL',out['status'],flush=True)
