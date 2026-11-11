from pathlib import Path
import bpy,sys,json,hashlib
from mathutils import Vector
P=Path('E:/jz/JIA/Rebuild_V26_5/Blender/Architecture_Complete_V26_5.blend');R=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.engine='CYCLES';sc.render.resolution_x=800;sc.render.resolution_y=700;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX';sc.cycles.samples=12;sc.cycles.use_denoising=True
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
 for d in pref.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
for tag,pos,aim in [('F2_Upper_Arrival',(6.8,7.95,7.4),(8.15,7.95,7.0))]:
 c=bpy.data.objects.new('ReadOnly_Review_'+tag,bpy.data.cameras.new('ReadOnly_Review_'+tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=26;c.data.clip_start=.02;c.data.clip_end=200;sc.camera=c;ld=bpy.data.lights.new('ReadOnly_fill','AREA');ld.energy=60;ld.shape='DISK';ld.size=1.5;light=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(light);light.location=c.location;light.rotation_euler=c.rotation_euler;sc.render.filepath=str(R/(tag+'.png'));bpy.ops.render.render(write_still=True);(R/(tag+'.json')).write_text(json.dumps({'model':str(P),'model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'camera':[pos,aim,26],'temporary_fill_watts':60,'saved_model_unmodified':True},indent=2),'utf8');bpy.data.objects.remove(c,do_unlink=True);bpy.data.objects.remove(light,do_unlink=True);print('READONLY_STAIR_VIEW_DONE',tag,flush=True)
