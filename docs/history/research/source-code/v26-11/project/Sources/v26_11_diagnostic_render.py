import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_11';R=D/'Diagnosis';R.mkdir(exist_ok=True);P=Path('E:/jz/JIA/Rebuild_V26_10/Blender/Architecture_Complete_V26_10.blend');bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.render.resolution_x=1000;sc.render.resolution_y=900;sc.render.resolution_percentage=100
try:
 pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
 for d in pref.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
views=[('Head_Left',(3.10,6.40,4.45),(3.35,7.4,6.8),22),('Feet_Left',(3.1,6.4,4.8),(2.8,7.4,3.55),27),('Reverse_Wall',(3.10,6.40,4.6),(3.4,8.5,5.5),25),('Storage_Closure',(14.0,-15.75,1.75),(13.45,-14.7,3.0),25)]
only=sys.argv[sys.argv.index('--only')+1:]if'--only'in sys.argv else[]
gray=bpy.data.materials.new('DIAGNOSTIC_UNIFORM_GRAY');gray.diffuse_color=(.55,.55,.55,1);gray.use_nodes=True;bs=next(n for n in gray.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.55,.55,.55,1);bs.inputs['Roughness'].default_value=.8
for tag,pos,aim,lens in views:
 if only and tag not in only:continue
 for clay in ([False,True]if tag=='Head_Left'else[False]):
  sc.view_layers[0].material_override=gray if clay else None
  c=bpy.data.objects.new(tag,bpy.data.cameras.new(tag));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.03;sc.camera=c;sc.render.filepath=str(R/(tag+('_Clay'if clay else'')+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(c,do_unlink=True);print('DIAG_RENDER',tag,clay,flush=True)
