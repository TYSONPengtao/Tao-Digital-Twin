import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v26_14_fast_display import apply
from v26_15_views import VIEWS
D=W/'v26_15/Review';D.mkdir(exist_ok=True);ver=sys.argv[sys.argv.index('--version')+1]if'--version'in sys.argv else'V26_15';P=Path('E:/jz/JIA/Rebuild_'+ver+'/Blender/Architecture_Complete_'+ver+'.blend');bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();apply();sc.render.resolution_x=1100;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.eevee.taa_render_samples=24
for tag,pos,aim,lens in VIEWS:
 if'--only'in sys.argv and tag not in sys.argv[sys.argv.index('--only')+1:]:continue
 cam=bpy.data.objects.new('Review_'+tag,bpy.data.cameras.new('Review_'+tag));sc.collection.objects.link(cam);cam.location=pos;cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_start=.02;sc.camera=cam;name=ver+'_'+tag;sc.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True);(D/(name+'.json')).write_text(json.dumps({'model':str(P),'model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'camera':[pos,aim,lens],'engine':sc.render.engine,'world':sc.world.name,'temporary_lights':0,'model_file_modified':False},indent=2),'utf8');bpy.data.objects.remove(cam,do_unlink=True);print('RENDERED',name,flush=True)
