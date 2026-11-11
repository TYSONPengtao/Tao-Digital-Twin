import bpy,sys,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_07_common import *
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;draft='--draft'in sys.argv;sc.render.engine='BLENDER_WORKBENCH'if draft else'CYCLES';sc.render.resolution_x=1280 if draft else 1440;sc.render.resolution_y=960 if draft else 1080;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
if draft:
 ds=sc.display.shading;ds.light='STUDIO';ds.color_type='MATERIAL';ds.show_shadows=True;ds.show_cavity=True;ds.cavity_type='BOTH';ds.show_object_outline=True;ds.background_type='WORLD';sc.world.color=(.16,.16,.16)
else:
 sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.view_settings.look='Medium High Contrast';sc.view_settings.exposure=.10
 for n,pos,tar,energy,size in [('Preview_Daylight',(6,-15,7),(6.6,-11.6,1.7),450,6),('Preview_Court_Fill',(4,-6,8),(8,-6,1.5),550,7)]:
  l=bpy.data.lights.new(n,'AREA');l.energy=energy;l.shape='DISK';l.size=size;o=bpy.data.objects.new(n,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(tar)-o.location).to_track_quat('-Z','Y').to_euler()
views=[('Gate_Whole_Part_Open',(6.6,-15.9,2.1),(6.6,-11.582,1.95),19,20),('Door_Closed',(6.6,-16.5,1.6),(6.6,-11.582,1.15),42,1),('Door_Panel_Hardware',(5.8,-14.8,1.25),(6.55,-11.58,1.0),42,20),('Marked_Junction',(10.8,-18.2,7.2),(6.9,-11.582,3.2),45,40),('Gate_Courtyard',(4.6,-7.4,2.8),(6.6,-11.582,2.55),21,40),('Balanced_Side',(1,-11.582,3.3),(6.6,-11.582,2.85),38,40)]
only=sys.argv[sys.argv.index('--only')+1:]if'--only'in sys.argv else[];saved=[]
for n,pos,tar,lens,f in views:
 if only and n not in only:continue
 c=bpy.data.objects.new('Preview_'+n,bpy.data.cameras.new('Preview_'+n));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
 if n=='Balanced_Side':c.data.type='ORTHO';c.data.ortho_scale=4.5
 sc.camera=c;sc.frame_set(f);fn=('Draft_'if draft else'V24_07_')+n+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True);saved.append({'file':fn,'frame':f,'position':pos,'target':tar,'lens_mm':lens});print('VIEW COMPLETE',fn,flush=True)
write('V24_07_'+('Draft'if draft else'Preview')+'_States.json',{'model_sha256':sha(P),'real_materials':not draft,'views':saved})
