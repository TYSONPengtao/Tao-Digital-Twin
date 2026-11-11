import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
O=Path('E:/jz/JIA/Rebuild_V24_13');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_13.blend';draft='--draft'in sys.argv
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.engine='CYCLES';sc.cycles.samples=8 if draft else 20;sc.cycles.use_denoising=True;sc.render.resolution_x=1200 if draft else 1600;sc.render.resolution_y=900 if draft else 1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for name,pos,target,power,size in [('V12_Render_Soft',(15,-15,10),(15,-14,.5),1300,8),('V12_Render_Fill',(10,-20,5),(15,-14,.5),650,6),('V12_Render_Room',(17,-11,3),(16,-15,1),80,2),('V12_Render_Back',(18,-4,7),(14,-8,1),750,7),('V12_Render_Screen',(7,-13,6),(7,-16.9,1),500,6)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(name,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
names=['User_Front','Level_Elevation','Eave_Junction','Top','Rear_Arc','Whole_Site'];views=[];only=sys.argv[sys.argv.index('--only')+1:]if '--only'in sys.argv else[]
for n in names:
 if only and n not in only:continue
 sc.camera=bpy.data.objects['V24_13_'+n];file=('Draft_'if draft else'')+'V24_13_'+n+'.png';sc.render.filepath=str(R/file);bpy.ops.render.render(write_still=True);views.append({'file':file,'camera':sc.camera.name,'frame':40});print('VIEW_DONE',n,flush=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
dest=R/('V24_13_Draft_States.json'if draft else'V24_13_Preview_States.json');dest.write_text(json.dumps({'model_sha256':h,'views':views},indent=2),encoding='utf8')
