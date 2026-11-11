import bpy
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid')
bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Reality_Hybrid_V8_LOCAL.blend'))
sc=bpy.context.scene
data=bpy.data.lights.new('Stair_QA_Preview_Light','POINT');data.energy=220;data.shadow_soft_size=.6
ob=bpy.data.objects.new('Stair_QA_Preview_Light',data);sc.collection.objects.link(ob);ob.location=(6.7,9.15,3.0)
sc.camera=bpy.data.objects['V8_Stair_Right_Wall']
sc.cycles.samples=24
sc.render.filepath=str(O/'06_Report/V8_Stair_Right_Wall.png')
bpy.ops.render.render(write_still=True)
print('Stair preview relit for review; exchange geometry and saved blend unchanged',flush=True)
