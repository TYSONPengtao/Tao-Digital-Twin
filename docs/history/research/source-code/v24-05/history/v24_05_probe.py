import bpy
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_04/Blender/Architecture_Complete_V24_04.blend')
for o in bpy.data.objects:
 if o.type=='LIGHT':print('LIGHT',o.name,tuple(o.matrix_world.translation),o.data.type,flush=True)
for n in ['SITE_V21_GATE_REFERENCE_LAYER_02_Geometry','SITE_V21_GATE_REFERENCE_LAYER_05_Geometry','GATE_V22_PALE_CEILING_DISK_Geometry','SITE_V15_INNER_GATE_HANGING_LANTERNS_Geometry']:
 o=bpy.data.objects[n];print('MATERIALS',n,[m.name for m in o.data.materials],flush=True)
