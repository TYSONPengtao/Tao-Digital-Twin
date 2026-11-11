import bpy,sys,json,numpy as np,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_18';D.mkdir(exist_ok=True);P=Path('E:/jz/JIA/Rebuild_V24_17/Blender/Architecture_Complete_V24_17.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8');rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 me=o.data;v=np.array([o.matrix_world@p.co for p in me.vertices]);n=o.name
 row={'name':n,'bounds':[v.min(0).tolist(),v.max(0).tolist()],'vertices':len(v),'faces':len(me.polygons),'materials':[m.name if m else None for m in me.materials],'parent':o.parent.name if o.parent else None,'matrix':list(map(list,o.matrix_world))}
 export=(not n.startswith(('SITE_','V24_')))or any(k in n for k in ['PERIMETER_JOINED_RETAINING_WALL_0_Geometry','Storage_West_Sealed_Gable','Storage_East_Sealed_Gable','Gable_Stone_Coping','Kitchen_Gable_Upper_Brick_Infill','Kitchen_Rear_Gable_Wall','Kitchen_Curved_Gable_Coping','Kitchen_North_Gable_Coping'])or n.startswith('SITE_SOUTH_SCREENWALL_')or n=='V24_09_Screenwall_Solid_Fork_and_Ridge_Seats'
 if export:
  me.calc_loop_triangles();f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[k].uv[:]for k in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));fn=f'SRC_{len(rows):04d}.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);row['file']=fn
 rows.append(row)
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
materials={}
for m in bpy.data.materials:
 if m.use_nodes:
  tex=[{'name':nd.image.name,'filepath':nd.image.filepath,'size':list(nd.image.size)}for nd in m.node_tree.nodes if nd.type=='TEX_IMAGE'and nd.image]
  if tex:materials[m.name]=tex
(D/'Material_Images.json').write_text(json.dumps(materials,ensure_ascii=False,indent=2),encoding='utf8')
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Source.json').write_text(json.dumps({'model':str(P),'sha256':h}),encoding='utf8')
for row in rows:
 if not row['name'].startswith(('SITE_','V24_'))or any(k in row['name']for k in ['TERRAIN','GROUND','FLOOR','ASBUILT','BASE','GRADE']):print(row['name'],row['bounds'],row['materials'],flush=True)
print('PROBE_COMPLETE',len(rows),flush=True)
