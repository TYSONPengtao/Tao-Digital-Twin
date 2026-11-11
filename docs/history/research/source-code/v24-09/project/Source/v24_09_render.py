import bpy,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_09_common import *
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;draft='--draft'in sys.argv;sc.render.engine='BLENDER_WORKBENCH'if draft else'CYCLES';sc.render.resolution_x=1400 if draft else 1600;sc.render.resolution_y=1000 if draft else 1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
if draft:
 ds=sc.display.shading;ds.light='STUDIO';ds.color_type='MATERIAL';ds.show_cavity=True;ds.cavity_type='BOTH';ds.show_shadows=True;ds.background_type='WORLD';sc.world.color=(.15,.15,.15)
else:
 sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.view_settings.look='Medium High Contrast';sc.view_settings.exposure=.1
 for n,pos,tar,energy,size in[('Screen_Outside',(5,-23,9),(7,-17,2.7),900,7),('Screen_Inside',(7,-13,8),(7,-16.9,3),600,5),('Screen_End',(14,-18,7),(10.8,-16.9,4),400,4)]:
  l=bpy.data.lights.new(n,'AREA');l.energy=energy;l.shape='DISK';l.size=size;o=bpy.data.objects.new(n,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(tar)-o.location).to_track_quat('-Z','Y').to_euler()
views=['Outside','Inside','Fork_Plan','Fork_Oblique','Underside','Whole_Site'];only=sys.argv[sys.argv.index('--only')+1:]if'--only'in sys.argv else[];saved=[]
for n in views:
 if only and n not in only:continue
 sc.camera=bpy.data.objects['V24_09_'+n];sc.frame_set(40);fn=('Draft_'if draft else'V24_09_')+n+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True);saved.append({'file':fn,'camera':sc.camera.name,'frame':40});print('VIEW COMPLETE',fn,flush=True)
write('V24_09_'+('Draft'if draft else'Preview')+'_States.json',{'model_sha256':sha(P),'real_materials':not draft,'views':saved})
