import bpy,json,hashlib,sys,shutil
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_18/Window_Frames';D.mkdir(exist_ok=True);R=Path('E:/jz/JIA/Rebuild_V24_18/Reports');P=R.parent/'Blender/Architecture_Complete_V24_18.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=960;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.fps=12;sc.camera=bpy.data.objects['V24_18_Windows_Detail'];roots=sorted(o.name for o in bpy.data.objects if o.get('UE_Interaction')=='HINGED_OUTWARD')
if hasattr(sc,'eevee'):
 if hasattr(sc.eevee,'taa_render_samples'):sc.eevee.taa_render_samples=32
 if hasattr(sc.eevee,'use_raytracing'):sc.eevee.use_raytracing=False
for n,pos,target,power,size in [('Window_Fill',(9,-5,12),(9,2,5),1600,9),('Window_Side',(17,-1,8),(10,2,6),600,6)]:
 l=bpy.data.lights.new(n,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(n,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
frames=[]
for f in range(1,41):
 sc.frame_set(f);bpy.context.view_layer.update();fn=D/f'Window_{f:04d}.png';sc.render.filepath=str(fn);bpy.ops.render.render(write_still=True);frames.append({'frame':f,'sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'angles_degrees':{n:float(bpy.data.objects[n].rotation_euler.z*180/3.141592653589793)for n in roots}})
 if f in [1,20,40]:shutil.copy2(fn,R/f'V24_18_Window_Motion_{f:02d}.png')
 if f%10==0:print('WINDOW_FRAME',f,flush=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(R/'V24_18_Window_Motion_States.json').write_text(json.dumps({'model_sha256':h,'fps':12,'frame_count':40,'resolution':[960,720],'camera':sc.camera.name,'outward_sashes':roots,'frames':frames},indent=2));print('WINDOW_MOTION_COMPLETE',flush=True)
