import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path(r'E:\jz\JIA\Rebuild_V12');bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Complete_Site_V12_LOCAL.blend'));sc=bpy.context.scene;sc.camera=bpy.data.objects['V12_Entrance_Ramp'];cam=sc.camera;corn=cam.data.view_frame(scene=sc);xmi=min(p.x for p in corn);xma=max(p.x for p in corn);ymi=min(p.y for p in corn);yma=max(p.y for p in corn);z=corn[0].z;dep=bpy.context.evaluated_depsgraph_get();rows=[]
for x,y in [(700,730),(780,750),(900,800),(570,610),(1240,700),(700,615),(780,880),(1400,900)]:
 q=Vector((xmi+(x/1600)*(xma-xmi),ymi+(1-y/1000)*(yma-ymi),z));dr=cam.matrix_world.to_quaternion()@q.normalized();hit,loc,nor,face,obj,matrix=sc.ray_cast(dep,cam.matrix_world.translation,dr,distance=1000);rows.append(dict(pixel=[x,y],hit=hit,object=obj.name if obj else None,location=list(loc),normal=list(nor),face=face))
print(json.dumps(rows,indent=2));Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work\v12_terrain\Ramp_Render_Raycast.json').write_text(json.dumps(rows,indent=2))
