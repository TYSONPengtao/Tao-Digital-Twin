import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_13_fast_display import apply
D=W/'v26_14/Diagnosis';D.mkdir(exist_ok=True);P=Path('E:/jz/JIA/Rebuild_V26_13/Blender/Architecture_Complete_V26_13.blend');bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();apply();sc.render.resolution_x=900;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.eevee.taa_render_samples=16
views=[('01_Left_WC_From_Rear',(3.25,9.00,4.62),(2.19,7.58,5.90),23),('02_Left_WC_From_Front',(3.15,6.7,4.70),(2.22,7.72,5.60),23),('03_Left_Main_From_Rear',(3.0,8.9,4.65),(3.88,7.32,5.8),23),('04_Right_WC_From_Rear',(9.75,9.0,4.65),(10.80,7.58,5.9),23),('05_Right_WC_From_Front',(9.80,6.7,4.7),(10.78,7.72,5.6),23),('06_Right_Main_From_Rear',(10.0,8.9,4.65),(9.12,7.32,5.8),23)]
for tag,pos,aim,lens in views:
 cam=bpy.data.objects.new('Diagnosis_'+tag,bpy.data.cameras.new('Diagnosis_'+tag));sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_start=.02;sc.camera=cam;sc.render.filepath=str(D/(tag+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(cam,do_unlink=True);print('DIAG_RENDER',tag,flush=True)
