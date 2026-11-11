import bpy,json,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import *
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;draft='--draft'in sys.argv
sc.render.engine='BLENDER_WORKBENCH'if draft else'CYCLES'
sc.render.resolution_x=1280 if draft else 1440;sc.render.resolution_y=960 if draft else 1080
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
if draft:
 ds=sc.display.shading;ds.light='STUDIO';ds.color_type='MATERIAL';ds.show_shadows=True;ds.show_cavity=True;ds.cavity_type='BOTH';ds.show_object_outline=True;ds.background_type='WORLD';sc.world.color=(.16,.16,.16)
else:
 sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.view_settings.look='Medium High Contrast';sc.view_settings.exposure=.1
 for n,pos,tar,energy,size in [('Preview_Daylight',(4,-6,8),(8,-6,1.5),650,7),('Preview_Timber_Fill',(5,-7,2.6),(8.7,-7,2.8),110,3)]:
  l=bpy.data.lights.new(n,'AREA');l.energy=energy;l.shape='DISK';l.size=size;o=bpy.data.objects.new(n,l);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(tar)-o.location).to_track_quat('-Z','Y').to_euler()
views=[
 ('Gate_Courtyard',(4.6,-7.4,2.8),(6.6,-11.582,2.85),21,None),
 ('Balanced_Side',(1,-11.582,3.3),(6.6,-11.582,3.1),38,4.5),
 ('Gate_Kitchen_Clearance',(4.2,-6.7,3.7),(7.65,-11.4,3.7),30,None),
 ('Kitchen_Timber',(6.85,-9.6,1.45),(8.5,-6,2.58),25,None),
 ('Passage_Paved',(-1,-12.5,25),(-1,-12.5,0),50,32),
 ('Gate_Roof_Top',(10.8,-18.2,7.2),(6.9,-11.582,3.2),45,None)
]
only=sys.argv[sys.argv.index('--only')+1:]if'--only'in sys.argv else[];saved=[]
for n,pos,tar,lens,ortho in views:
 if only and n not in only:continue
 c=bpy.data.objects.new('Preview_'+n,bpy.data.cameras.new('Preview_'+n));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
 if n=='Passage_Paved':sc.render.resolution_x=1600;sc.render.resolution_y=1000
 else:sc.render.resolution_x=1280 if draft else 1440;sc.render.resolution_y=960 if draft else 1080
 sc.camera=c;sc.frame_set(40);fn=('Draft_'if draft else'V24_06_')+n+'.png';sc.render.filepath=str(R/fn);bpy.ops.render.render(write_still=True)
 saved.append({'file':fn,'frame':40,'position':pos,'target':tar,'lens_mm':lens,'ortho_scale':ortho});print('VIEW COMPLETE',fn,flush=True)
write('V24_06_'+('Draft'if draft else'Preview')+'_States.json',{'model_sha256':sha(P),'real_materials':not draft,'material_override':None,'views':saved})
