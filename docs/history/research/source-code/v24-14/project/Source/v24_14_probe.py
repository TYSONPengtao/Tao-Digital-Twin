import bpy,sys,json,numpy as np
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));D=W/'v24_14';D.mkdir(exist_ok=True)
from v24_06_common import snapshot
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_13/Blender/Architecture_Complete_V24_13.blend')
bpy.context.scene.frame_set(40);bpy.context.view_layer.update()
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False,indent=2),encoding='utf8')
rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 me=o.data;me.calc_loop_triangles();v=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);T=np.array(o.matrix_world);v=v@T[:3,:3].T+T[:3,3];lo=v.min(0);hi=v.max(0)
 relevant=any(k in o.name.upper() for k in ['STORAGE','SCREENWALL','SOUTH_SCREEN','PERIMETER','KITCHEN'])
 if relevant:
  row={'name':o.name,'vertices':len(v),'triangles':len(me.loop_triangles),'bounds':[lo.tolist(),hi.tolist()],'materials':[m.name if m else None for m in me.materials],'parent':o.parent.name if o.parent else None,'location':list(o.location),'matrix':T.tolist()};rows.append(row)
  if len(v)<250000 or o.name.startswith('SITE_PERIMETER_JOINED'):
   f=np.array([t.vertices[:] for t in me.loop_triangles]);pi=np.array([t.polygon_index for t in me.loop_triangles]);mi=np.array([p.material_index for p in me.polygons])[pi];u=me.uv_layers.active;uv=np.array([[u.data[li].uv[:] for li in t.loops] for t in me.loop_triangles]) if u else np.zeros((len(f),3,2));np.savez_compressed(D/(o.name+'.npz'),v=v,f=f,mi=mi,uv=uv)
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(rows,ensure_ascii=False),flush=True)
