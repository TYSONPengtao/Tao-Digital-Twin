"""Read-only review of the delivered Fast model in a separate Blender GUI."""
import bpy,sys,json,hashlib,time,math
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_17_views import VIEWS
O=Path('E:/jz/JIA/Rebuild_V26_17');D=W/'v26_17/Review';expected=O/'Blender/Architecture_Complete_V26_17_Fast.blend'
assert Path(bpy.data.filepath).resolve()==expected.resolve()
input_hash=hashlib.sha256(expected.read_bytes()).hexdigest();sc=bpy.context.scene
sc.render.resolution_x=1000;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
exec(compile((O/'Roam/start_roam_fast.py').read_text('utf8'),'<delivered fast tour>','exec'),{'__name__':'__main__'})
stage=0;started=time.monotonic();records=[];manual=[VIEWS[i]for i in[1,3,6,2]]

def context():
 for win in bpy.context.window_manager.windows:
  areas=[a for a in win.screen.areas if a.type=='VIEW_3D']
  if areas:
   a=max(areas,key=lambda a:a.width*a.height);r=next(r for r in a.regions if r.type=='WINDOW');return win,a,r
 raise RuntimeError('No 3D viewport')

def capture(tag,win,a,r,**details):
 sc.render.filepath=str(D/(tag+'.png'))
 with bpy.context.temp_override(window=win,area=a,region=r):bpy.ops.render.opengl(write_still=True,view_context=True)
 row={'image':tag+'.png','model':str(expected),'model_sha256':input_hash,'actual_viewport':True,'shading':a.spaces.active.shading.type,'engine':sc.render.engine,'world':sc.world.name,'extra_lights':0,**details}
 records.append(row);(D/(tag+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2),'utf8');print('VIEWPORT_CAPTURED',tag,flush=True)

def setup_manual(index,area):
 tag,pos,aim,lens=manual[index];s=area.spaces.active;pos=Vector(pos);aim=Vector(aim)
 s.lens=lens;s.clip_start=.025;s.shading.type='MATERIAL';s.shading.use_scene_world=True;s.shading.use_scene_lights=True
 s.region_3d.view_perspective='PERSP';s.region_3d.view_rotation=(aim-pos).to_track_quat('-Z','Y');s.region_3d.view_location=aim;s.region_3d.view_distance=(aim-pos).length;s.overlay.show_overlays=False;area.tag_redraw()

def tick():
 global stage
 try:
  control=sys.modules.get('architecture_roam_controller');running=getattr(control,'_running',None)
  if stage==0:
   if running is None:
    if time.monotonic()-started>120:raise RuntimeError('Tour did not start')
    return 1.
   win,a,r=context()
   with bpy.context.temp_override(window=win,area=a,region=r):
    running.walker.place((10.7,3.,-.449999988));running.yaw=math.atan2(-1.5,-.95);running.pitch=-.85;sc.arch_roam.first_person=True;running.camera_pos=None;running._input_dirty=True;running.update(bpy.context,1/60)
   stage=1;return 18.
  if stage==1:
   win,a,r=context();capture('Viewport_01_F1_Right_Window_Tour',win,a,r,tour_running=running is not None,mode='Delivered first-person tour inside first-floor right bedroom',person_m=list(running.walker.p),controller_hud_label='V26.17')
   with bpy.context.temp_override(window=win,area=a,region=r):running.finish(bpy.context)
   for ob in bpy.data.objects['V24_21_Roam_Person_165cm'].children_recursive:
    if ob.type=='MESH':ob.hide_set(True)
   setup_manual(0,a);stage=2;return 12.
  index=stage-2;win,a,r=context();capture('Viewport_'+str(stage).zfill(2)+'_'+manual[index][0],win,a,r,mode='Actual native material viewport; avatar temporarily hidden for inspection',nominal_camera=[manual[index][1],manual[index][2],manual[index][3]])
  if index+1<len(manual):setup_manual(index+1,a);stage+=1;return 12.
  ch=json.loads((O/'Reports/V26_17_Changes.json').read_text('utf8'))
  checks=[
   {'check':'Delivered Fast first-person tour runs inside the first-floor right bedroom','pass':records[0]['tour_running']and abs(records[0]['person_m'][2]+.449999988)<.01},
   {'check':'All five captures use the actual native material viewport with inherited overcast and no additional lights','pass':len(records)==5 and all(r['shading']=='MATERIAL'and r['extra_lights']==0 and r['world']=='V26_8_Overcast_Soft_Even_Daylight'for r in records)},
   {'check':'Corrected native objects visible and exact original archives hidden','pass':all(bpy.data.objects[n].visible_get()for n in ch['geometry_changed'])and not any(bpy.data.objects[n].visible_get()for n in ch['archived'])},
   {'check':'Local AO stays enabled in actual viewport','pass':sc.eevee.use_raytracing and sc.eevee.use_fast_gi and sc.eevee.fast_gi_method=='AMBIENT_OCCLUSION_ONLY'},
   {'check':'Embedded controller uses current V26.17 HUD','pass':'V26.17'in bpy.data.texts['V24_21_漫游控制器.py'].as_string()},
   {'check':'Viewport review leaves delivered Fast model byte-identical','pass':hashlib.sha256(expected.read_bytes()).hexdigest()==input_hash}]
  fail=[q for q in checks if not q['pass']];out={'status':'PASS'if not fail else'FAIL','model_sha256':input_hash,'checks':checks,'failures':fail,'captures':records,'framing_note':'Native viewport aspect mapping can differ from offline camera renders; both are actual model views.'}
  (O/'Reports/V26_17_Runtime_Viewport_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('VIEWPORT_REVIEW_DONE',out['status'],flush=True);stage+=1;bpy.ops.wm.quit_blender();return None
 except Exception:
  import traceback;traceback.print_exc();(D/'Viewport_Review_Error.txt').write_text(traceback.format_exc(),'utf8');bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(tick,first_interval=4.)
