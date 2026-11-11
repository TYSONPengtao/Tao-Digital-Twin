import bpy,json
from mathutils import Vector
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V13');bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V13_Readback_LOCAL.blend'));sc=bpy.context.scene;sc.camera=bpy.data.objects['V13_Native_Canopy_Underside'];cam=sc.camera;deps=bpy.context.evaluated_depsgraph_get();frame=cam.data.view_frame(scene=sc)
rows=[]
for x,y in [[807,530],[810,564],[824,569],[804,474],[833,520],[807,595]]:
 # view_frame: top-right, bottom-right, bottom-left, top-left
 u=x/sc.render.resolution_x;v=y/sc.render.resolution_y;p=frame[3].lerp(frame[0],u).lerp(frame[2].lerp(frame[1],u),v);direction=(cam.matrix_world.to_3x3()@p).normalized();hit,loc,normal,fi,ob,mat=sc.ray_cast(deps,cam.matrix_world.translation,direction)
 rows.append({'pixel':[x,y],'hit':hit,'object':ob.name if hit else None,'local_hit':list(loc) if hit else None,'metadata':ob.parent.get('Parameters','') if hit and ob.parent else ''})
(O/'06_Report/Canopy_Ray_Inspection.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(rows,ensure_ascii=False),flush=True)
