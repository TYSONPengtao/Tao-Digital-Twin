import bpy,sys,json,math,time,hashlib,types
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W))
O=Path('E:/jz/JIA/Rebuild_V24_27');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_27.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
m=types.ModuleType('architecture_roam_physics');sys.modules[m.__name__]=m;exec(compile(bpy.data.texts['V24_21_碰撞控制.py'].as_string(),'embedded physics','exec'),m.__dict__);World=m.World;Walker=m.Walker;HEIGHT=m.HEIGHT;RADIUS=m.RADIUS
ob=bpy.data.objects['V24_21_Navigation_Collision'];me=ob.data;me.calc_loop_triangles();world=World([ob.matrix_world@v.co for v in me.vertices],[t.vertices[:]for t in me.loop_triangles]);checks=[];traces={};start=time.perf_counter()
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw,flush=True)
def go(w,xy,limit=7.):
 tr=[];limit=int(limit*60)
 for i in range(limit):
  diff=Vector((xy[0]-w.p.x,xy[1]-w.p.y,0))
  if diff.length<.045:return True,tr
  d=diff.normalized();w.update(d,1/60)
  if i%6==0:tr.append([*w.p,w.vz,w.grounded])
 return False,tr

w=Walker(world,(6.5,-4.8,-.411));ground=w.p.z;ck('Courtyard spawn has foot support and 1.65m clearance',w.grounded and world.clear(w.p),position=list(w.p))
ck('Wall collision prevents walking through stair-facing masonry',True)
w=Walker(world,(8.5,8.0,0.))
for _ in range(180):w.update((1,0),1/60)
checks[-1].update({'pass':8.5<w.p.x<8.80,'final_position':list(w.p)})
w=Walker(world,(8.5,9.0,0.));ok,tr=go(w,(9.8,9.0));traces['stair_wc_door']=tr;ck('Stair-facing WC door passes the human capsule',ok,position=list(w.p))
for _ in range(120):w.update((1,0),1/60)
ck('Blue WC partition blocks human passage',9.7<w.p.x<10.42,position=list(w.p))
w=Walker(world,(11.1,6.9,0.));ok,tr=go(w,(11.1,8.3));traces['right_wc_door']=tr;ck('Relocated right WC door passes the human capsule',ok,position=list(w.p))

w=Walker(world,(8.5,7.8,0.));route=[(8.5,9.1),(4.55,9.1),(4.55,8.0),(8.5,8.0)]
for floor,target_z in [(2,3.900024),(3,7.5)]:
 success=True;tr=[]
 for xy in route:
  ok,t=go(w,xy);tr+=t
  if not ok:success=False;print('STAIR_STUCK',floor,xy,list(w.p),flush=True);break
 traces['ascend_floor_'+str(floor)]=tr;ck('Walk up actual two-flight stair to floor '+str(floor),success and abs(w.p.z-target_z)<.045,final_position=list(w.p),expected_floor_z=target_z)
 if not success:break
if w.p.z>7.4:
 for floor,target_z in [(2,3.900024),(1,0.)]:
  success=True;tr=[]
  for xy in [(4.55,8.0),(4.55,9.1),(8.5,9.1),(8.5,7.8)]:
   ok,t=go(w,xy);tr+=t
   if not ok:success=False;break
  traces['descend_floor_'+str(floor)]=tr;ck('Walk down actual two-flight stair to floor '+str(floor),success and abs(w.p.z-target_z)<.045,final_position=list(w.p),expected_floor_z=target_z)

w=Walker(world,(6.5,-4.8,-.411));z0=w.p.z;peak=z0
for i in range(150):w.update((0,0),1/60,jump=i==0);peak=max(peak,w.p.z)
ck('Space jump lifts the person and lands on the same surface',.50<peak-z0<.67 and w.grounded and abs(w.p.z-z0)<.005,jump_height_m=peak-z0,landing_error_m=w.p.z-z0)
target=Vector((8.4,8.0,1.25));desired=Vector((10.5,8.0,1.7));camera=world.camera(target,desired);ck('Follow camera retracts before entering the wall',camera.x<8.9 and(camera-target).length<1.,camera=list(camera))
root=bpy.data.objects['V24_21_Roam_Person_165cm'];vs=[o.matrix_world@v.co for o in root.children_recursive if o.type=='MESH'for v in o.data.vertices];height=max(v.z for v in vs)-min(v.z for v in vs);ck('Visible standing person height is exactly 1.65m',abs(height-1.65)<.00002,measured_height_m=height)
w=Walker(world,(8.87,-10.45,-.4));ok,tr=go(w,(8.87,-3.55),limit=10.);traces['kitchen_porch']=tr;ck('Walk full kitchen porch past centre post',ok,position=list(w.p))
w=Walker(world,(8.87,-3.55,-.4));ok,tr=go(w,(8.87,-2.35));traces['kitchen_north_exit']=tr;ck('New north white wall blocks the marked opening',not ok and w.p.y<-3.20,position=list(w.p))
w=Walker(world,(10.1,-7.75,-.4));ok,tr=go(w,(12.6,-7.75));traces['kitchen_interior']=tr;ck('Kitchen floor remains walkable with wall posts',ok,position=list(w.p))
w=Walker(world,(-5.5,3.0,-.50));ok,tr=go(w,(-.65,3.0),limit=9.);traces['west_yard_grade']=tr;ck('Walk up the corrected west yard grade without jumping',ok and -.195<w.p.z<-.165,position=list(w.p))
ok,tr=go(w,(-.65,8.8),limit=9.);traces['west_bathroom_side']=tr;ck('Walk along west bathroom exterior with ground support',ok and w.grounded,position=list(w.p))
w=Walker(world,(6.5,-4.8,-.42));ok,tr=go(w,(6.5,-.70),limit=9.);traces['court_to_house_step']=tr;ck('Walk graded court to the lower entry landing',ok and abs(w.p.z+.148)<.01,position=list(w.p))
ok,tr=go(w,(6.5,1.0),limit=7.);traces['entry_single_step_up']=tr;ck('Climb the retained single entry step without jumping',ok and abs(w.p.z)<.015,position=list(w.p))
ok,tr=go(w,(6.5,-.7),limit=7.);traces['entry_single_step_down']=tr;ck('Walk down the single entry step onto the court',ok and w.grounded,position=list(w.p))
w=Walker(world,(6.5,-.7,-.16));success=True;tr=[]
for xy in [(6.5,-2.),(7.,-3.9),(8.87,-3.9)]:
 ok,t=go(w,xy,limit=7.);tr+=t;success=success and ok
traces['house_court_to_kitchen_gallery']=tr;ck('Continuous walk from house court to kitchen gallery',success and abs(w.p.z+.4)<.02,position=list(w.p))
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[r for r in checks if not r['pass']];out={'status':'PASS_ACTUAL_MODEL_ROAM_PHYSICS'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail,'trajectory_samples':traces,'test_seconds':time.perf_counter()-start};(R/'V24_27_Physics_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('V21_PHYSICS_QA',len(checks),'FAIL',len(fail),'SECONDS',out['test_seconds'],flush=True)
