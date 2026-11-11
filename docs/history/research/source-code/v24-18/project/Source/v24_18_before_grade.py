import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path('E:/jz/JIA/Rebuild_V24_18/Reports');P=Path('E:/jz/JIA/Rebuild_V24_17/Blender/Architecture_Complete_V24_17.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=20;sc.cycles.use_denoising=True;sc.render.resolution_x=1600;sc.render.resolution_y=1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
for n,pos,target,power,size in [('V18_Court',(10,-10,13),(9,-6,1),1800,10),('V18_Storage',(17,-16,10),(15,-14,1),1200,8),('V18_House',(6,-5,12),(6,3,5),1500,8),('V18_Rear',(18,4,8),(13,0,1),900,7),('V18_Grade',(-2,5,.8),(0,5,-.15),65,2)]:
 l=bpy.data.lights.new(n,'AREA');l.energy=power;l.shape='DISK';l.size=size;o=bpy.data.objects.new(n,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.objects.new('V24_18_Before_Grade_Camera',bpy.data.cameras.new('V24_18_Before_Grade_Camera'));sc.collection.objects.link(c);c.location=(-2.0,7.8,1.0);c.rotation_euler=(Vector((0,7.8,.45))-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=24;c.data.clip_start=.04;c.data.clip_end=300;sc.camera=c;sc.render.filepath=str(R/'V24_18_House_Grade_Before_V17.png');bpy.ops.render.render(write_still=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(R/'V24_18_Grade_Comparison_States.json').write_text(json.dumps({'before_model':str(P),'before_model_sha256':h,'before_file':'V24_18_House_Grade_Before_V17.png','after_file':'V24_18_House_Grade.png','camera_location':list(c.location),'target':[0,7.8,.45],'lens_mm':24,'illumination':'Identical inspection area lights and base scene','frame':40},indent=2));print('BEFORE_GRADE_RENDERED',flush=True)
