import bpy,sys,json,math,time,hashlib,types
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W))
O=Path('E:/jz/JIA/Rebuild_V26_18');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_18.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
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
w=Walker(world,(10.,6.8,0.));ok,tr=go(w,(10.,8.0));traces['restored_wc_separation']=tr;ck('Restored WC front partition prevents bedroom entry through a missing wall',not ok and w.p.y<7.0,position=list(w.p))
w=Walker(world,(11.1,6.9,0.));ok,tr=go(w,(11.1,8.3));traces['right_wc_door']=tr;ck('Relocated right WC door passes the human capsule',ok,position=list(w.p))

w=Walker(world,(8.5,7.8,0.));route=[(8.5,9.1),(4.55,9.1),(4.55,8.0),(8.5,8.0)]
for floor,target_z in [(2,3.450024),(3,7.05)]:
 success=True;tr=[]
 for xy in route:
  ok,t=go(w,xy);tr+=t
  if not ok:success=False;print('STAIR_STUCK',floor,xy,list(w.p),flush=True);break
 traces['ascend_floor_'+str(floor)]=tr;ck('Walk up actual two-flight stair to floor '+str(floor),success and abs(w.p.z-target_z)<.045,final_position=list(w.p),expected_floor_z=target_z)
 if not success:break
if w.p.z>6.95:
 for floor,target_z in [(2,3.450024),(1,-.45)]:
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
w=Walker(world,(8.87,-3.55,-.4));ok,tr=go(w,(8.87,-2.35));traces['kitchen_north_exit']=tr;ck('Restored kitchen north wall stops the capsule at the new inner face',not ok and abs(w.p.y-(-2.755-RADIUS))<.02,position=list(w.p),wall_inner_y_m=-2.755,capsule_radius_m=RADIUS)
w=Walker(world,(10.1,-7.75,-.4));ok,tr=go(w,(12.6,-7.75));traces['kitchen_interior']=tr;ck('Kitchen floor remains walkable with wall posts',ok,position=list(w.p))
w=Walker(world,(-5.5,3.0,-.50));ok,tr=go(w,(-.65,3.0),limit=9.);traces['west_yard_grade']=tr;ck('Walk across the level exterior without jumping',ok and abs(w.p.z+.60)<.005,position=list(w.p))
ok,tr=go(w,(-.65,8.8),limit=9.);traces['west_bathroom_side']=tr;ck('Walk along west bathroom exterior with ground support',ok and w.grounded,position=list(w.p))
w=Walker(world,(6.5,-4.8,-.42));ok,tr=go(w,(6.5,-.70),limit=9.);traces['court_to_house_step']=tr;ck('Walk low paved court to the one-step entrance',ok and w.grounded and abs(w.p.z+.60)<.012,position=list(w.p),capsule_support_radius_m=RADIUS)
ok,tr=go(w,(6.5,1.0),limit=7.);traces['entry_single_step_up']=tr;ck('Enter the lowered house over the single 15cm step',ok and abs(w.p.z+.45)<.015,position=list(w.p))
ok,tr=go(w,(6.5,-.7),limit=7.);traces['entry_single_step_down']=tr;ck('Return down the single entrance step to the low court',ok and w.grounded,position=list(w.p))
# Cross the marked step in both directions, then follow its high side.
import numpy as np
A=np.array([8.15,-.30]);B=np.array([8.15,-3.12]);u=(A-B)/np.linalg.norm(A-B);hi=np.array([u[1],-u[0]])
p=B+(A-B)*.55;lo=p-hi*.45;upper=p+hi*.45
w=Walker(world,(*lo,-.30));z0=w.p.z;ok,tr=go(w,upper);traces['new_step_up']=tr
ck('Step from low main court onto high north lane',ok and abs(w.p.z-z0-.15)<.012,position=list(w.p),rise_m=w.p.z-z0)
ok,tr=go(w,lo);traces['new_step_down']=tr
ck('Step down from high north lane to low main court',ok and w.grounded and abs(w.p.z-z0)<.02,position=list(w.p))
p0=B+(A-B)*.30+hi*.40;p1=B+(A-B)*.90+hi*.40
w=Walker(world,(*p0,-.28));ok,tr=go(w,p1);traces['high_side_to_house']=tr
ck('Walk along the level approach toward the lowered house',ok and w.grounded,position=list(w.p))
w=Walker(world,(6.5,2.8,0.));ok,tr=go(w,(2.,2.8));traces['flat_house_room']=tr
ck('First-floor interior remains flat while traversing the room',ok and abs(w.p.z+.45)<.015 and all(abs(p[2]+.45)<.015 for p in tr),position=list(w.p))
# Walk from the outer gate along the actual graded approach, then enter
# the flat white yard at its nearly flush inner landing.
w=Walker(world,(-13.5,-10.9,-.80));success=True;tr=[]
for xy in [(-12.,-10.9),(-9.,-11.0),(-6.,-11.9),(-3.,-12.),(-.7,-12.),(-.7,-10.5),(-2.,-8.8)]:
 ok,t=go(w,xy,limit=8.);tr+=t
 if not ok:success=False;break
