import bpy,json
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24/Blender/Architecture_Complete_V24_02.blend')
rows=[]
for ob in bpy.data.objects:
 if ob.type!='MESH' or not any(t in ob.name for t in ['KITCHEN','STORAGE','Kitchen']):continue
 p=[ob.matrix_world@Vector(v) for v in ob.bound_box];r={'name':ob.name,'bbox':[[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]],'verts':len(ob.data.vertices),'mats':[m.name if m else None for m in ob.data.materials]}
 if ob.parent and 'Parameters'in ob.parent:
  try:
   d=json.loads(ob.parent['Parameters']);r['parameters_keys']=list(d);r['parts_count']=len(d.get('parts',[]));r['parts']=[{'type':p.get('geometry',{}).get('type'),'material':p.get('material')} for p in d.get('parts',[])][:10]
  except Exception:pass
 rows.append(r)
(W/'v24_kitchen_inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print('KITCHEN INVENTORY',len(rows),flush=True)
