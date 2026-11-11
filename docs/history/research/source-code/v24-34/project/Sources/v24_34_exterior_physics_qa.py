from pathlib import Path
import bpy,sys,types,json,hashlib,math,time,numpy as np
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_34';O=Path('E:/jz/JIA/Rebuild_V24_34');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_34.blend';bpy.ops.wm.open_mainfile(filepath=str(P));m=types.ModuleType('architecture_roam_physics');exec(bpy.data.texts['V24_21_碰撞控制.py'].as_string(),m.__dict__);a=np.load(D/'Final_Collision.npz');world=m.World(a['v'].tolist(),a['f'].tolist());checks=[];traces={};start=time.perf_counter()
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('CHECK',n,bool(p),kw,flush=True)
def go(w,p,limit=3.):
 for i in range(int(limit*30)):
  diff=Vector((p[0]-w.p.x,p[1]-w.p.y,0))
  if diff.length<.07:return True
  d=diff.normalized();w.update(d,min(1/30,diff.length/1.85))
 return False
for r in json.loads((D/'Planned_Routes.json').read_text()):
 w=m.Walker(world,r['points'][0]);trace=[list(w.p)];okay=True;blocked=None
 for p in r['points'][1:]:
  if not go(w,p):okay=False;blocked={'target':p,'at':list(w.p)};break
  trace.append(list(w.p))
 traces[r['name']]=trace;ck('Real capsule follows '+r['name'],okay and w.grounded and w.recoveries==0,planned_length_m=r['length_xy_m'],completed_points=len(trace),planned_points=len(r['points']),blocked=blocked,final_position=list(w.p))
 # Repeat selected route support in reverse, including a real old/new seam.
 if okay and 'Seam'in r['name']:
  reverse=True
  for p in r['points'][-2::-1]:
   if not go(w,p):reverse=False;break
  ck('Same old MB7 road seam is walkable in reverse',reverse and w.grounded and w.recoveries==0,final_position=list(w.p))
# The new southern ground is below -12m, a valid height previously reset by
# the controller. It now remains a supported physical location.
south=json.loads((D/'Planned_Routes.json').read_text())[-1]['points'][-1];w=m.Walker(world,south);z0=w.p.z;peak=z0
for i in range(120):w.update((0,0),1/60,jump=i==0);peak=max(peak,w.p.z)
ck('Jump and land on new ground below minus twelve metres',z0<-12 and w.grounded and abs(w.p.z-z0)<.02,ground_z_m=z0,jump_height_m=peak-z0,final_position=list(w.p))
# Actual finite MB7 road boundary, both normal walking and an airborne attempt.
for jumping in [False,True]:
 w=m.Walker(world,(31.,-68.,-15.2));z0=w.p.z;minz=z0
 for i in range(900):w.update((0.,-1.),1/30,jump=jumping and i%60==0,run=True);minz=min(minz,w.p.z)
 for i in range(120):w.update((0,0),1/60)
 ck('Actual exterior boundary stops '+('jumping'if jumping else'walking')+' before missing geometry',w.edge_stops>0 and w.grounded and minz>world.bottom and w.recoveries<3,edge_stops=w.edge_stops,recoveries=w.recoveries,final_position=list(w.p),minimum_z_m=minz)
# Controlled plane and a real open hole isolate safety from complex site shape.
v=[(-2,-2,0),(2,-2,0),(2,2,0),(-2,2,0)];f=[(0,1,2),(0,2,3)];small=m.World(v,f)
for jumping in [False,True]:
 okay=True;recoveries=0
 for k in range(16):
  w=m.Walker(small,(0,0,0));d=(math.cos(k*math.tau/16),math.sin(k*math.tau/16))
  for i in range(300):w.update(d,1/30,jump=jumping and i%50==0,run=True)
  okay &= w.grounded and w.p.z>-.01 and max(abs(w.p.x),abs(w.p.y))<2.25;recoveries+=w.recoveries
 ck('Finite support prevents falls in sixteen directions '+('with jumping'if jumping else'walking'),okay,recoveries=recoveries)
w=m.Walker(small,(0,0,0));w.p.z=-2;w.grounded=False;w.update((0,0),1/60);ck('Lost-support fail-safe restores last validated supported position',w.grounded and w.recoveries==1 and abs(w.p.z)<.005,position=list(w.p))
ck('Architecture runtime has no fixed minus-twelve height reset','p.z<-12'not in bpy.data.texts['V24_21_漫游控制器.py'].as_string())
fail=[r for r in checks if not r['pass']];out={'status':'PASS_ALL_MODEL_EXTERIOR_SUPPORT_AND_EDGE_SAFETY'if not fail else'FAIL','model_sha256':sha(P),'checks':checks,'failures':fail,'route_traces':traces,'seconds':time.perf_counter()-start};(R/'V24_34_Exterior_Physics_QA.json').write_text(json.dumps(out,indent=2));print('EXTERIOR_QA',len(checks),'FAIL',len(fail),flush=True)