traces['outer_gate_road_to_white_yard']=tr
ck('Walk graded gate approach and enter the white building pad',success and w.grounded and abs(w.p.z+.60)<.008,position=list(w.p))
w=Walker(world,(-12.,0.,-.5));ok,tr=go(w,(-3.,0.),limit=10.);traces['flat_white_pad']=tr
# Native pad vertices are unchanged. The single-precision BVH capsule support
# may settle a few millimetres above its exact plane after triangulation changes.
ck('Flat white outer pad has continuous foot support',ok and w.grounded and all(abs(p[2]+.60)<.005 for p in tr),position=list(w.p),allowed_support_tolerance_m=.005,maximum_support_error_m=max(abs(p[2]+.60) for p in tr))
w=Walker(world,(-.65,10.8,-.5));ok,tr=go(w,(.65,10.8),limit=4.);traces['rear_partition']=tr
ck('Rear partition physically separates outer yard and high internal strip',not ok and w.p.x<-.30,position=list(w.p))
w=Walker(world,(13.7,2.0,-.3));ok,tr=go(w,(14.1,6.0),limit=9.);traces['high_rear_lane']=tr
ck('High lane remains walkable beside corrected perimeter wall',ok and w.grounded and abs(w.p.z+.45)<.008,position=list(w.p))
w=Walker(world,(8.45,-12.7,-.45));ok,tr=go(w,(12.55,-12.7),limit=8.);traces['filled_storage_approach']=tr
ck('Walk across the formerly missing storage approach without falling',ok and w.grounded and all(p[2]>-.70 for p in tr),position=list(w.p))
w=Walker(world,(-9.0,-13.6,-.75));ok,tr=go(w,(-4.8,-13.6),limit=8.);traces['filled_road_to_wall_toe']=tr
ck('Repaired road edge beside the wall has continuous foot support',ok and w.grounded and all(p[2]>-1.45 for p in tr),position=list(w.p))
# Walk through the exact newly repaired interfaces.
for fl,z in [(2,3.450024366378784),(3,7.050000190734863)]:
 w=Walker(world,(8.5,6.75,z));ok,tr=go(w,(8.5,8.0));traces['fixed_landing_'+str(fl)]=tr
 ck('Cross the repaired gray landing threshold F'+str(fl),ok and w.grounded and all(abs(p[2]-z)<.01 for p in tr),position=list(w.p))
w=Walker(world,(4.6,6.4,7.05));ok,tr=go(w,(1.7,6.4));traces['f3_terrace_entry']=tr
ck('Enter the F3 terrace through the flush original doorway',ok and w.grounded and abs(w.p.z-7.05)<.01,position=list(w.p))
ok,tr=go(w,(1.7,1.7),limit=9.);traces['f3_terrace_level_walk']=tr
ck('Walk the entire repaired terrace without an overlay step',ok and w.grounded and all(abs(p[2]-7.05)<.01 for p in tr),position=list(w.p))
w=Walker(world,(11.4,-15.7,-.4));ok,tr=go(w,(14.0,-15.7),limit=8.);traces['fixed_storage_gallery_join']=tr
ck('Cross the repaired storage passage and gallery flush join',ok and w.grounded and all(p[2]>-.45 for p in tr),position=list(w.p))

