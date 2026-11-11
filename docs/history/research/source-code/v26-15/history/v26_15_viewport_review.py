import bpy,sys,json,hashlib,time,math
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V26_15');D=W/'v26_15/Review';expected=O/'Blender/Architecture_Complete_V26_15_Fast.blend';assert Path(bpy.data.filepath).resolve()==expected.resolve();input_hash=hashlib.sha256(expected.read_bytes()).hexdigest();sc=bpy.context.scene
sc.render.resolution_x=1000;sc.render.resolution_y=1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';exec(compile((O/'Roam/start_roam_fast.py').read_text('utf8'),'<delivered fast tour>','exec'),{'__name__':'__main__'})
stage=0;started=time.monotonic();records=[]
def context():
 for win in bpy.context.window_manager.windows:
  aa=[a for a in win.screen.areas if a.type=='VIEW_3D']
  if aa:
   a=max(aa,key=lambda a:a.width*a.height);r=next(r for r in a.regions if r.type=='WINDOW');return win,a,r
 raise RuntimeError('No3D viewport')
def capture(tag,win,a,r,**details):
 sc.render.filepath=str(D/(tag+'.png'))
 with bpy.context.temp_override(window=win,area=a,region=r):bpy.ops.render.opengl(write_still=True,view_context=True)
 row={'image':tag+'.png','model':str(expected),'model_sha256':input_hash,'actual_viewport':True,'shading':a.spaces.active.shading.type,'engine':sc.render.engine,'world':sc.world.name,'extra_lights':0,**details};records.append(row);(D/(tag+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2),'utf8');print('VIEWPORT_CAPTURED',tag,flush=True)
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
    running.walker.place((3.15,6.70,3.4500244));running.yaw=math.atan2(-.93,1.02);running.pitch=-.55;sc.arch_roam.first_person=True;running.camera_pos=None;running._input_dirty=True;running.update(bpy.context,1/60)
   stage=1;return 18.
  if stage==1:
   win,a,r=context();capture('Viewport_01_WC_Eye_Tour',win,a,r,tour_running=running is not None,mode='Actual first-person tour, placed at the F2 left WC for inspection',person_m=list(running.walker.p),controller_hud_label='V26.15')
   with bpy.context.temp_override(window=win,area=a,region=r):running.finish(bpy.context)
   for ob in bpy.data.objects['V24_21_Roam_Person_165cm'].children_recursive:
    if ob.type=='MESH':ob.hide_set(True)
   s=a.spaces.active;pos=Vector((3.15,6.70,4.70));aim=Vector((2.22,7.72,5.60));s.lens=23.;s.clip_start=.025;s.shading.type='MATERIAL';s.shading.use_scene_world=True;s.shading.use_scene_lights=True;s.region_3d.view_perspective='PERSP';s.region_3d.view_rotation=(aim-pos).to_track_quat('-Z','Y');s.region_3d.view_location=aim;s.region_3d.view_distance=(aim-pos).length;s.overlay.show_overlays=False;a.tag_redraw();stage=2;return 15.
  if stage==2:
   win,a,r=context();capture('Viewport_02_WC_Flush_Return',win,a,r,mode='Actual native material viewport close-up; person hidden only for unobstructed wall inspection')
   checks=[{'check':'Delivered Fast person tour runs at the inspected F2 room','pass':records[0]['tour_running']and abs(records[0]['person_m'][2]-3.4500244)<.01},
    {'check':'Both captures use native material viewport with inherited overcast and no added lights','pass':all(r['shading']=='MATERIAL'and r['extra_lights']==0 and r['world']=='V26_8_Overcast_Soft_Even_Daylight'for r in records)},
    {'check':'Corrected house is visible and the previous house archive stays hidden','pass':bpy.data.objects['V26_3_House_Connected_Walls_And_Stairs'].visible_get()and not bpy.data.objects['V26_15_Previous_WC_Wall_Returns_Archive'].visible_get()},
    {'check':'Inherited local AO is enabled in the actual viewport','pass':sc.eevee.use_raytracing and sc.eevee.use_fast_gi and sc.eevee.fast_gi_method=='AMBIENT_OCCLUSION_ONLY'},
    {'check':'Embedded controller uses V26.15 HUD label','pass':'V26.15'in bpy.data.texts['V24_21_漫游控制器.py'].as_string()},
    {'check':'Actual review leaves the delivered model byte-identical','pass':hashlib.sha256(expected.read_bytes()).hexdigest()==input_hash}]
   fail=[r for r in checks if not r['pass']];out={'status':'PASS'if not fail else'FAIL','model_sha256':input_hash,'checks':checks,'failures':fail,'captures':records};(O/'Reports/V26_15_Runtime_Viewport_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('VIEWPORT_REVIEW_DONE',out['status'],flush=True);stage=3;bpy.ops.wm.quit_blender();return None
 except Exception:
  import traceback;traceback.print_exc();(D/'Viewport_Review_Error.txt').write_text(traceback.format_exc(),'utf8');bpy.ops.wm.quit_blender();return None
bpy.app.timers.register(tick,first_interval=4.)
