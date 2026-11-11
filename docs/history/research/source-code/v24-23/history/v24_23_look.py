import bpy,json,sys
from pathlib import Path
from mathutils import Vector
D=Path(__file__).parent/'v24_23';bpy.ops.wm.open_mainfile(filepath=json.loads((D/'Source.json').read_text())['model']);sc=bpy.context.scene;sc.frame_set(40);sc.render.engine='CYCLES';sc.cycles.samples=4;sc.cycles.use_denoising=True;sc.render.resolution_x=960;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except:pass
views=[('Store_A',(14.2,-13.0,1.13),(13.4,-10.7,2.1),20),('Store_B',(11.8,-14.5,1.13),(13.7,-12.5,2.0),23),('Store_C',(14.7,-15.1,1.13),(13.4,-12.4,2.0),20),('Store_D',(12.0,-10.0,1.13),(13.4,-13.0,2.0),20),('Kitchen_North',(8.85,-8.2,1.13),(8.65,-2.7,1.4),24),('Gate_Front',(6.6,-15.8,1.13),(6.6,-11.6,1.3),25)]
for tag,pos,aim,lens in views:
 c=bpy.data.objects.new(tag,bpy.data.cameras.new(tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;sc.camera=c;sc.render.filepath=str(D/(tag+'_Before.png'));bpy.ops.render.render(write_still=True);print('DONE',tag,flush=True)
