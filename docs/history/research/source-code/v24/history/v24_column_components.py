import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24_02.blend');rows=[]
for ob in bpy.data.objects:
 if ob.type!='MESH' or not 'KITCHEN'in ob.name:continue
 if not any(t in ob.name for t in ['BEFORE_WOOD_15','BEFORE_WOOD_29','TRADITIONAL_EXPOSED','GROUNDED_OUTER_COLUMN','BEFORE_WOOD_35']):continue
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);remain=set(bm.verts);rr=[]
 while remain:
  v=remain.pop();todo=[v];vs={v}
  while todo:
   for e in todo.pop().link_edges:
    u=e.other_vert(v) if False else None
   # explicit vertex below
   v=next(iter(vs)) if False else v
  # restart conventional flood
  todo=[v]
  while todo:
   a=todo.pop()
   for e in a.link_edges:
    b=e.other_vert(a)
    if b in remain:remain.remove(b);vs.add(b);todo.append(b)
  p=[ob.matrix_world@a.co for a in vs];lo=[min(a[i]for a in p)for i in range(3)];hi=[max(a[i]for a in p)for i in range(3)]
  if hi[2]-lo[2]>1 or len(vs)>100:rr.append({'verts':len(vs),'bbox':[lo,hi]})
 bm.free();rows.append({'name':ob.name,'components':rr})
(W/'v24_column_components.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
