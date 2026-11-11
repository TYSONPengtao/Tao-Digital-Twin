from pathlib import Path
import bpy,sys,json,hashlib
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_5_views import VIEWS
before='--before'in sys.argv;cycles='--material-preview'in sys.argv;ver='V26_4'if before else'V26_5';P=Path('E:/jz/JIA/Rebuild_'+ver+'/Blender/Architecture_Complete_'+ver+'.blend');R=W/'v26_5/Review';R.mkdir(parents=True,exist_ok=True);only=sys.argv[sys.argv.index('--only')+1:]if'--only'in sys.argv else[]
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.engine='CYCLES'if cycles else'BLENDER_WORKBENCH';sc.render.resolution_x=850;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'if cycles else'Standard'
if cycles:
 sc.cycles.samples=20;sc.cycles.use_denoising=True
 try:
  pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
  for d in pref.devices:d.use=d.type=='OPTIX'
  sc.cycles.device='GPU'
 except Exception:pass
else:
 sh=sc.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=False;sh.background_type='WORLD';sc.world.color=(.12,.12,.12);sc.display.render_aa='16'
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
for tag,pos,aim,lens in VIEWS:
 if only and tag not in only:continue
 c=bpy.data.objects.new('Review_'+tag,bpy.data.cameras.new('Review_'+tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=600;sc.camera=c;light=None
 if cycles:
  ld=bpy.data.lights.new('Temporary_review_fill','AREA');ld.energy=75;ld.shape='DISK';ld.size=2.;light=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(light);light.location=c.location;light.rotation_euler=c.rotation_euler
 fn=('Before_'if before else'After_')+tag+('_Cycles'if cycles else'_Solid')+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True);(R/(fn[:-4]+'.json')).write_text(json.dumps({'model':str(P),'model_sha256':h,'camera':[pos,aim,lens],'temporary_review_fill_watts':75 if light else 0,'saved_model_unmodified':True},indent=2),encoding='utf8');print('REVIEW_DONE',fn,flush=True)
 if light:bpy.data.objects.remove(light,do_unlink=True)
 bpy.data.objects.remove(c,do_unlink=True)
