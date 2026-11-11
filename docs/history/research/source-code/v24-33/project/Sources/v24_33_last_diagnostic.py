import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_33';P=Path('E:/jz/JIA/Rebuild_V24_32/Blender/Architecture_Complete_V24_32.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=8;sc.cycles.use_denoising=True;sc.render.resolution_x=960;sc.render.resolution_y=800;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.exposure=-.65
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for x in p.devices:x.use=x.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
for tag,pos in [('F3',(6.5,6.7,9.8)),('F2',(6.,7.7,6.6)),('Kitchen',(7.5,-5.,2.0))]:
 l=bpy.data.lights.new('DIAG_'+tag,'AREA');l.energy=100;l.size=3;o=bpy.data.objects.new(l.name,l);sc.collection.objects.link(o);o.location=pos
views=[('KitchenNorth',(7.8,-1.8,1.25),(8.9,-2.95,1.5),20),('KitchenNorthOutside',(7.6,-2.4,1.25),(9.0,-2.96,1.4),22),('StoragePassage',(12.3,-15.0,1.05),(13.1,-16.4,-.05),22)]
for tag,pos,aim,lens in views:
 c=bpy.data.objects.new('DIAG_'+tag,bpy.data.cameras.new('DIAG_'+tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;sc.camera=c;sc.render.filepath=str(D/('Before_'+tag+'.png'));bpy.ops.render.render(write_still=True);print('DONE',tag,flush=True)
(D/'Last_Diagnostic_Views.json').write_text(json.dumps(views),encoding='utf8')
