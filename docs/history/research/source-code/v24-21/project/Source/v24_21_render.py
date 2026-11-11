import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
O=Path('E:/jz/JIA/Rebuild_V24_21');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_21.blend';draft='--draft'in sys.argv;only=sys.argv[sys.argv.index('--only')+1:]if '--only'in sys.argv else[]
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=6 if draft else 16;sc.cycles.use_denoising=True;sc.render.resolution_x=1120 if draft else 1500;sc.render.resolution_y=800 if draft else 1050;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for name,pos,aim,power,size in [('Frieze',(-31,6,6),(-23,7,2.2),1100,7),('Person',(9,-7,6),(6.5,-4.8,.5),900,5)]:
 l=bpy.data.lights.new('V21_'+name,'AREA');l.energy=power;l.size=size;o=bpy.data.objects.new(l.name,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(aim)-o.location).to_track_quat('-Z','Y').to_euler()
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
for name in ['Exterior_Frieze','Exterior_Frieze_Close','Person']:
 if only and name not in only:continue
 sc.camera=bpy.data.objects['V24_21_'+name];fn=('Draft_'if draft else'')+'V24_21_'+name+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True)
 (R/(fn[:-4]+'_State.json')).write_text(json.dumps({'model_sha256':h,'file':fn,'camera':sc.camera.name,'camera_matrix':list(map(list,sc.camera.matrix_world)),'draft':draft,'frame':40},indent=2));print('VIEW_DONE',fn,flush=True)