# Cross the recovered photographed ramp at four separate positions, in both
# directions, using the same capsule and gravity as the delivered runtime.
import math
P0=Vector((-14.8813,-8.4793,0));P1=Vector((-12.5895,-12.7096,0));u=(P1-P0).normalized();inward=Vector((-u.y,u.x,0))
for s in [0.9,1.9,2.9,3.9]:
 a=P0+u*s-inward*1.6;b=P0+u*s+inward*1.8
 w=Walker(world,(a.x,a.y,-.8));recoveries=w.recoveries;ok,tr=go(w,(b.x,b.y),limit=8.);traces['source_ramp_in_'+str(s)]=tr
 ck('Original photographed ramp enters continuously at station '+str(s),ok and w.grounded and w.recoveries==recoveries,position=list(w.p),recoveries=w.recoveries)
 ok,tr=go(w,(a.x,a.y),limit=8.);traces['source_ramp_out_'+str(s)]=tr
 ck('Original photographed ramp exits continuously at station '+str(s),ok and w.grounded and w.recoveries==recoveries,position=list(w.p),recoveries=w.recoveries)
a=P0+u*2.5-inward*.6;w=Walker(world,(a.x,a.y,-1.));z0=w.p.z;peak=z0
for i in range(150):w.update((0,0),1/60,jump=i==0);peak=max(peak,w.p.z)
ck('Jump lands on the recovered photographic ramp',w.grounded and w.recoveries==0 and abs(w.p.z-z0)<.01 and peak-z0>.5,position=list(w.p),jump_height_m=peak-z0)
headroom=[]
for key,trace in traces.items():
 if not key.startswith(('ascend_floor_','descend_floor_')):continue
 for p in trace:
  hit,no,index,dist=world.bvh.ray_cast(Vector((p[0],p[1],p[2]+.025)),Vector((0,0,1)),10.)
  if hit is not None:headroom.append(float(hit.z-p[2]))
ck('Actual stair route overhead clearance is at least 2.20m',headroom and min(headroom)>=2.20,minimum_vertical_clearance_m=min(headroom) if headroom else None,sampled_positions=len(headroom))

# Cross the original inner gate over its retained stone threshold.
w=Walker(world,(6.6,-12.55,-.5));recoveries=w.recoveries;ok,tr=go(w,(6.6,-10.0),limit=8.);traces['inner_gate_in']=tr
ck('Walk through the inner gate over its retained threshold',ok and w.grounded and w.recoveries==recoveries,position=list(w.p),recoveries=w.recoveries)
ok,tr=go(w,(6.6,-12.55),limit=8.);traces['inner_gate_out']=tr
ck('Return through the inner gate without a floor snag or recovery',ok and w.grounded and w.recoveries==recoveries,position=list(w.p),recoveries=w.recoveries)
# Trace the gate approach outside the projecting waist's 215mm capsule envelope.
# The five direct support rays in Native_QA separately inspect the exposed pads.
for label,a,b in [('left_apron',(4.40,-12.30),(5.20,-12.30)),('right_apron',(8.80,-12.30),(8.00,-12.30))]:
 w=Walker(world,(*a,-.50));rec=w.recoveries;ok,tr=go(w,b,limit=6.);traces['gate_'+label]=tr
 ck('Ground beside reduced gate apron remains continuously supported '+label,ok and w.grounded and w.recoveries==rec and all(p[2]>-.72 for p in tr),position=list(w.p),recoveries=w.recoveries)
# Actual MB7 ground, outside the reconstructed court. Select broad upward
# triangles and verify a short walk using the same capsule and BVH.
vv=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',vv);vv=vv.reshape(-1,3);ff=np.empty(len(me.loop_triangles)*3,np.int32);me.loop_triangles.foreach_get('vertices',ff);ff=ff.reshape(-1,3);index=json.loads((R/'V26_18_Collision_Index.json').read_text('utf8'))['objects'];candidates=[]
for rr in index:
 if not rr['name'].startswith('V24_34_MB7_'):continue
 ix=np.arange(rr['first_triangle'],rr['first_triangle']+rr['triangles']);t=vv[ff[ix]];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(no,axis=1)/2;cent=t.mean(1);mask=(no[:,2]>area*1.7)&(area>.035)&(cent[:,2]<5.)&(cent[:,2]>-16.)&((cent[:,0]<-25.5)|(cent[:,0]>22.)|(cent[:,1]<-20.)|(cent[:,1]>13.))
 for j in np.flatnonzero(mask):candidates.append((float(area[j]),int(ix[j]),rr['name']))
