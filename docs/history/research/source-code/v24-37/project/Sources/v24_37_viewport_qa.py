"""Read-only native material-preview captures in a separate Blender window."""
import bpy,time,json,hashlib,traceback
from pathlib import Path
from mathutils import Vector
R=Path('E:/jz/JIA/Rebuild_V24_37/Reports');stage=0;ready=0.;started=time.perf_counter();rows=[];errors=[];jobs=[('V24_35_01_Kitchen_East','A'),('V24_35_01_Kitchen_East','B'),('V24_37_02_House_And_PTJIA6','A'),('V24_37_02_House_And_PTJIA6','B'),('V24_37_04_PTJIA6_Road_Eye','A'),('V24_37_05_PTJIA6_Field_Context','A')]
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def finish():
 out={'status':'CAPTURED_PENDING_VISUAL_REVIEW'if not errors and len(rows)==len(jobs)else'FAIL','model_sha256':sha(bpy.data.filepath),'mode':'Blender native MATERIAL preview OpenGL, studio lighting','captures':rows,'checks':[],'failures':errors}
 (R/'V24_37_Viewport_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('V31_VIEWPORT_CAPTURED',len(rows),errors,flush=True);bpy.ops.wm.quit_blender()
def tick():
 global stage,ready,win,area,region,space,c,original
 try:
  if stage==0:
   win=bpy.context.window_manager.windows[0];area=max((a for a in win.screen.areas if a.type=='VIEW_3D'),key=lambda a:a.width*a.height);region=next(r for r in area.regions if r.type=='WINDOW');space=area.spaces.active;space.overlay.show_overlays=False;space.show_gizmo=False;space.shading.type='MATERIAL';space.shading.use_scene_world=False;space.shading.use_scene_lights=False;space.clip_start=.035;space.clip_end=2000.;sc=bpy.context.scene;sc.render.resolution_x=1280;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.frame_set(40);stage=1
  i=(stage-1)//2
  if i>=len(jobs):finish();return None
  tag,pose=jobs[i]
  if stage%2==1:
   c=bpy.data.objects[tag];original=c.matrix_world.copy()
   if pose=='B':c.location+=Vector((.045,.025,.004))
   bpy.context.scene.camera=c;space.region_3d.view_perspective='CAMERA';space.region_3d.view_camera_zoom=0.;space.region_3d.view_camera_offset=(0,0);area.tag_redraw();bpy.context.view_layer.update();ready=time.perf_counter();stage+=1;return 12. if i==0 else 4.
  name='V24_37_Viewport_'+tag+'_'+pose+'.png';bpy.context.scene.render.filepath=str(R/name)
  with bpy.context.temp_override(window=win,area=area,region=region):bpy.ops.render.opengl(write_still=True,view_context=True)
  assert (R/name).stat().st_size>20000,name
  rows.append({'file':name,'camera':c.name,'pose':pose,'camera_matrix':[list(r)for r in c.matrix_world],'bytes':(R/name).stat().st_size});c.matrix_world=original;print('VIEWPORT_DONE',name,flush=True);stage+=1;return .3
 except Exception:errors.append(traceback.format_exc());finish();return None
bpy.app.timers.register(tick,first_interval=3.)
