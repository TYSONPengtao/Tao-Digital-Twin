import bpy,json
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_28/Blender/Architecture_Complete_V24_28.blend')
sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();cam=bpy.data.objects['V24_28_Continuous_Step_Overview'];dep=bpy.context.evaluated_depsgraph_get();inv=cam.calc_matrix_camera(dep,x=1120,y=800).inverted();out=[]
names=['V24_24_House_Front_Matching_Stone_Paving','V24_28_Continuous_Kitchen_To_House_Step','HOUSE_V20_ONE_SOLID_ENTRY_STEP_AND_PORCH_SUPPORT_Geometry','SITE_KITCHEN_STONE_FLOOR_Geometry','SLAB_JOINED_F1_Geometry']
for px,py in [(350,718),(400,728),(500,745),(600,765),(670,773),(397,565),(720,760),(350,705),(350,730)]:
 p=inv@Vector((2*px/1120-1,1-2*py/800,-1,1));p/=p.w;direction=(cam.matrix_world.to_3x3()@Vector(p[:3])).normalized();hits=[]
 for n in names:
  o=bpy.data.objects[n];iv=o.matrix_world.inverted();hit,loc,no,face=o.ray_cast(iv@cam.location,(iv.to_3x3()@direction).normalized())
  if hit:
   q=o.matrix_world@loc;hits.append({'object':n,'point':list(q),'distance':(q-cam.location).length})
 hits.sort(key=lambda r:r['distance']);out.append({'pixel':[px,py],'hits':hits[:3]})
Path(__file__).with_suffix('.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False,indent=2),flush=True)