chosen=[]
for area,j,n in sorted(candidates,reverse=True):
 t=vv[ff[j]];c=t.mean(0)
 if any(np.linalg.norm(c[:2]-p[:2])<1.5 for p in chosen):continue
 w=Walker(world,(float(c[0]),float(c[1]),float(c[2]+.12)))
 if not w.grounded or not world.clear(w.p):continue
 chosen.append(c);d=t[0,:2]-c[:2];d=d/max(np.linalg.norm(d),1e-9)*.24;target=c[:2]+d;recoveries=w.recoveries;ok,tr=go(w,target,limit=3.);traces['MB7_ground_'+str(len(chosen))]=tr
 ck('MB7 exterior walkable surface supports a short capsule walk '+str(len(chosen)),ok and w.grounded and w.recoveries==recoveries,source=n,start=c.tolist(),position=list(w.p),recoveries=w.recoveries)
 if len(chosen)>=4:break
ck('Four separated MB7 exterior walkable patches were inspected',len(chosen)>=4,available_upward_triangles=len(candidates),inspected=len(chosen))
# Direct capsule passages through the newly full-depth interior door linings.
for fl,z in [(1,-.45),(2,3.4500244)]:
 for label,a,b in [('left_bed',(4.6,2.85),(3.2,2.85)),('right_bed',(8.4,2.85),(10.,2.85)),('left_bath',(1.5,8.05),(2.7,8.05))]:
  w=Walker(world,(*a,z));rec=w.recoveries;ok,tr=go(w,b);traces['finished_frame_F'+str(fl)+'_'+label]=tr
  ck('Full-depth finished door passage F'+str(fl)+' '+label,ok and w.grounded and w.recoveries==rec,position=list(w.p),recoveries=w.recoveries)
for label,a,b,z in [('F3_bedroom',(8.3,6.6),(10.,6.6),7.05),('F3_study',(8.4,5.1),(8.4,6.7),7.05),('F3_bath',(10.1,8.05),(11.5,8.05),7.05),('F1_right_corrected_glass',(11.1,6.5),(11.1,8.1),-.45)]:
 w=Walker(world,(*a,z));rec=w.recoveries;ok,tr=go(w,b);traces['new_door_'+label]=tr
 ck('Saved corrected door passage '+label,ok and w.grounded and w.recoveries==rec,position=list(w.p),recoveries=w.recoveries)
for label,x,z in [('F1_left',3.05,-.45),('F2_left',3.05,3.4500244),('F2_right',9.95,3.4500244),('F3_right',9.95,7.05)]:
 w=Walker(world,(x,6.70,z));rec=w.recoveries;ok,tr=go(w,(x,8.90));traces['aligned_wc_return_in_'+label]=tr
 ck('Enter room passage beside corrected WC return '+label,ok and w.grounded and w.recoveries==rec and abs(w.p.z-z)<.01,position=list(w.p),recoveries=w.recoveries)
 ok,tr=go(w,(x,6.70));traces['aligned_wc_return_out_'+label]=tr
 ck('Return past corrected WC corner '+label,ok and w.grounded and w.recoveries==rec and abs(w.p.z-z)<.01,position=list(w.p),recoveries=w.recoveries)
for label,a,b in [('gate_wall_return',(8.55,-11.38),(9.15,-11.38)),('storage_door',(16.0,-15.15),(16.0,-13.5))]:
 w=Walker(world,(*a,-.4));rec=w.recoveries;ok,tr=go(w,b,limit=6.);traces['V26_18_'+label+'_in']=tr
 ck('New repair remains walkable with level support '+label,ok and w.grounded and w.recoveries==rec and all(abs(p[2]+.4)<.008 for p in tr),position=list(w.p),recoveries=w.recoveries)
 ok,tr=go(w,a,limit=6.);traces['V26_18_'+label+'_out']=tr
 ck('Return through repaired area without a snag '+label,ok and w.grounded and w.recoveries==rec,position=list(w.p),recoveries=w.recoveries)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[r for r in checks if not r['pass']];out={'status':'PASS_ACTUAL_MODEL_ROAM_PHYSICS'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail,'trajectory_samples':traces,'test_seconds':time.perf_counter()-start};(R/'V26_18_Interior_Physics_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('V21_PHYSICS_QA',len(checks),'FAIL',len(fail),'SECONDS',out['test_seconds'],flush=True)

