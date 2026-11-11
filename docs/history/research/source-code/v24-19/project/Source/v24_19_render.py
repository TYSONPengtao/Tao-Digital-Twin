import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path('E:/jz/JIA/Rebuild_V24_19/Reports');P=R.parent/'Blender/Architecture_Complete_V24_19.blend';draft='--draft'in sys.argv;only=sys.argv[sys.argv.index('--only')+1:]if '--only'in sys.argv else[]
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=6 if draft else 20;sc.cycles.use_denoising=True;sc.render.resolution_x=1120 if draft else 1600;sc.render.resolution_y=840 if draft else 1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for n,pos,target,power,size in [('Court',(10,-10,13),(9,-6,1),1800,10),('Storage',(17,-16,10),(15,-14,1),1200,8),('House',(6,-5,12),(6,3,5),1500,8),('Rear',(18,4,8),(13,0,1),900,7),('Grade',(-2,5,.8),(0,5,-.15),65,2)]:
 l=bpy.data.lights.new('V19_'+n,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(l.name,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
names=['Gable_East','Gable_Detail','Gable_West','Kitchen_North','House_Foot','House_Front','Entry_Grade','Screen_Valley','Whole_Site']
for n in names:
 if only and n not in only:continue
 for frame in ([40,1]if n=='House_Front'and not draft else[40]):
  sc.frame_set(frame);sc.camera=bpy.data.objects['V24_19_'+n];fn=('Draft_'if draft else'')+'V24_19_'+n+('_Closed'if frame==1 else'')+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True)
  (R/(fn[:-4]+'_State.json')).write_text(json.dumps({'model_sha256':h,'camera':sc.camera.name,'file':fn,'frame':frame,'draft':draft,'camera_matrix':list(map(list,sc.camera.matrix_world))},indent=2));print('VIEW_DONE',fn,flush=True)
