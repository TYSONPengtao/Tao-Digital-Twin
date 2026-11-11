from pathlib import Path
import bpy,json
P=Path('E:/jz/JIA/Rebuild_V26_5/Blender/Architecture_Complete_V26_5.blend');bpy.ops.wm.open_mainfile(filepath=str(P));out=[]
keys=['type','light','color_type','single_color','studio_light','studiolight_rotate_z','studiolight_background_alpha','studiolight_background_blur','studiolight_intensity','use_studiolight_world','studio_light','show_shadows','show_cavity','cavity_type','curvature_ridge_factor','curvature_valley_factor','show_specular_highlight','show_object_outline','use_scene_lights','use_scene_world','background_type']
for scr in bpy.data.screens:
 for ar in scr.areas:
  if ar.type!='VIEW_3D':continue
  sh=ar.spaces.active.shading;row={'screen':scr.name,'size':[ar.width,ar.height]}
  for k in keys:
   try:v=getattr(sh,k);row[k]=list(v)if hasattr(v,'__len__')and not isinstance(v,str)else v
   except:pass
  out.append(row)
row={'scene_display':True};sh=bpy.context.scene.display.shading
for k in keys:
 try:v=getattr(sh,k);row[k]=list(v)if hasattr(v,'__len__')and not isinstance(v,str)else v
 except:pass
out.append(row);Path(__file__).with_name('Saved_Shading.json').write_text(json.dumps(out,indent=2));print('SHADING_DONE',json.dumps(out),flush=True)
