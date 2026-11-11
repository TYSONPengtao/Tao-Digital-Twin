from pathlib import Path
import bpy,sys,json
from mathutils import Vector
R=Path(__file__).parent
P=Path('E:/jz/JIA/Rebuild_V26_4/Blender/Architecture_Complete_V26_4.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=850;sc.render.resolution_y=1100;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard'
sh=sc.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.background_type='WORLD';sc.world.color=(.12,.12,.12);sc.display.render_aa='16'
views=[('RightWCBackCorner',(11.4,8.6,.1),(10.65,9.75,1.5),17),('StairWCBackWindow',(9.7,8.4,1.15),(9.95,9.8,2.5),17),('RightWCBackWindowSide',(11.3,8.9,.6),(10.6,9.8,1.9),20),('RightWCFrontCorner',(12.2,8.8,.2),(10.7,7.4,1.8),17)]
for tag,pos,aim,lens in views:
 c=bpy.data.objects.new(tag,bpy.data.cameras.new(tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=600;sc.camera=c;sc.render.filepath=str(R/(tag+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(c,do_unlink=True);print('DONE',tag,flush=True)
