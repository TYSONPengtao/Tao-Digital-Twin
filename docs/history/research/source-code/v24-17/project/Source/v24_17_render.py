import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
O=Path('E:/jz/JIA/Rebuild_V24_17');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_17.blend';draft='--draft'in sys.argv
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.engine='CYCLES';sc.cycles.samples=6 if draft else 20;sc.cycles.use_denoising=True;sc.render.resolution_x=1200 if draft else 1600;sc.render.resolution_y=900 if draft else 1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for name,pos,target,power,size in [('V17_Render_Soft',(15,-15,10),(15,-14,.5),1300,8),('V17_Render_Fill',(10,-20,5),(15,-14,.5),650,6),('V17_Render_Back',(18,-4,7),(14,-8,1),850,7),('V17_Render_Screen',(7,-13,6),(7,-17.1,1),500,6)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(name,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
names=['Storage_Outside','Storage_West_Gable','Roof_Junction','Kitchen_Rear','Secondary_Outside','Secondary_Gallery','Entry_White_Bay','Whole_Site'];views=[];only=sys.argv[sys.argv.index('--only')+1:]if '--only'in sys.argv else[]
for n in names:
 if only and n not in only:continue
 sc.camera=bpy.data.objects['V24_17_'+n];file=('Draft_'if draft else'')+'V24_17_'+n+'.png';sc.render.filepath=str(R/file);bpy.ops.render.render(write_still=True);views.append({'file':file,'camera':sc.camera.name,'frame':40});print('VIEW_DONE',n,flush=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(R/('V24_17_Draft_States.json'if draft else'V24_17_Preview_States.json')).write_text(json.dumps({'model_sha256':h,'views':views},indent=2))
