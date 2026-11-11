import bpy,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_08_common import *
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;draft='--draft'in sys.argv;sc.render.engine='BLENDER_WORKBENCH'if draft else'CYCLES';sc.render.resolution_x=1280 if draft else 1600;sc.render.resolution_y=960 if draft else 1200;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
if draft:
 ds=sc.display.shading;ds.light='STUDIO';ds.color_type='MATERIAL';ds.show_shadows=True;ds.show_cavity=True;ds.cavity_type='BOTH';ds.background_type='WORLD';sc.world.color=(.14,.14,.14)
else:
 sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.view_settings.look='Medium High Contrast';sc.view_settings.exposure=.1
 for n,pos,tar,energy,size in [('Exterior_Fill',(24,-4,9),(13,-5,1),1100,8),('Court_Fill',(5,-7,9),(8,-6,1.4),650,7)]:
  l=bpy.data.lights.new(n,'AREA');l.energy=energy;l.shape='DISK';l.size=size;o=bpy.data.objects.new(n,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(tar)-o.location).to_track_quat('-Z','Y').to_euler()
views=['Court','Exterior','Exterior_Wall','Kitchen_Exterior','Court_Plan','Gate_Junction'];only=sys.argv[sys.argv.index('--only')+1:]if'--only'in sys.argv else[];saved=[]
for n in views:
 if only and n not in only:continue
 sc.camera=bpy.data.objects['V24_08_'+n];sc.frame_set(40);fn=('Draft_'if draft else'V24_08_')+n+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True);saved.append({'file':fn,'frame':40,'camera':sc.camera.name});print('VIEW COMPLETE',fn,flush=True)
write('V24_08_'+('Draft'if draft else'Preview')+'_States.json',{'model_sha256':sha(P),'real_materials':not draft,'views':saved})
