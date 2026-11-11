import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_12/Review';D.mkdir(exist_ok=True)
version=sys.argv[sys.argv.index('--version')+1]if'--version'in sys.argv else'V26_12'
P=Path('E:/jz/JIA/Rebuild_'+version+'/Blender/Architecture_Complete_'+version+'.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
sc.render.resolution_x=1200;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
views=[('01_Gate_Whole',(6.6,-16.8,1.9),(6.6,-11.6,1.55),26),('02_Stone_Corner',(4.78,-12.75,1.25),(5.19,-11.86,1.25),37),('03_Stone_Flowers',(4.96,-12.45,.12),(5.2,-11.87,.14),42),('04_Header',(6.6,-14.4,2.75),(6.6,-11.80,2.95),41)]
for tag,pos,aim,lens in views:
 if '--only'in sys.argv and tag not in sys.argv[sys.argv.index('--only')+1:]:continue
 cam=bpy.data.objects.new('Review_'+tag,bpy.data.cameras.new('Review_'+tag));sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_start=.025;sc.camera=cam
 name=version+'_'+tag;sc.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True)
 (D/(name+'.json')).write_text(json.dumps({'model':str(P),'model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'camera':[pos,aim,lens],'saved_world':sc.world.name,'extra_lights':0,'engine':sc.render.engine},indent=2),'utf8');bpy.data.objects.remove(cam,do_unlink=True);print('RENDERED',name,flush=True)
