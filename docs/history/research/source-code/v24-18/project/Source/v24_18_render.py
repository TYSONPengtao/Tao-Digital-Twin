import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path('E:/jz/JIA/Rebuild_V24_18/Reports');P=R.parent/'Blender/Architecture_Complete_V24_18.blend';draft='--draft'in sys.argv;only=sys.argv[sys.argv.index('--only')+1:]if '--only'in sys.argv else[]
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=6 if draft else 20;sc.cycles.use_denoising=True;sc.render.resolution_x=1200 if draft else 1600;sc.render.resolution_y=900 if draft else 1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for n,pos,target,power,size in [('V18_Court',(10,-10,13),(9,-6,1),1800,10),('V18_Storage',(17,-16,10),(15,-14,1),1200,8),('V18_House',(6,-5,12),(6,3,5),1500,8),('V18_Rear',(18,4,8),(13,0,1),900,7),('V18_Grade',(-2,5,.8),(0,5,-.15),65,2)]:
 l=bpy.data.lights.new(n,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(n,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
names=['Narrow_Ears','Screen_Valley','Screen_Outside','Wall_Continuity','Wall_Rear','House_Front','Windows_Detail','House_Grade','Whole_Site'];rows=[]
for n in names:
 if only and n not in only:continue
 sc.frame_set(40);sc.camera=bpy.data.objects['V24_18_'+n];fn=('Draft_'if draft else'')+'V24_18_'+n+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True);rows.append({'camera':sc.camera.name,'file':fn,'frame':40});print('VIEW_DONE',n,flush=True)
 if n in ['House_Front','Windows_Detail']and not draft:
  sc.frame_set(1);fn='V24_18_'+n+'_Closed.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True);rows.append({'camera':sc.camera.name,'file':fn,'frame':1})
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(R/('V24_18_Draft_States.json'if draft else'V24_18_Preview_States.json')).write_text(json.dumps({'model_sha256':h,'views':rows},indent=2));print('RENDER_COMPLETE',len(rows),flush=True)
