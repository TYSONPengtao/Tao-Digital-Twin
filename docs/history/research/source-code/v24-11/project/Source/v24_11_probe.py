import bpy,sys,json,numpy as np,bmesh
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_03_junction_blender import _bounds
D=W/'v24_11';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_10/Blender/Architecture_Complete_V24_10.blend')
bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 if any(s in o.name.upper() for s in ['STORAGE','SCREENWALL','PERIMETER','KITCHEN','GATE']):
  bb=_bounds(o)
  row={'name':o.name,'bounds':bb,'materials':[m.name if m else None for m in o.data.materials],'nv':len(o.data.vertices),'nf':len(o.data.polygons)}
  rows.append(row)
  if any(s in o.name for s in ['MASONRY','STORAGE','CURVED_TILE_SHELL','STEPPED_MASONRY_UNDEREAVE','WHITE_INSIDE_FINISH','GATE_STONE','RETAINING_WALL_0_Geometry','Kitchen_Perimeter']):
   o.data.calc_loop_triangles();V=np.array([o.matrix_world@v.co for v in o.data.vertices]);F=np.array([tuple(t.vertices)for t in o.data.loop_triangles]);MI=np.array([t.material_index for t in o.data.loop_triangles]);uv=o.data.uv_layers.active;UV=np.array([[tuple(uv.data[i].uv)for i in t.loops]for t in o.data.loop_triangles])if uv else np.zeros((len(F),3,2));np.savez_compressed(D/(o.name+'.npz'),v=V,f=F,mi=MI,uv=UV)
  if 'STORAGE_TIMBER_COLUMNS_AND_STONE'in o.name:
   bm=bmesh.new();bm.from_mesh(o.data);seen=set();comp=[]
   for v in bm.verts:
    if v in seen:continue
    ss={v};stack=[v];seen.add(v)
    while stack:
     t=stack.pop()
     for e in t.link_edges:
      u=e.other_vert(t)
      if u not in seen:seen.add(u);ss.add(u);stack.append(u)
    vv=np.array([o.matrix_world@k.co for k in ss]);comp.append({'n':len(vv),'min':vv.min(0).tolist(),'max':vv.max(0).tolist()})
   row['components']=comp;bm.free()
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print('INVENTORY',len(rows),flush=True)
for r in rows:
 if any(s in r['name']for s in ['STORAGE_CONNECTED_TIMBER','MASONRY','STEPPED_MASONRY_UNDEREAVE','STONE_BASE','GATE_STONE']):print(json.dumps(r,ensure_ascii=False),flush=True)
