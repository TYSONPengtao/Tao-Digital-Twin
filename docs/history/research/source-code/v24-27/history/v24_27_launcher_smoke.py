import bpy,sys,time,json,hashlib,traceback,math
from pathlib import Path
from mathutils import Vector
from bpy_extras import view3d_utils
R=Path('E:/jz/JIA/Rebuild_V24_27/Reports');started=time.perf_counter();stage=0;checks=[];errors=[];click_index=0
def digest(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('CHECK',n,bool(p),kw,flush=True)
def key(n,v='PRESS'):win.event_simulate(type=n,value=v,x=region.x+region.width//2,y=region.y+region.height//2)
def tap(n):key(n);key(n,'RELEASE')
def click_world(p):
 xy=view3d_utils.location_3d_to_region_2d(region,op.region3d,Vector(p));assert xy is not None and 0<xy.x<region.width and 0<xy.y<region.height,('Point outside viewport',p,xy)
 for v in ['PRESS','RELEASE']:win.event_simulate(type='LEFTMOUSE',value=v,x=int(region.x+xy.x),y=int(region.y+xy.y))
def finish():
 fail=[c for c in checks if not c['pass']];ok=not fail and not errors and stage==9
 (R/'V24_27_Launcher_QA.json').write_text(json.dumps({'status':'PASS_REAL_LAUNCHER_AND_SURFACE_MEASURE_UI'if ok else'FAIL','model_sha256':digest(bpy.data.filepath),'bootstrap_sha256':digest(R.parent/'Roam/start_roam.py'),'checks':checks,'failures':fail,'errors':errors},ensure_ascii=False,indent=2),encoding='utf8');print('V25_GUI_TEST',ok,errors,flush=True);bpy.ops.wm.quit_blender()
def tick():
 global stage,win,area,region,mod,op,at,initial,points,click_index,move_start
 try:
  now=time.perf_counter()
  if stage==0:
   mod=sys.modules.get('architecture_roam_controller');op=mod._running if mod else None
   if op is None:
    if now-started>50:raise RuntimeError('Startup failed')
    return .5
   win=op.window;area=op.area;region=next(r for r in area.regions if r.type=='WINDOW');ck('Dedicated launcher enters roam and measurement runtime',hasattr(op,'measure')and len(win.screen.areas)==1)
   op.scene.arch_roam.first_person=False;op.scene.arch_roam.distance=5.;op.pitch=math.radians(55);op.yaw=0.;initial=op.walker.p.copy();tap('L');stage=1;at=now;return .8
  op=mod._running
  if stage==1:
   ck('L enters length tool',op.measure.mode=='LENGTH');key('UP_ARROW');stage=2;at=now;return .4
  if stage==2:
   key('UP_ARROW','RELEASE');ck('Measurement mode freezes walking while selecting', (op.walker.p-initial).length<.003)
   x,y,z=op.walker.p;points=[(x-.7,y+.3,z),(x+.7,y+.3,z)];click_index=0;stage=3;return .2
  if stage==3:
   if click_index<len(points):click_world(points[click_index]);click_index+=1;return .35
   rs=op.measure.records;ck('Two actual viewport clicks measure length',len(rs)==1 and abs(rs[0]['length_m']-1.4)<.035,result=rs[-1]if rs else None);tap('P');stage=4;click_index=0;x,y,z=op.walker.p;points=[(x-.7,y-.5,z),(x+.7,y-.5,z),(x+.7,y+.5,z),(x-.7,y+.5,z)];return .3
  if stage==4:
   if click_index<len(points):click_world(points[click_index]);click_index+=1;return .35
   tap('RET');stage=5;return .4
  if stage==5:
   rs=op.measure.records;ck('Four viewport clicks and Enter measure area',len(rs)==2 and abs(rs[-1].get('horizontal_area_m2',0)-1.4)<.045,result=rs[-1]if rs else None)
   measure=sys.modules['architecture_roam_measure'];measure.export_records(rs,R/'V24_27_Measure_Viewport_Demo.csv');ck('Viewport results persist in scene history',len(measure.read_records(op.scene))==2)
   sc=op.scene;sc.render.resolution_x=1400;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
   with bpy.context.temp_override(window=win,area=area,region=region):bpy.ops.screen.screenshot(filepath=str(R/'V24_27_Measure_UI.png'),check_existing=False)
   tap('BACK_SPACE');stage=6;return .4
  if stage==6:
   ck('Undo removes most recent measurement',len(op.measure.records)==1);tap('ESC');stage=7;return .3
  if stage==7:
   ck('First Esc returns to roam without closing the tour',op is not None and op.measure.mode=='OFF');move_start=op.walker.p.copy();key('UP_ARROW');stage=8;at=now;return .4
  if stage==8:
   key('UP_ARROW','RELEASE');ck('Arrow walking resumes after measurement', (op.walker.p-move_start).length>.15);tap('V');stage=81;return .4
  if stage==81:
   ck('V still enters human eye view',op.scene.arch_roam.first_person and abs(op.camera.location.z-op.walker.p.z-1.53)<.002);tap('V');tap('ESC');stage=82;return .4
  if stage==82:
   ck('Esc exits the tour normally',mod._running is None);tap('F8');stage=83;at=now;return .6
  if stage==83:
   if mod._running is None and now-at<15:return .4
   op=mod._running;ck('F8 restores tour and saved measurement history',op is not None and len(op.measure.records)==1)
   with bpy.context.temp_override(window=win,area=area,region=region):bpy.ops.arch_roam.measure_mode(mode='AREA')
   ck('Header area button operator starts the same tool',op.measure.mode=='AREA')
   with bpy.context.temp_override(window=win,area=area,region=region):bpy.ops.arch_roam.measure_mode(mode='OFF')
   stage=9;finish();return None
 except Exception:errors.append(traceback.format_exc());finish();return None
bpy.app.timers.register(tick,first_interval=3.)
