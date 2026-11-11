import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path('E:/jz/JIA/Rebuild_V24_20/Reports');P=R.parent/'Blender/Architecture_Complete_V24_20.blend';draft='--draft'in sys.argv;only=sys.argv[sys.argv.index('--only')+1:]if '--only'in sys.argv else[]
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=6 if draft else 12;sc.cycles.use_denoising=True;sc.render.resolution_x=1120 if draft else 1400;sc.render.resolution_y=840 if draft else 1050;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for n,pos,target,power,size in [('Court',(10,-10,13),(9,-6,1),1800,10),('Kitchen',(10,-7,2.1),(13,-7,1.2),140,4),('Storage',(17,-16,10),(15,-14,1),1200,8),('House',(6,-5,12),(6,3,5),1500,8),('Roof',(18,8,18),(10,5,11),1000,6),('Rear',(18,4,8),(13,0,1),900,7),('Perimeter',(-31,-7,8),(-22,4,0),1600,12),('WC',(10.9,8.4,2.8),(11.8,8.7,1),70,2)]:
 l=bpy.data.lights.new('V20_'+n,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(l.name,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
camera=bpy.data.objects.new('V24_20_House_Roof',bpy.data.cameras.new('V24_20_House_Roof'));sc.collection.objects.link(camera);camera.location=(18.5,12.5,17.5);camera.rotation_euler=(Vector((8.7,5.9,11.4))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=52;camera.data.clip_start=.04;camera.data.clip_end=300
l=bpy.data.lights.new('V20_WC_Left','AREA');l.energy=35;l.size=1.2;o=bpy.data.objects.new(l.name,l);sc.collection.objects.link(o);o.location=(9.7,8.8,2.5)
names=['Perimeter','Perimeter_Corner','Kitchen_Interior','Kitchen_Floor','Kitchen_Roof','Roof_Units','Roof_Junction','House_Front','House_Roof','WC_Entrance','WC_Interior','WC_Stair_Entry','Whole_Site']
for n in names:
 if only and n not in only:continue
 sc.frame_set(40);sc.camera=bpy.data.objects['V24_20_'+n];fn=('Draft_'if draft else'')+'V24_20_'+n+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True)
 (R/(fn[:-4]+'_State.json')).write_text(json.dumps({'model_sha256':h,'camera':sc.camera.name,'file':fn,'frame':40,'draft':draft,'camera_matrix':list(map(list,sc.camera.matrix_world))},indent=2));print('VIEW_DONE',fn,flush=True)
