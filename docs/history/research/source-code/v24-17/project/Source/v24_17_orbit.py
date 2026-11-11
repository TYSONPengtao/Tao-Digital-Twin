"""Read-only realtime-material orbit; fixed frame 40 keeps all doors still."""
import bpy,sys,json,math,hashlib,shutil
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_17/Orbit_Frames';D.mkdir(exist_ok=True);R=Path('E:/jz/JIA/Rebuild_V24_17/Reports');P=R.parent/'Blender/Architecture_Complete_V24_17.blend'
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene
for name in ['BLENDER_EEVEE','BLENDER_EEVEE_NEXT']:
 try:sc.render.engine=name;break
 except TypeError:pass
assert 'EEVEE'in sc.render.engine,'Realtime renderer unavailable'
if hasattr(sc,'eevee'):
 for name in ['taa_render_samples','taa_samples']:
  if hasattr(sc.eevee,name):setattr(sc.eevee,name,16)
 if hasattr(sc.eevee,'use_raytracing'):sc.eevee.use_raytracing=False
sc.render.resolution_x=960;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.fps=24;sc.frame_set(40);bpy.context.view_layer.update()
for n,pos,tar,power,size in [('Orbit_Soft',(15,-15,10),(15,-14,.5),1300,8),('Orbit_Fill',(10,-20,5),(15,-14,.5),650,6),('Orbit_Back',(18,-4,7),(14,-8,1),850,7)]:
 l=bpy.data.lights.new(n,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(n,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(tar)-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('V24_17_Runtime_Orbit_Camera',bpy.data.cameras.new('V24_17_Runtime_Orbit_Camera'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.lens=42;cam.data.clip_start=.05;cam.data.clip_end=300;frames=[];N=72
for i in range(N):
 t=i/(N-1);ang=-.60+.95*t;cam.location=(14.8+10.5*math.cos(ang),-11.5+10.5*math.sin(ang),6.9+.4*math.sin(math.pi*t));target=Vector((14.8,-11.5,3.4));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();fn=D/f'Orbit_{i+1:04d}.png';sc.render.filepath=str(fn);bpy.ops.render.render(write_still=True)
 frames.append({'frame':i+1,'source_scene_frame':40,'camera_location':list(cam.location),'camera_rotation':list(cam.rotation_euler),'sha256':hashlib.sha256(fn.read_bytes()).hexdigest()})
 if i+1 in [1,24,48,72]:shutil.copy2(fn,R/f'V24_17_Orbit_Check_{i+1:03d}.png')
 if i%12==0:print('ORBIT_FRAME',i+1,flush=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(R/'V24_17_Orbit_States.json').write_text(json.dumps({'model_sha256':h,'engine':sc.render.engine,'source_scene_frame':40,'fps':24,'frame_count':N,'resolution':[960,720],'camera_clip_m':[.05,300],'frames':frames},indent=2));print('ORBIT_COMPLETE',N,flush=True)
