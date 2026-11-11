import bpy,json,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_04_common import *
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;draft='--draft'in sys.argv
sc.render.engine='BLENDER_WORKBENCH'if draft else'CYCLES';sc.render.resolution_x=1280 if draft else 1600;sc.render.resolution_y=960 if draft else 1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
if draft:
 ds=sc.display.shading;ds.light='STUDIO';ds.color_type='MATERIAL';ds.show_shadows=True;ds.show_cavity=True;ds.cavity_type='BOTH';ds.show_object_outline=True;ds.background_type='WORLD';sc.world.color=(.15,.15,.15)
else:
 sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.view_settings.look='Medium High Contrast';sc.view_settings.exposure=.05
 l=bpy.data.lights.new('Review_Soft_Daylight','AREA');l.energy=650;l.shape='DISK';l.size=7;o=bpy.data.objects.new(l.name,l);sc.collection.objects.link(o);o.location=(4,-6,8);o.rotation_euler=(Vector((8,-6,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
views=[('Kitchen_Wall_Closed',(4.2,-.6,2.1),(9.6,-2.8,1.5),28,40),('Gate_Front',(6.6,-16.,1.45),(6.6,-11.9,1.75),19,20),('Gate_Courtyard',(4.6,-7.4,2.5),(6.6,-11.9,1.85),25,40),('Gate_Roof_Top',(10.8,-18.2,6.8),(6.9,-11.8,2.65),45,40)]
only=sys.argv[sys.argv.index('--only')+1:]if '--only'in sys.argv else[]
saved=[]
for name,pos,tar,lens,f in views:
 if only and name not in only:continue
 c=bpy.data.objects.new('Review_'+name,bpy.data.cameras.new('Review_'+name));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;sc.camera=c;sc.frame_set(f);fn=('Draft_'if draft else'V24_04_')+name+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True);saved.append({'file':fn,'position':pos,'target':tar,'lens_mm':lens,'frame':f});print('VIEW COMPLETE',fn,flush=True)
write('V24_04_'+('Draft'if draft else'Preview')+'_States.json',{'model_sha256':sha(P),'real_materials':not draft,'views':saved,'material_override':None})
