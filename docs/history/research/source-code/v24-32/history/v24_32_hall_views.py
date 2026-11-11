import bpy,json,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_32';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_31/Blender/Architecture_Complete_V24_31.blend');sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=8;sc.cycles.use_denoising=True;sc.render.resolution_x=800;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.exposure=-1.0
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
views=[('HallRight',(6.7,3.9,8.5),(9.,4.0,8.5),24),('HallLeft',(6.7,3.9,8.5),(4.,4.,8.5),24)]
for name,loc,aim,lens in views:
 c=bpy.data.objects.new('BASE_'+name,bpy.data.cameras.new('BASE_'+name));sc.collection.objects.link(c);c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.02;sc.camera=c;sc.render.filepath=str(D/('Before_'+name+'.png'));bpy.ops.render.render(write_still=True);print('BASE_DONE',name,flush=True)
