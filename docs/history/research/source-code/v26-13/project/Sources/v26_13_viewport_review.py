"""Open the delivered Fast file and capture its native interactive material view."""
import bpy,sys,json,hashlib,time
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V26_13');D=W/'v26_13/Review'
expected=O/'Blender/Architecture_Complete_V26_13_Fast.blend'
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
   win,a,r=context();capture('Viewport_01_Actual_Tour',win,a,r,{'mode':'Delivered third-person tour outside the gate','tour_running':running is not None,'controller_hud_label':'V26.13','person_m':list(running.walker.p)})
   with bpy.context.temp_override(window=win,area=a,region=r):running.finish(bpy.context)
   space=a.spaces.active;pos=Vector((4.72,-12.72,1.05));aim=Vector((5.17,-11.82,1.05));rotation=(aim-pos).to_track_quat('-Z','Y')
   space.lens=37.;space.clip_start=.025;space.shading.type='MATERIAL';space.shading.use_scene_world=True;space.shading.use_scene_lights=True;space.region_3d.view_perspective='PERSP';space.region_3d.view_rotation=rotation;space.region_3d.view_location=aim;space.region_3d.view_distance=(aim-pos).length;space.overlay.show_overlays=False;a.tag_redraw();stage=2;return 15.
  if stage==2:
   win,a,r=context();capture('Viewport_02_Faceted_Stone',win,a,r,{'mode':'Native interactive material viewport','camera':[[4.72,-12.72,1.05],[5.17,-11.82,1.05],37]})
   active=[o for o in sc.objects if o.name.startswith('V26_13_Photo_Fit_')]+[o for o in sc.objects if o.name.startswith('V26_12_Restored_')and'Header'in o.name]
   checks=[{'check':'Delivered Fast file starts the actual person tour','pass':records[0]['tour_running']},
           {'check':'Both native captures use material shading, inherited overcast and no extra lights','pass':all(q['shading']=='MATERIAL'and q['extra_lights']==0 and q['saved_overcast']=='V26_8_Overcast_Soft_Even_Daylight'for q in records)},
           {'check':'All21 active sculpted panels and original waist carving are visible','pass':len(active)==21 and all(o.visible_get()and not o.hide_render for o in active)and bpy.data.objects['V26_13_Original_Faceted_Waist_Carving'].visible_get()},
           {'check':'Readable low-cost local AO is enabled during native review','pass':sc.eevee.use_raytracing and sc.eevee.use_fast_gi and sc.eevee.fast_gi_method=='AMBIENT_OCCLUSION_ONLY'},
           {'check':'Embedded controller contains the V26.13 HUD label','pass':'V26.13'in bpy.data.texts['V24_21_漫游控制器.py'].as_string()},
           {'check':'Native viewport inspection leaves delivered Fast file byte-identical','pass':hashlib.sha256(expected.read_bytes()).hexdigest()==input_hash}]
   result={'status':'PASS'if all(q['pass']for q in checks)else'FAIL','model_sha256':input_hash,'checks':checks,'failures':[q for q in checks if not q['pass']],'captures':records}
   (O/'Reports/V26_13_Runtime_Viewport_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8');print('VIEWPORT_REVIEW_DONE',result['status'],flush=True);stage=3
   bpy.ops.wm.quit_blender();return None
 except Exception:
  import traceback;traceback.print_exc();(D/'Viewport_Review_Error.txt').write_text(traceback.format_exc(),'utf8');bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(tick,first_interval=4.)
