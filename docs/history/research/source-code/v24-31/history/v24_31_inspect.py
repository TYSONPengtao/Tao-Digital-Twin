import bpy,json,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_31';D.mkdir(exist_ok=True)
P=Path('E:/jz/JIA/Rebuild_V24_30/Blender/Architecture_Complete_V24_30.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(40);bpy.context.view_layer.update();rows=[];exports=[]
terms=['STAIR','RAIL','BALUST','SLAB_JOINED','BEAM','CEILING','SOFFIT','BAY_','WINDOW_','REVEAL','SILL','FLOOR','ROAD','SOIL','CURB','White_Building_Pad','White_Pl','V24_30_','CONCRETE','PLINTH','PARTITION','FACADE','WALL','FINISH','PAVEMENT']
for o in bpy.data.objects:
 pts=[o.matrix_world@Vector(p)for p in o.bound_box]if o.type in ['MESH','CURVE']else []
 row={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],'matrix':[list(r)for r in o.matrix_world],'bounds':[[min(p[i]for p in pts)for i in range(3)],[max(p[i]for p in pts)for i in range(3)]]if pts else None,'props':{k:str(v)for k,v in o.items()},'materials':[m.name if m else None for m in o.data.materials]if o.type=='MESH'else []};rows.append(row)
 if o.type=='MESH'and not o.hide_render and not o.name.startswith('V24_21_') and any(t.upper()in o.name.upper()for t in terms):
  me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));fn='SRC_'+str(len(exports))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);exports.append(dict(row,file=fn,vertices=len(v),triangles=len(f)))
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8');(D/'Geometry_Index.json').write_text(json.dumps(exports,ensure_ascii=False),encoding='utf8')
mats={}
for m in bpy.data.materials:
 bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)if m.node_tree else None
 mats[m.name]={'diffuse':list(m.diffuse_color),'base':list(bs.inputs['Base Color'].default_value)if bs else None,'images':[n.image.name for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image]if m.node_tree else []}
(D/'Materials.json').write_text(json.dumps(mats,ensure_ascii=False),encoding='utf8')
print('EXPORTED',len(rows),len(exports),flush=True)
for r in exports:
 if any(t in r['name'].upper()for t in ['STAIR','RAIL','CEILING','SLAB_JOINED','ROOM','ZONE','RED','BAY_WINDOW','SILL_WINDOW','REVEAL','RING_BEAM']):print(r['name'],r['bounds'],r['materials'],flush=True)
