import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_33';P=Path('E:/jz/JIA/Rebuild_V24_32/Blender/Architecture_Complete_V24_32.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=8;sc.cycles.use_denoising=True;sc.render.resolution_x=960;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.exposure=-.65
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for x in p.devices:x.use=x.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
for tag,pos in [('F3',(6.5,6.7,9.8)),('F2',(6.,7.7,6.6)),('Kitchen',(7.5,-5.,2.0))]:
 l=bpy.data.lights.new('DIAG_'+tag,'AREA');l.energy=100;l.size=3;o=bpy.data.objects.new(l.name,l);sc.collection.objects.link(o);o.location=pos
views=[('01_Terrace_Threshold',(5.,6.4,8.5),(3.,6.4,7.5),25),('02_Terrace_Plate',(1.7,7.,8.55),(1.7,2.,7.7),20),('03_Stair_Wall_F2',(4.5,8.,6.3),(7.,7.4,6.65),18),('04_F3_Well_Edge',(8.7,8.8,8.6),(5.7,6.7,7.7),20),('05_Kitchen_Wood',(7.5,-4.7,1.25),(9.5,-4.7,1.45),22),('06_Passage_Grade',(13.,-.65,1.0),(14.1,-2.9,-.1),24),('07_F3_Door',(8.45,7.,8.5),(8.45,5.5,8.4),26),('08_Wall_Return',(13.4,-1.8,1.15),(14.1,-3.2,1.0),20)]
only=sys.argv[sys.argv.index('--only')+1:] if '--only' in sys.argv else []
for tag,pos,aim,lens in views:
 if only and tag not in only:continue
 c=bpy.data.objects.new('DIAG_'+tag,bpy.data.cameras.new('DIAG_'+tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;sc.camera=c;sc.render.filepath=str(D/('Before_'+tag+'.png'));bpy.ops.render.render(write_still=True);print('DONE',tag,flush=True)
(D/'Diagnostic_Views.json').write_text(json.dumps(views),encoding='utf8')
