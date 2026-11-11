from pathlib import Path
import bpy,sys,json,hashlib,math,numpy as np
from mathutils import Vector
D=Path(__file__).resolve().parent;P=Path('E:/jz/JIA/Rebuild_V26_6/Blender/Architecture_Complete_V26_6.blend');prep=json.loads((D/'Prepared_Railing.json').read_text('utf8'));row=prep['objects'][0];a=np.load(D/row['file'])
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
source_hash=sha(P);candidate_hash=sha(D/row['file']);bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.render.resolution_x=1000;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:pass
views=[('Lower_U_Return',(8.70,9.10,1.35),(7.78,8.55,.68),48),('F3_Rear_Guard_Ball',(8.68,9.02,8.80),(7.86,8.70,8.15),48)]
for state in (['After']if '--after-only'in sys.argv else['Before','After']):
 if state=='After':
  o=bpy.data.objects[row['name']];iv=o.matrix_world.inverted();me=bpy.data.meshes.new('Candidate_Railing_Preview');me.from_pydata([iv@Vector(v)for v in a['v']],[],a['f']);me.materials.append(bpy.data.materials[row['materials'][0]]);me.polygons.foreach_set('use_smooth',np.ones(len(me.polygons),bool));me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='Candidate_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());me.set_sharp_from_angle(angle=math.radians(38));me.update();o.data=me;bpy.context.view_layer.update()
 for tag,pos,aim,lens in views:
  c=bpy.data.objects.new('Audit_camera',bpy.data.cameras.new('Audit_camera'));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.02;sc.camera=c
  ld=bpy.data.lights.new('Audit_fill','AREA');ld.energy=65;ld.shape='DISK';ld.size=1.3;li=bpy.data.objects.new('Audit_fill',ld);sc.collection.objects.link(li);li.location=c.location;li.rotation_euler=c.rotation_euler
  name=f'{state}_{tag}.png';sc.render.filepath=str(D/name);bpy.ops.render.render(write_still=True);(D/(name[:-4]+'.json')).write_text(json.dumps({'source_model':str(P),'source_model_sha256':source_hash,'candidate_npz_sha256':candidate_hash if state=='After'else None,'state':state,'camera':[pos,aim,lens],'temporary_light_watts':65,'in_memory_preview_only_no_blend_saved':True},indent=2),'utf8');print('RAIL_PREVIEW_DONE',name,flush=True);bpy.data.objects.remove(c,do_unlink=True);bpy.data.objects.remove(li,do_unlink=True)
assert sha(P)==source_hash;print('SOURCE_UNMODIFIED',source_hash,flush=True)
