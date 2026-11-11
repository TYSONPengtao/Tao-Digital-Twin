import bpy,json,sys,numpy as np,hashlib
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_30';D.mkdir(exist_ok=True)
P=Path('E:/jz/JIA/Rebuild_V24_29/Blender/Architecture_Complete_V24_29.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
rows=[];exports=[]
terms=['SITE_','CONSTRUCTION_COURTYARD','Matching_Stone','High_Approach','Graded_Road','PERIMETER','White_Wall','Retaining','Courtyard_Stone','GATE_','WALL_','ONE_SOLID_ENTRY','PLANTER','GAZEBO']
for o in bpy.data.objects:
 pts=[o.matrix_world@Vector(p)for p in o.bound_box]if o.type in ['MESH','CURVE']else []
 row={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],'bounds':[[min(p[i]for p in pts)for i in range(3)],[max(p[i]for p in pts)for i in range(3)]]if pts else None,'props':{k:str(v)for k,v in o.items()}}
 rows.append(row)
 if o.type=='MESH' and not o.hide_render and any(t in o.name for t in terms):
  me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2))
  fn='SRC_'+str(len(exports))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv)
  exports.append(dict(row,file=fn,materials=[m.name if m else None for m in me.materials],vertices=len(v),triangles=len(f)))
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf8');(D/'Geometry_Index.json').write_text(json.dumps(exports,ensure_ascii=False),encoding='utf8')
print('EXPORTED',len(exports),flush=True)
print(json.dumps([(r['name'],r['bounds'],r['vertices'])for r in exports if any(t in r['name'].upper()for t in ['RETAINING','GRADED','SOIL','ROAD','GATE','ONE_SOLID_ENTRY','PLANTER','GAZEBO','MATCHING'])],ensure_ascii=False),flush=True)
