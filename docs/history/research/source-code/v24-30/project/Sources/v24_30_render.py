import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
O=Path('E:/jz/JIA/Rebuild_V24_30');R=O/'Reports';W=Path(__file__).parent;P=O/'Blender/Architecture_Complete_V24_30.blend';draft='--draft'in sys.argv;before='--before'in sys.argv;only=sys.argv[sys.argv.index('--only')+1:]if '--only'in sys.argv else[]
if before:P=Path('E:/jz/JIA/Rebuild_V24_26/Blender/Architecture_Complete_V24_26.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=8 if draft else 24;sc.cycles.use_denoising=True;sc.render.resolution_x=1120 if draft else 1600;sc.render.resolution_y=800 if draft else 1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in prefs.devices):sc.cycles.device='GPU'
except Exception as e:print('GPU',e)
for name,pos,aim,power,size in [('Courtyard',(4.5,-6,5.0),(8.4,-7,1.7),500,5),('Storage',(11.0,-14.8,4.8),(13.4,-12.1,2.3),300,3.5),('Gate',(7,-15.5,5.2),(7,-11.7,1.4),450,4),('InnerWall',(-2.,-13.,5.),(1.,-11.58,2.3),220,4)]:
 l=bpy.data.lights.new('V26_Inspection_'+name,'AREA');l.energy=power;l.size=size;o=bpy.data.objects.new(l.name,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler()
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
for name,loc,aim,lens in json.loads((W/'v24_30/Views.json').read_text('utf8')):
 if only and name not in only:continue
 if before:
  c=bpy.data.objects.new('V24_30_'+name,bpy.data.cameras.new('V24_30_'+name));sc.collection.objects.link(c);c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=300
 else:c=bpy.data.objects['V24_30_'+name]
 sc.camera=c;fn=('Before_'if before else'Draft_'if draft else'')+'V24_30_'+name+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True)
 (R/(fn[:-4]+'_State.json')).write_text(json.dumps({'model_sha256':h,'file':fn,'camera':c.name,'camera_matrix':list(map(list,c.matrix_world)),'draft':draft,'before':before,'frame':40,'eye_z_m':c.location.z},indent=2));print('VIEW_DONE',fn,flush=True)

