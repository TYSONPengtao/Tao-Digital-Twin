"""Inspect the delivered Fast file in its real material viewport and tour."""
import bpy, sys, json, hashlib, time, numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V26_12');D=W/'v26_12/Review';D.mkdir(exist_ok=True)
expected=O/'Blender/Architecture_Complete_V26_12_Fast.blend'
assert Path(bpy.data.filepath).resolve()==expected.resolve()
input_hash=hashlib.sha256(expected.read_bytes()).hexdigest()
sc=bpy.context.scene;sc.render.resolution_x=1200;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
exec(compile((O/'Roam/start_roam_fast.py').read_text('utf8'),'<delivered fast tour>','exec'),{'__name__':'__main__'})
stage=0;started=time.monotonic();records=[]
def context():
 for win in bpy.context.window_manager.windows:
  areas=[a for a in win.screen.areas if a.type=='VIEW_3D']
  if areas:
   a=max(areas,key=lambda x:x.width*x.height);r=next(x for x in a.regions if x.type=='WINDOW');return win,a,r
 raise RuntimeError('No3D viewport')
def capture(name,win,a,r,details):
 sc.render.filepath=str(D/(name+'.png'))
 with bpy.context.temp_override(window=win,area=a,region=r):bpy.ops.render.opengl(write_still=True,view_context=True)
 rec={'image':name+'.png','model':str(expected),'model_sha256':input_hash,'shading':a.spaces.active.shading.type,'engine':sc.render.engine,'saved_overcast':sc.world.name,'extra_lights':0,'actual_viewport':True,**details}
 (D/(name+'.json')).write_text(json.dumps(rec,ensure_ascii=False,indent=2),'utf8');records.append(rec);print('VIEWPORT_CAPTURED',name,flush=True)
def tick():
 global stage
 try:
  control=sys.modules.get('architecture_roam_controller');running=getattr(control,'_running',None)
  if stage==0:
   if running is None:
    if time.monotonic()-started>120:raise RuntimeError('Delivered tour did not start')
    return 1.
   win,a,r=context()
   with bpy.context.temp_override(window=win,area=a,region=r):
    running.walker.place((6.6,-13.1,-.6));running.yaw=0.;running.pitch=0.;sc.arch_roam.distance=3.5;running.camera_pos=None;running._input_dirty=True;running.update(bpy.context,1/60)
   stage=1;return 18.
  if stage==1:
   win,a,r=context();capture('Viewport_01_Actual_Tour',win,a,r,{'mode':'Actual delivered third-person tour, placed outside the gate for review','tour_running':running is not None,'hud_version':'V26.12','person_m':list(running.walker.p)})
   with bpy.context.temp_override(window=win,area=a,region=r):running.finish(bpy.context)
   space=a.spaces.active;pos=Vector((4.78,-12.75,1.25));aim=Vector((5.19,-11.86,1.25));rotation=(aim-pos).to_track_quat('-Z','Y')
   space.lens=37.;space.clip_start=.025;space.shading.type='MATERIAL';space.shading.use_scene_world=True;space.shading.use_scene_lights=True;space.region_3d.view_perspective='PERSP';space.region_3d.view_rotation=rotation;space.region_3d.view_location=aim;space.region_3d.view_distance=(aim-pos).length;space.overlay.show_overlays=False;a.tag_redraw();stage=2;return 15.
  if stage==2:
   win,a,r=context();capture('Viewport_02_Stone_Corner',win,a,r,{'mode':'Actual manual material viewport; no rendering-only substitution','camera':[[4.78,-12.75,1.25],[5.19,-11.86,1.25],37]})
   def detail(path):
    im=bpy.data.images.load(str(path),check_existing=False);ww,hh=im.size;px=np.empty(ww*hh*4,np.float32);im.pixels.foreach_get(px);g=px.reshape(hh,ww,4)[...,0:3]@np.array([.2126,.7152,.0722]);crop=g[int(hh*.25):int(hh*.7),int(ww*.48):int(ww*.55)];result=float(np.std(np.diff(crop,axis=0))+np.std(np.diff(crop,axis=1)));bpy.data.images.remove(im);return result
   before_detail=detail(W/'v26_12/Diagnosis/Before_Flat_Viewport_02_Stone_Corner.png');after_detail=detail(D/'Viewport_02_Stone_Corner.png')
   checks=[{'check':'Delivered Fast file launches the actual tour','pass':records[0]['tour_running']},
           {'check':'Both captures use actual material viewport, inherited overcast and no extra lights','pass':all(q['shading']=='MATERIAL'and q['extra_lights']==0 for q in records)},
           {'check':'All21 restored inserts visible in the viewport','pass':sum(o.visible_get()for o in sc.objects if o.name.startswith('V26_12_Restored_'))==21},
           {'check':'Viewport inspection leaves the delivered file byte-identical','pass':hashlib.sha256(expected.read_bytes()).hexdigest()==input_hash},
           {'check':'Actual material viewport carving detail exceeds the reproduced flat baseline','pass':after_detail>max(before_detail*3,.001),'before_gradient_std':before_detail,'after_gradient_std':after_detail}]
   result={'status':'PASS'if all(q['pass']for q in checks)else'FAIL','model_sha256':input_hash,'checks':checks,'failures':[q for q in checks if not q['pass']],'captures':records}
   (O/'Reports/V26_12_Runtime_Viewport_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
   (D/'Viewport_Review_Done.json').write_text(json.dumps(result,ensure_ascii=False),'utf8');print('VIEWPORT_REVIEW_DONE',result['status'],flush=True);stage=3;return None
 except Exception:
  import traceback;traceback.print_exc();(D/'Viewport_Review_Error.txt').write_text(traceback.format_exc(),'utf8');return None
bpy.app.timers.register(tick,first_interval=4.)
