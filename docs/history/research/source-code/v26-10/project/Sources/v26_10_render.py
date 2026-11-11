from pathlib import Path
import bpy,sys,json,hashlib
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_10_views import VIEWS
before='--before'in sys.argv;ver='V26_9'if before else'V26_10'
P=Path('E:/jz/JIA/Rebuild_'+ver+'/Blender/Architecture_Complete_'+ver+'.blend');R=W/'v26_10/Review';R.mkdir(parents=True,exist_ok=True)
only=sys.argv[sys.argv.index('--only')+1:]if'--only'in sys.argv else[]
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.engine='CYCLES';sc.render.resolution_x=1000;sc.render.resolution_y=820;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.cycles.samples=16;sc.cycles.use_denoising=True
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
 for d in pref.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
for tag,pos,aim,lens in VIEWS:
 if only and tag not in only:continue
 c=bpy.data.objects.new('Review_'+tag,bpy.data.cameras.new('Review_'+tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=600;sc.camera=c
 fn=('Before_'if before else'After_')+tag+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True)
 (R/(fn[:-4]+'.json')).write_text(json.dumps({'model':str(P),'model_sha256':h,'camera':[pos,aim,lens],'saved_world':sc.world.name,'extra_lights':0,'saved_model_unmodified':True},indent=2),'utf8')
 print('REVIEW_DONE',fn,flush=True);bpy.data.objects.remove(c,do_unlink=True)
