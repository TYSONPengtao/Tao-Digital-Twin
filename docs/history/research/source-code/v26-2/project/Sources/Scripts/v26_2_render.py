from pathlib import Path
import bpy,json,sys,hashlib
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_2_views import VIEWS
after='--after'in sys.argv;draft='--draft'in sys.argv;only=sys.argv[sys.argv.index('--only')+1:]if'--only'in sys.argv else[]
P=Path('E:/jz/JIA/Rebuild_V26_2/Blender/Architecture_Complete_V26_2.blend')if after else Path('E:/jz/JIA/Rebuild_V26_1/Blender/Architecture_Complete_V26_1.blend')
R=Path('E:/jz/JIA/Rebuild_V26_2/Reports');R.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=8 if draft else 32;sc.cycles.use_denoising=True;sc.render.resolution_x=1000 if draft else 1600;sc.render.resolution_y=800 if draft else 1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
with P.open('rb')as fp:h=hashlib.file_digest(fp,'sha256').hexdigest()
for tag,pos,aim,lens in VIEWS:
 if only and tag not in only:continue
 sc.frame_set(1 if tag.startswith('12_')else 40);bpy.context.view_layer.update()
 cam=bpy.data.cameras.new('V26_2_Review_'+tag);c=bpy.data.objects.new(cam.name,cam);sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();cam.lens=lens;cam.clip_start=.025;cam.clip_end=600;sc.camera=c;light=None;sc.view_settings.exposure=-.15
 if int(tag[:2])<=5 or tag.startswith(('09_','10_','11_','12_','13_')):
  l=bpy.data.lights.new('Temporary_Review_Light','AREA');l.energy=65;l.shape='DISK';l.size=2.;light=bpy.data.objects.new(l.name,l);sc.collection.objects.link(light);light.location=c.location;light.rotation_euler=c.rotation_euler;sc.view_settings.exposure=.15
 fn=('Draft_'if draft else'')+('After_'if after else'Before_')+tag+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True);(R/(fn[:-4]+'_State.json')).write_text(json.dumps({'model':str(P),'model_sha256':h,'frame':sc.frame_current,'camera':tag,'position':pos,'aim':aim,'lens':lens,'draft':draft,'temporary_review_light':bool(light),'saved_file_unchanged':True},indent=2));print('VIEW_DONE',fn,flush=True)
 if light:bpy.data.objects.remove(light,do_unlink=True)
 bpy.data.objects.remove(c,do_unlink=True)
