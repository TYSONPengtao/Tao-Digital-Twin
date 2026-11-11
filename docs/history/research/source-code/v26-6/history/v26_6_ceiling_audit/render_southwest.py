from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).parent
P=Path('E:/jz/JIA/Rebuild_V26_5/Blender/Architecture_Complete_V26_5.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=1200;sc.render.resolution_y=850;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard'
sh=sc.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.background_type='WORLD';sc.world.color=(.12,.12,.12);sc.display.render_aa='16'
views=[('F1_Landing_SouthWest',(5.3,8.5,1.15),(2.5,6.6,2.0),16),('F2_Landing_SouthWest',(5.3,8.5,5.05),(2.5,6.6,5.9),16),('F1_Landing_SouthWest2',(5.0,8.8,.6),(2.7,6.6,2.0),16),('F2_Landing_SouthWest2',(5.0,8.8,4.5),(2.7,6.6,5.9),16)]
for tag,pos,aim,lens in views:
 c=bpy.data.objects.new(tag,bpy.data.cameras.new(tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=600;sc.camera=c;sc.render.filepath=str(R/(tag+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(c,do_unlink=True);print('DONE',tag,flush=True)
