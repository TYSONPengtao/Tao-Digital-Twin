import bpy,math,json
from mathutils import Vector
from pathlib import Path
O=Path(r'E:/jz/JIA/Rebuild_V19');bpy.ops.wm.open_mainfile(filepath=str(O/'05_Export/Actual_Rhino_V19_Readback_LOCAL.blend'));sc=bpy.context.scene;cam=bpy.data.objects['V19_Perimeter_Ordinary_South'];dep=bpy.context.evaluated_depsgraph_get();rows=[]
for x,y in [(290,650),(300,650),(310,650),(285,470)]:
 a=math.tan(cam.data.angle/2);d=Vector(((x/1600-.5)*2*a,(.5-y/1100)*2*a*1100/1600,-1));d=cam.matrix_world.to_3x3()@d.normalized();hit,p,no,f,ob,mt=sc.ray_cast(dep,cam.location,d)
 rows.append({'pixel':[x,y],'hit':hit,'object':ob.name if ob else None,'point':list(p),'material':ob.data.materials[ob.data.polygons[f].material_index].name if ob and ob.type=='MESH' else None})
Path(__file__).with_suffix('.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows),flush=True)
