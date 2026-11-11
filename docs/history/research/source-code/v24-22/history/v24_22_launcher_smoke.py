"""Exercise the real external launcher bootstrap, not a test-only controller load."""
import bpy,sys,time,json,hashlib,traceback
from pathlib import Path
R=Path('E:/jz/JIA/Rebuild_V24_22/Reports')
BOOT=R.parent/'Roam/start_roam.py'
started=time.perf_counter();stage=0;checks=[];errors=[]
def digest(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def check(name,value,**details):checks.append({'check':name,'pass':bool(value),**details})
def key(name,value='PRESS'):win.event_simulate(type=name,value=value,x=area.x+area.width//2,y=area.y+area.height//2)
def tap(name):key(name);key(name,'RELEASE')
def finish():
 failures=[c for c in checks if not c['pass']]
 result={'status':'PASS_REAL_LAUNCHER_ENTRY'if len(checks)==8 and not failures and not errors else'FAIL','model_sha256':digest(bpy.data.filepath),'bootstrap_sha256':digest(BOOT),'checks':checks,'failures':failures,'errors':errors}
 (R/'V24_22_Launcher_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 print('LAUNCHER_TEST',result['status'],errors,flush=True);bpy.ops.wm.quit_blender()
def tick():
 global stage,win,area,region,mod,initial,stage_at
 try:
  now=time.perf_counter()
  if stage==0:
   mod=sys.modules.get('architecture_roam_controller')
   if mod is None or mod._running is None:
    if now-started>40:raise RuntimeError('External startup did not enter roam')
    return .5
   op=mod._running;win=op.window;area=op.area;region=next(r for r in area.regions if r.type=='WINDOW')
   check('External startup starts the actual embedded controller',op is not None)
   check('Dedicated viewport hides timeline and other editors',len(win.screen.areas)==1 and area.type=='VIEW_3D')
   check('Factory startup avoids unrelated add-on startup','blender_mcp'not in sys.modules)
   initial=op.walker.p.copy();key('UP_ARROW');stage=1;stage_at=now;return .1
  op=mod._running
  if stage==1:
   if now-stage_at<.65:return .1
   key('UP_ARROW','RELEASE');moved=(op.walker.p-initial).length
   check('Arrow moves the person without keyframe jumping',moved>.35 and bpy.context.scene.frame_current==40,moved_m=moved)
   tap('V');stage=2;return .4
  if stage==2:
   check('V enters human eye view after launcher start',bpy.context.scene.arch_roam.first_person and abs(op.camera.location.z-op.walker.p.z-1.53)<.002)
   tap('V');stage=3;return .4
  if stage==3:
   check('V returns to third person',not bpy.context.scene.arch_roam.first_person)
   sc=bpy.context.scene;sc.render.resolution_x=1200;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(R/'V24_22_Launcher_UI.png')
   with bpy.context.temp_override(window=win,area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
   tap('ESC');stage=4;return .4
  if stage==4:
   check('Esc exits normally',mod._running is None)
   tap('F8');stage=5;stage_at=now;return .5
  if stage==5:
   if mod._running is None and now-stage_at<20:return .5
   check('F8 re-enters after explicit controller load',mod._running is not None)
   finish();return None
 except Exception:
  errors.append(traceback.format_exc());finish();return None
bpy.app.timers.register(tick,first_interval=3.)
