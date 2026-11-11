from pathlib import Path
import bpy,sys,json
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_1';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V26/Blender/Architecture_Complete_V26.blend');sc=bpy.context.scene;sc.frame_set(40)
sc.render.engine='CYCLES';sc.cycles.samples=8;sc.cycles.use_denoising=True;sc.render.resolution_x=1000;sc.render.resolution_y=750;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.view_settings.exposure=-.5
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
views=[('Before_Stair',(7.5,9.1,2.75),(4.6,8.6,1.7),22),('Before_Terrace',(1.5,8.3,8.5),(3.9,8.3,10.1),17),('Before_West_Wall',(-5,-17,2.8),(.5,-10,1.3),25),('Before_Screen',(18,-25,4.0),(11.7,-16.7,1.8),35),('Before_Gate_Floor',(6.35,-11.0,1.05),(8.0,-10.8,-.4),20)]
for tag,pos,aim,lens in views:
 c=bpy.data.objects.new(tag,bpy.data.cameras.new(tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.02;c.data.clip_end=500;sc.camera=c
 light=None
 if tag=='Before_Stair':
  l=bpy.data.lights.new('review','AREA');l.energy=48;l.size=2;light=bpy.data.objects.new('review',l);sc.collection.objects.link(light);light.location=pos;light.rotation_euler=c.rotation_euler
 sc.render.filepath=str(D/(tag+'.png'));bpy.ops.render.render(write_still=True);print('BEFORE_VIEW',tag,flush=True)
 if light:bpy.data.objects.remove(light,do_unlink=True)
