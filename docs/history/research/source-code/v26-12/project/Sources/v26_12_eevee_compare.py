import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_12/Diagnosis';D.mkdir(exist_ok=True);P=Path('E:/jz/JIA/Rebuild_V26_12/Blender/Architecture_Complete_V26_12_Fast.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1000;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.eevee.taa_render_samples=16
cam=bpy.data.objects.new('EEVEE_Diagnosis',bpy.data.cameras.new('EEVEE_Diagnosis'));sc.collection.objects.link(cam);cam.location=(4.78,-12.75,1.25);cam.rotation_euler=(Vector((5.19,-11.86,1.25))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=37;cam.data.clip_start=.025;sc.camera=cam
for name,enabled in[('EEVEE_01_AO_Off',False),('EEVEE_02_Local_AO',True)]:
 e=sc.eevee;e.use_raytracing=enabled;e.use_fast_gi=enabled
 if enabled:
  e.fast_gi_method='AMBIENT_OCCLUSION_ONLY';e.fast_gi_resolution='2';e.fast_gi_ray_count=2;e.fast_gi_step_count=8;e.fast_gi_distance=.20;e.fast_gi_thickness_near=.025;e.fast_gi_quality=.25;e.ray_tracing_options.trace_max_roughness=0.
 sc.render.filepath=str(D/(name+'.png'));bpy.ops.render.render(write_still=True);print('COMPARE_SAVED',name,flush=True)
 (D/(name+'.json')).write_text(json.dumps({'input_model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'ray_tracing':e.use_raytracing,'fast_gi':e.use_fast_gi,'fast_gi_method':e.fast_gi_method,'distance':e.fast_gi_distance,'extra_lights':0,'saved_file_modified':False},indent=2),'utf8')
