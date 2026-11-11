import bpy,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_29';D.mkdir(exist_ok=True)
P=Path('E:/jz/JIA/Rebuild_V24_28/Blender/Architecture_Complete_V24_28.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
rows=[]
for o in bpy.data.objects:
    pts=[o.matrix_world@Vector(p)for p in o.bound_box]if o.type in ['MESH','CURVE']else []
    rows.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],
      'bounds':[[min(p[i]for p in pts)for i in range(3)],[max(p[i]for p in pts)for i in range(3)]]if pts else None,
      'location':list(o.location),'matrix':[list(r)for r in o.matrix_world],'action':o.animation_data.action.name if o.animation_data and o.animation_data.action else None,
      'props':{k:str(v)for k,v in o.items()}})
(D/'Scene_Inventory.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8')
print('COLLECTIONS',json.dumps({c.name:len(c.objects)for c in bpy.data.collections},ensure_ascii=False),flush=True)
print('ROOTS',json.dumps([(o.name,o.type)for o in bpy.data.objects if o.parent is None and (o.type=='EMPTY' or o.children)],ensure_ascii=False),flush=True)
print('DONE',len(rows),flush=True)
