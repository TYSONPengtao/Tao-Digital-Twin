from pathlib import Path
import bpy,json,sys,hashlib
W=Path(__file__).parent;D=W/'v26_1';O=Path('E:/jz/JIA/Rebuild_V26_1');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_1.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);draft='--draft'in sys.argv;only=sys.argv[sys.argv.index('--only')+1:]if'--only'in sys.argv else[]
sc.render.engine='CYCLES';sc.cycles.samples=8 if draft else 32;sc.cycles.use_denoising=True;sc.render.resolution_x=1100 if draft else 1600;sc.render.resolution_y=825 if draft else 1150;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
for tag,pos,aim,lens in json.loads((D/'Views.json').read_text('utf8')):
 if only and tag not in only:continue
 c=bpy.data.objects['V26_1_'+tag];sc.camera=c;light=None;sc.view_settings.exposure=-.15
 if int(tag[:2])<=6 or tag.startswith(('08_','09_','10_','13_')):
  l=bpy.data.lights.new('Temporary_Review_Light','AREA');l.energy=65 if tag.startswith('08_')else 48;l.shape='DISK';l.size=2.;light=bpy.data.objects.new('Temporary_Review_Light',l);sc.collection.objects.link(light);light.location=c.location;light.rotation_euler=c.rotation_euler;sc.view_settings.exposure=.15
 fn=('Draft_'if draft else'')+'V26_1_'+tag+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True);(R/(fn[:-4]+'_State.json')).write_text(json.dumps({'model_sha256':h,'frame':40,'camera':c.name,'draft':draft,'temporary_review_light':light is not None,'file':fn,'saved_file_unchanged':True},indent=2));print('VIEW_DONE',tag,flush=True)
 if light:bpy.data.objects.remove(light,do_unlink=True)
