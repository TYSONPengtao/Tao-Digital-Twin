from pathlib import Path
import bpy,json
p=Path('E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend');bpy.ops.wm.open_mainfile(filepath=str(p));sc=bpy.context.scene
print('WORLD',sc.world.name,[(n.name,n.type,[(a.name,str(a.default_value))for a in n.inputs if hasattr(a,'default_value')])for n in sc.world.node_tree.nodes]);print('LIGHTS',[(o.name,o.data.type,o.data.energy,getattr(o.data,'angle',None),o.hide_render,o.hide_get())for o in sc.objects if o.type=='LIGHT']);print('COLOR',sc.view_settings.view_transform,sc.view_settings.look,sc.view_settings.exposure,sc.view_settings.gamma)
for scr in bpy.data.screens:
 for a in scr.areas:
  if a.type=='VIEW_3D': print('VIEW',scr.name,a.spaces.active.shading.type,a.spaces.active.shading.use_scene_world,a.spaces.active.shading.use_scene_lights,a.spaces.active.shading.studio_light,a.spaces.active.shading.studiolight_intensity)
