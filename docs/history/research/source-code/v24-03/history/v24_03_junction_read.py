import bpy,json,sys
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;O=W/'v24_03_junction_review';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24_02.blend')
rows=[]
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 b=[ob.matrix_world@Vector(p) for p in ob.bound_box];lo=[min(p[j] for p in b) for j in range(3)];hi=[max(p[j] for p in b) for j in range(3)]
 if hi[0]<3.4 or lo[0]>9.6 or hi[1]<-12.6 or lo[1]>-10.5 or hi[2]<-.7 or lo[2]>4.5:continue
 rows.append({'name':ob.name,'bbox':[lo,hi],'materials':[m.name if m else None for m in ob.data.materials],'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons)})
(O/'Current_Candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:print(r['name'],r['bbox'],r['materials'],flush=True)
