from pathlib import Path
import bpy,json,sys,hashlib
W=Path(__file__).parent;D=W/'v26';O=Path('E:/jz/JIA/Rebuild_V26');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);draft='--draft'in sys.argv;only=sys.argv[sys.argv.index('--only')+1:]if'--only'in sys.argv else[]
sc.render.engine='CYCLES';sc.cycles.samples=8 if draft else 24;sc.cycles.use_denoising=True;sc.render.resolution_x=1200 if draft else 1600;sc.render.resolution_y=900 if draft else 1150;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.exposure=-.5
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
for tag,loc,aim,lens in json.loads((D/'Views.json').read_text('utf8')):
 if only and tag not in only:continue
 hide=[]
 if tag in ['07_Structure_Cutaway','08_Stair_Bearings_Cutaway']:
  for o in bpy.data.objects:
   if o.type!='MESH' or o.hide_render:continue
   if not o.name.startswith(('KZ_','BEAM_','SLAB_JOINED','STAIR_F','STAIR_LANDING','V26_Stair_')):o.hide_render=True;hide.append(o)
 c=bpy.data.objects['V26_'+tag];sc.camera=c;worklight=None
 if tag.startswith(('03_','04_','05_')):
  light=bpy.data.lights.new('Temporary_Review_Work_Light','AREA');light.energy=48;light.shape='DISK';light.size=2.0;worklight=bpy.data.objects.new('Temporary_Review_Work_Light',light);sc.collection.objects.link(worklight);worklight.location=c.location;worklight.rotation_euler=c.rotation_euler;sc.view_settings.exposure=0.;sc.view_settings.view_transform='AgX'
 else:sc.view_settings.exposure=-.5
 fn=('Draft_'if draft else'')+'V26_'+tag+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True)
 (R/(fn[:-4]+'_State.json')).write_text(json.dumps({'model_sha256':h,'file':fn,'camera':c.name,'draft':draft,'frame':40,'temporary_cutaway_hidden_objects':len(hide),'temporary_review_work_light':worklight is not None,'saved_model_not_modified':True}));print('VIEW_DONE',fn,flush=True)
 if worklight is not None:bpy.data.objects.remove(worklight,do_unlink=True)
 for o in hide:o.hide_render=False
