import bpy,sys,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));O=W/'v24_03_junction_review'
import v24_xieshan_roof_blender as roof
import v24_03_junction_blender as junction
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24_02.blend')
roof.apply_v24_xieshan_roof(bpy,O)
q=junction.apply_v24_03_junction(bpy,O)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.render.resolution_x=1400;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
for name,pos,tar in [('Junction_Kitchen',(10,-15.6,4.7),(8.7,-11.3,3.0)),('Junction_Left',(3.6,-14.7,2.0),(4.95,-11.7,1.1))]:
 cam=bpy.data.objects.new(name,bpy.data.cameras.new(name));sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(tar)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=46;sc.camera=cam;sc.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
print('JUNCTION_TEST_COMPLETE',q['status'],flush=True)
