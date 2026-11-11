import bpy,sys,json,numpy as np,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_20';D.mkdir(exist_ok=True);P=Path('E:/jz/JIA/Rebuild_V24_19/Blender/Architecture_Complete_V24_19.blend')
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8');sc.frame_set(40);bpy.context.view_layer.update();rows=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 n=o.name;me=o.data;v=np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64);row={'name':n,'bounds':[v.min(0).tolist(),v.max(0).tolist()],'vertices':len(v),'polygons':len(me.polygons),'materials':[m.name if m else None for m in me.materials],'parent':o.parent.name if o.parent else None,'matrix':list(map(list,o.matrix_world))}
 upper=n.upper();take=any(k in upper for k in ['KITCHEN','PERIMETER_JOINED','STORAGE','F1','DOWNPIPE','DRAIN','GUTTER','ROOF','TILE','BATH','TOILET','STAIR','DOOR','XIESHAN','PAVILION','FLOOR','CONTINUOUS_BALCONY_EDGE'])and not any(k in upper for k in ['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','TREES'])
 if take:
  me.calc_loop_triangles();f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[j].uv[:]for j in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));fn=f'SRC_{len(rows):04d}.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);row['file']=fn
 rows.append(row)
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
materials={}
for m in bpy.data.materials:
 if not m.use_nodes:continue
 if not any(k in m.name.upper()for k in ['BRICK','ROOF','CERAMIC','RUBBLE','STONE','TILE','WALL']):continue
 ns=[]
 for nd in m.node_tree.nodes:
  rr={'type':nd.type,'name':nd.name,'inputs':{s.name:list(s.default_value)if hasattr(s.default_value,'__len__')else s.default_value for s in nd.inputs if hasattr(s,'default_value')and s.type in ['VALUE','VECTOR','RGBA']}}
  if nd.type=='TEX_IMAGE'and nd.image:rr.update(image=nd.image.name,filepath=nd.image.filepath,size=list(nd.image.size),extension=nd.extension)
  ns.append(rr)
 materials[m.name]={'nodes':ns,'links':[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name]for l in m.node_tree.links]}
(D/'Material_Nodes.json').write_text(json.dumps(materials,ensure_ascii=False,indent=2),encoding='utf8')
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Source.json').write_text(json.dumps({'model':str(P),'sha256':h},indent=2),encoding='utf8')
for r in rows:
 if r.get('file')and any(k in r['name'].upper()for k in ['F1','KITCHEN','PERIMETER_JOINED','DRAIN','DOWNPIPE','GUTTER','ROOF']):print(r['name'],r['bounds'],r['materials'],flush=True)
print('V20_PROBE_COMPLETE',len(rows),flush=True)
