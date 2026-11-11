import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
O=Path('E:/jz/JIA/Rebuild_V24_23');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_23.blend';draft='--draft'in sys.argv;only=sys.argv[sys.argv.index('--only')+1:]if '--only'in sys.argv else[]
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=8 if draft else 24;sc.cycles.use_denoising=True;sc.render.resolution_x=1120 if draft else 1600;sc.render.resolution_y=800 if draft else 1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in prefs.devices):sc.cycles.device='GPU'
except Exception as e:print('GPU',e)
# Lighting for inspection only; geometry is rendered directly from the saved file.
for name,pos,aim,power,size in [('Interior',(11.1,-7.0,2.75),(13.4,-7,1.3),110,2.3),('Courtyard',(4.5,-6,5.0),(8.4,-7,1.7),500,5),('Storage',(11.0,-14.8,4.8),(13.4,-12.1,2.3),300,3.5),('Gate',(7,-15.5,5.2),(7,-11.7,1.4),450,4)]:
 l=bpy.data.lights.new('V22_Inspection_'+name,'AREA');l.energy=power;l.size=size;o=bpy.data.objects.new(l.name,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler()
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
for name in ['Kitchen_North','Gate_Front','Gate_Pier','Storage_Joint','Storage_Wide','Storage_Foot']:
 if only and name not in only:continue
 sc.camera=bpy.data.objects['V24_23_'+name];fn=('Draft_'if draft else'')+'V24_23_'+name+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True)
 (R/(fn[:-4]+'_State.json')).write_text(json.dumps({'model_sha256':h,'file':fn,'camera':sc.camera.name,'camera_matrix':list(map(list,sc.camera.matrix_world)),'draft':draft,'frame':40,'eye_z_m':sc.camera.location.z},indent=2));print('VIEW_DONE',fn,flush=True)
