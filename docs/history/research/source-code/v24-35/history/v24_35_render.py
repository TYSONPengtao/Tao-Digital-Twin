from pathlib import Path
import bpy,sys,json,hashlib
W=Path(__file__).parent;D=W/'v24_35';ver=sys.argv[sys.argv.index('--version')+1]if '--version'in sys.argv else '35';O=Path('E:/jz/JIA/Rebuild_V24_'+ver);R=O/'Reports';P=O/('Blender/Architecture_Complete_V24_'+ver+'.blend');bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=8 if '--draft'in sys.argv else 24;sc.cycles.use_denoising=True;sc.render.resolution_x=1600;sc.render.resolution_y=1180;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.exposure=-.15
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
for tag,*_ in json.loads((D/'Views.json').read_text()):
 sc.camera=bpy.data.objects['V24_35_'+tag];name='V24_'+ver+'_'+tag+'.png';sc.render.filepath=str(R/name);bpy.ops.render.render(write_still=True);(R/(name[:-4]+'_State.json')).write_text(json.dumps({'model_sha256':h,'file':name,'camera':sc.camera.name,'frame':40,'draft':'--draft'in sys.argv}));print('REPAIR_VIEW',name,flush=True)
