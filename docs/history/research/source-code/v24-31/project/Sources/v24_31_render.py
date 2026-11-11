import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
O=Path('E:/jz/JIA/Rebuild_V24_31');R=O/'Reports';W=Path(__file__).parent;P=O/'Blender/Architecture_Complete_V24_31.blend';draft='--draft'in sys.argv;only=sys.argv[sys.argv.index('--only')+1:]if '--only'in sys.argv else[]
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=8 if draft else 24;sc.cycles.use_denoising=True;sc.render.resolution_x=1120 if draft else 1600;sc.render.resolution_y=800 if draft else 1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.exposure=-.65
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in prefs.devices):sc.cycles.device='GPU'
except Exception as e:print('GPU',e)
for name,pos,aim,power,size in [('Storage',(11.,-14.8,4.8),(10.,-12.1,.3),300,3.5),('HouseF1',(6.4,5.,2.9),(6.4,5.,-.4),150,3.),('Stair',(7.,8.6,3.),(5.,8.6,1.),60,2.),('HouseF2',(6.4,5.,6.6),(6.4,5.,3.5),150,3.),('HouseF3',(11.,5.,9.5),(11.,5.,7.05),140,3.),('WC',(11.7,8.3,2.7),(13.,8.55,1.3),8,1.5),('BayLeft',(2.,-.4,2.6),(1.95,1.1,.0),150,3.),('BayRight',(11.,-.4,2.6),(10.9,1.1,.0),150,3.)]:
 l=bpy.data.lights.new('V31_Inspection_'+name,'AREA');l.energy=power;l.size=size;o=bpy.data.objects.new(l.name,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler()
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
for name,loc,aim,lens in json.loads((W/'v24_31/Views.json').read_text('utf8')):
 if only and name not in only:continue
 c=bpy.data.objects['V24_31_'+name];sc.camera=c;fn=('Draft_'if draft else'')+'V24_31_'+name+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True)
 (R/(fn[:-4]+'_State.json')).write_text(json.dumps({'model_sha256':h,'file':fn,'camera':c.name,'camera_matrix':list(map(list,c.matrix_world)),'draft':draft,'frame':40,'inspection_lights':True,'eye_z_m':c.location.z},indent=2));print('VIEW_DONE',fn,flush=True)
