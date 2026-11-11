"""Run an actual Blender modal-operator keyboard smoke test, then exit."""
import bpy,json,time,sys,traceback,types,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('E:/jz/JIA/Rebuild_V24_21/Reports');started=time.perf_counter();stage=0;samples=[];errors=[]
with Path(bpy.data.filepath).open('rb')as f:model_hash=hashlib.file_digest(f,'sha256').hexdigest()
def activate():
 global stage,win,area,region,mod,initial
 try:
  win=bpy.context.window_manager.windows[0];area=max((a for a in win.screen.areas if a.type=='VIEW_3D'),key=lambda a:a.width*a.height);region=next(r for r in area.regions if r.type=='WINDOW');area.spaces.active.shading.type='SOLID'
  for n,t in [('architecture_roam_physics','V24_21_碰撞控制.py'),('architecture_roam_controller','V24_21_漫游控制器.py')]:
   m=types.ModuleType(n);sys.modules[n]=m;exec(compile(bpy.data.texts[t].as_string(),t,'exec'),m.__dict__)
  mod=sys.modules['architecture_roam_controller']
  with bpy.context.temp_override(window=win,area=area,region=region):mod.register();bpy.ops.arch_roam.start('INVOKE_DEFAULT')
  initial=list(mod._running.walker.p)
  try:bpy.ops.blendermcp.start_server()
  except Exception:pass
  bpy.app.timers.register(tick,first_interval=.5);print('UI_SMOKE_STARTED',flush=True)
 except Exception:
  errors.append(traceback.format_exc());finish()
 return None
def press(k):win.event_simulate(type=k,value='PRESS')
def release(k):win.event_simulate(type=k,value='RELEASE')
def capture(name,op):
 sc=bpy.context.scene;sc.render.resolution_x=1200;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(R/(name+'.png'))
 with bpy.context.temp_override(window=win,area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
 (R/(name+'_State.json')).write_text(json.dumps({'model_sha256':model_hash,'file':name+'.png','runtime':True,'person_foot':list(op.walker.p),'camera':list(op.camera.location),'first_person':sc.arch_roam.first_person,'shading':area.spaces.active.shading.type,'method':'Actual running Blender viewport, not a posed render.'},indent=2))
def tick():
 global stage,stage_started
 try:
  now=time.perf_counter();op=mod._running
  if stage==0:
   press('UP_ARROW');stage_started=now;stage=1;return .1
  if stage==1 and now-stage_started>=1.3:
   release('UP_ARROW');samples.append({'event':'forward','position':list(op.walker.p),'camera':list(op.camera.location)})
   try:
    sc=bpy.context.scene;sc.render.resolution_x=1200;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(R/'V24_21_UI_ThirdPerson.png')
    with bpy.context.temp_override(window=win,area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
    (R/'V24_21_UI_ThirdPerson_State.json').write_text(json.dumps({'model_sha256':model_hash,'file':'V24_21_UI_ThirdPerson.png','runtime':True,'person_foot':list(op.walker.p),'camera':list(op.camera.location),'method':'Actual running Blender viewport after simulated keyboard input, Workbench preview.'},indent=2))
   except Exception:errors.append(traceback.format_exc())
   press('SPACE');release('SPACE');stage_started=time.perf_counter();stage=2;return .1
  if stage==2:
   samples.append({'event':'jump_sample','position':list(op.walker.p)})
   if now-stage_started<1.3:return .10
   press('V');release('V');stage_started=now;stage=3;return .3
  if stage==3:
   samples.append({'event':'first_person','enabled':bpy.context.scene.arch_roam.first_person,'camera_height':op.camera.location.z-op.walker.p.z});press('V');release('V');press('RIGHT_ARROW');stage_started=now;stage=4;return .1
  if stage==4 and now-stage_started>=.8:
   release('RIGHT_ARROW');samples.append({'event':'right','position':list(op.walker.p)});press('HOME');release('HOME');stage_started=now;stage=5;return .5
  if stage==5:
   samples.append({'event':'home','position':list(op.walker.p)});press('M');release('M');stage=6;return 3.
  if stage==6:
   samples.append({'event':'material','mode':area.spaces.active.shading.type});capture('V24_21_UI_Material_ThirdPerson',op);press('V');release('V');stage=7;return 1.
  if stage==7:
   capture('V24_21_UI_FirstPerson',op);press('ESC');release('ESC');stage=8;return .5
  if stage==8:
   samples.append({'event':'escape','stopped':mod._running is None});finish();return None
  return .1
 except Exception:
  errors.append(traceback.format_exc());finish();return None
def finish():
 checks=[]
 def ck(n,v,**kw):checks.append({'check':n,'pass':bool(v),**kw})
 try:
  fwd=next(s for s in samples if s['event']=='forward');ck('Real Up Arrow events move the modal character',fwd['position'][1]>initial[1]+.5,moved_m=fwd['position'][1]-initial[1]);j=[s['position'][2]for s in samples if s['event']=='jump_sample'];ck('Real Space events trigger a jump',max(j)>fwd['position'][2]+.30)
  first=next(s for s in samples if s['event']=='first_person');ck('V switches to a 1.53m human eye view',first['enabled']and abs(first['camera_height']-1.53)<.002)
  right=next(s for s in samples if s['event']=='right');ck('Real Right Arrow events strafe right',right['position'][0]>fwd['position'][0]+.4)
  home=next(s for s in samples if s['event']=='home');ck('Home restores the courtyard start',(Vector(home['position'])-Vector(initial)).length<.03);ck('Escape exits and restores viewport control',samples[-1].get('stopped',False))
  material=next(s for s in samples if s['event']=='material');ck('M switches to textured material preview',material['mode']=='MATERIAL')
 except Exception:errors.append(traceback.format_exc())
 fail=[r for r in checks if not r['pass']];out={'status':'PASS_REAL_UI_KEYBOARD_SMOKE'if len(checks)==7 and not fail and not errors else'FAIL','model_sha256':model_hash,'initial':globals().get('initial'),'checks':checks,'failures':fail,'samples':samples,'errors':errors};(R/'V24_21_UI_Smoke_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('UI_SMOKE_RESULT',out['status'],errors,flush=True);bpy.ops.wm.quit_blender()
bpy.app.timers.register(activate,first_interval=2.)
