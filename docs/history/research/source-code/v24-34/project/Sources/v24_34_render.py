import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_34';O=Path('E:/jz/JIA/Rebuild_V24_34');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_34.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);draft='--draft'in sys.argv;only=sys.argv[sys.argv.index('--only')+1:]if '--only'in sys.argv else[]
sc.render.engine='CYCLES';sc.cycles.samples=8 if draft else 24;sc.cycles.use_denoising=True;sc.render.resolution_x=1400 if draft else 1800;sc.render.resolution_y=1000 if draft else 1250;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.exposure=-.5
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
for name,loc,aim,lens in json.loads((D/'Views.json').read_text()):
 if only and name not in only:continue
 c=bpy.data.objects['V24_34_'+name];sc.camera=c;fn=('Draft_'if draft else'')+'V24_34_'+name+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True);(R/(fn[:-4]+'_State.json')).write_text(json.dumps({'model_sha256':h,'file':fn,'camera':c.name,'draft':draft,'frame':40}));print('VIEW_DONE',fn,flush=True)
if not only or 'top'in only:
 c=bpy.data.objects.new('QA_Top',bpy.data.cameras.new('QA_Top'));sc.collection.objects.link(c);c.location=(7.,-9.,180.);c.rotation_euler=(0,0,0);c.data.type='ORTHO';c.data.ortho_scale=158.;c.data.clip_end=400;sc.camera=c;sc.render.resolution_x=2400;sc.render.resolution_y=2400;sc.render.filepath=str(R/'V24_34_Expanded_Top.png');bpy.ops.render.render(write_still=True);print('TOP_DONE',flush=True)
