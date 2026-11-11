from pathlib import Path
import bpy,hashlib,json,math
from mathutils import Vector
W=Path(__file__).parent;P=Path('E:/jz/JIA/Rebuild_V26_8/Blender/Architecture_Complete_V26_8.blend');D=W/'v26_8/Dynamic';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
sc.render.resolution_x=640;sc.render.resolution_y=480;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
c=bpy.data.objects.new('Temporary_Oblique_Step_Review',bpy.data.cameras.new('Temporary_Oblique_Step_Review'));sc.collection.objects.link(c);c.data.lens=25;c.data.clip_start=.025;sc.camera=c;poses=[]
for i in range(12):
 u=i/11;c.location=(6.65-.7*u,9.06+.12*math.sin(math.pi*u),1.75);aim=Vector((6.23,9.68,.84));c.rotation_euler=(aim-c.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(D/f'Step_Oblique_{i:03d}.png');bpy.ops.render.render(write_still=True);poses.append({'frame':i,'position_m':list(c.location),'aim_m':list(aim)});print('DYNAMIC_FRAME_DONE',i,flush=True)
(D/'Metadata.json').write_text(json.dumps({'model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'frames':12,'camera_poses':poses,'engine':'Cycles12samples','temporary_lights':0,'saved_model_unmodified':True,'scope':'Oblique camera sweep for targeted stair-wall visual inspection, together with independent native near-coplanar surface audit. Not a test of all GPU driver or live viewport behavior.'},indent=2),'utf8')
