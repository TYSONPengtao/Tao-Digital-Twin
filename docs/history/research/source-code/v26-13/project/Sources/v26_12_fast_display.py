"""Fast overcast preview, retaining the local occlusion needed to read carving."""
import bpy
def assign_enum(obj,name,preferred):
 if not hasattr(obj,name):return None
 prop=obj.bl_rna.properties.get(name)
 if prop is None:return None
 choices=[i.identifier for i in prop.enum_items];chosen=next((v for v in preferred if v in choices),None)
 if chosen is not None:setattr(obj,name,chosen)
 return chosen
def set_local_ao(sc):
 e=sc.eevee;e.use_raytracing=True;e.use_fast_gi=True;e.fast_gi_method='AMBIENT_OCCLUSION_ONLY';e.fast_gi_resolution='2';e.fast_gi_ray_count=2;e.fast_gi_step_count=8;e.fast_gi_distance=.20;e.fast_gi_thickness_near=.025;e.fast_gi_quality=.25
 # Threshold zero sends rough surfaces to the cheaper AO approximation.
 e.ray_tracing_options.trace_max_roughness=0.
 return {'method':e.fast_gi_method,'resolution':e.fast_gi_resolution,'rays':e.fast_gi_ray_count,'steps':e.fast_gi_step_count,'distance_m':e.fast_gi_distance,'thickness_m':e.fast_gi_thickness_near,'roughness_threshold':e.ray_tracing_options.trace_max_roughness}
def apply(scene=None):
 sc=scene or bpy.context.scene;changes={}
 changes['viewport_texture_limit']=assign_enum(bpy.context.preferences.system,'gl_texture_limit',['CLAMP_2048','2048']);changes['preview_pixel_size']=assign_enum(sc.render,'preview_pixel_size',['2'])
 if hasattr(bpy.context.preferences.view,'show_splash'):bpy.context.preferences.view.show_splash=False
 sc.render.engine='BLENDER_EEVEE';e=sc.eevee;e.taa_samples=8;e.use_shadow_jitter_viewport=False;e.shadow_resolution_scale=.5;e.volumetric_samples=16;assign_enum(e,'shadow_pool_size',['128','256'])
 changes['local_ao']=set_local_ao(sc)
 shadow_lights=[]
 for ob in sc.objects:
  if ob.type=='LIGHT':
   ob.data.use_shadow=ob.name=='V20_INSPECTION_Gate_Soffit'
   if ob.data.use_shadow and ob.data.energy>0:shadow_lights.append(ob.name)
 changes['shadow_lights']=shadow_lights
 for screen in bpy.data.screens:
  for area in screen.areas:
   for space in area.spaces:
    if space.type=='VIEW_3D':
     shade=space.shading;shade.type='MATERIAL';shade.use_scene_lights=True;shade.use_scene_world=True;shade.use_dof=False;space.overlay.show_overlays=False;space.show_gizmo=False;space.clip_end=180.
 changes.update(engine=sc.render.engine,geometry_modified=False,texture_pixels_modified=False)
 return changes
if __name__=='__main__':print('FAST_DISPLAY',apply(),flush=True)
