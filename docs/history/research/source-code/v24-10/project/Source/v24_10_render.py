import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V24_10');P=O/'Blender/Architecture_Complete_V24_10.blend';R=O/'Reports';draft='--draft'in sys.argv
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
sc.render.engine='CYCLES';sc.cycles.samples=12 if draft else 16;sc.cycles.use_denoising=True;sc.render.resolution_x=1400 if draft else 1600;sc.render.resolution_y=1050 if draft else 1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for name,pos,power,size in [('V10_Draft_Soft',(15,-15,10),1300,8),('V10_Draft_Fill',(10,-20,5),650,6),('V10_Draft_Room',(17,-11,3),80,2)]:
 l=bpy.data.lights.new(name,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(name,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((15,-14,0.5))-o.location).to_track_quat('-Z','Y').to_euler()
names=['Top','Entry_Outside','Entry_Approach','Entry_Overview','Gallery','Storage_Inside','Outer_Canopy','Outside','Whole_Site'];views=[]
only=sys.argv[sys.argv.index('--only')+1:]if '--only'in sys.argv else[]
for n in names:
 if only and n not in only:continue
 sc.camera=bpy.data.objects['V24_10_'+n];file=('Draft_'if draft else '')+'V24_10_'+n+'.png';sc.render.filepath=str(R/file);bpy.ops.render.render(write_still=True);views.append({'file':file,'camera':sc.camera.name,'frame':40});print('VIEW_DONE',n,flush=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(R/('V24_10_Draft_States.json'if draft else 'V24_10_Preview_States.json')).write_text(json.dumps({'model_sha256':h,'views':views},ensure_ascii=False,indent=2),encoding='utf8')
