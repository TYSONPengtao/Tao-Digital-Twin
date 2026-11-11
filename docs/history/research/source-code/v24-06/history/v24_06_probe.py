import bpy,json,sys,bmesh
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_03_junction_blender import _bounds
R=W/'v24_06_probe';R.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_05/Blender/Architecture_Complete_V24_05.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 row={'name':o.name,'bounds':_bounds(o),'materials':[m.name if m else None for m in o.data.materials],'vertices':len(o.data.vertices),'faces':len(o.data.polygons)};rows.append(row)
 if any(s in o.name for s in ['TREE_','REBUILT_COURT','V12_BEFORE_WOOD_','ROUND_PURLIN','EXPOSED_TIMBER','DENSE_WOOD_RAFTER','TRANSVERSE_EAVE','SOIL','COURTYARD_WEST']):print('ITEM',json.dumps(row),flush=True)
(R/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
# Component bounds make it possible to replace duplicate timber details only.
for n in ['SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry','SITE_KITCHEN_V12_LONGITUDINAL_ROUND_PURLINS_Geometry','SITE_V22_KITCHEN_TRANSVERSE_EAVE_TIES_AND_HANGING_ENDS_Geometry']:
 o=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8);remain=set(bm.verts);parts=[]
 while remain:
  v=remain.pop();stack=[v];part=[v]
  while stack:
   for e in stack.pop().link_edges:
    v=e.other_vert(part[-1]) if False else None
   # Traverse through vertex adjacency without modifying geometry.
   break
  stack=part.copy();seen=set(part)
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    q=e.other_vert(v)
    if q not in seen:seen.add(q);remain.discard(q);stack.append(q)
  p=[o.matrix_world@v.co for v in seen];parts.append({'n':len(p),'bounds':[[min(v[i]for v in p)for i in range(3)],[max(v[i]for v in p)for i in range(3)]]})
 bm.free();(R/(n+'.json')).write_text(json.dumps(parts,indent=2),encoding='utf8');print('PARTS',n,len(parts),flush=True)
print('PROBE COMPLETE',flush=True)
