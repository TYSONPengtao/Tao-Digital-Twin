from pathlib import Path
import bpy,numpy as np,json
from mathutils import Vector
D=Path(__file__).parent/'v26_1';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V26/Blender/Architecture_Complete_V26.blend');out=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render:continue
 if not any(k in o.name for k in ['ORIGINAL_EXTERIOR_','V24_34_MB7_','SITE_PERIMETER_JOINED_RETAINING_WALL_0_TILE_COPING','SITE_V19_CONTINUOUS_PERIMETER_EAVE','V24_21_Exterior_']):continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],np.float64);f=np.array([t.vertices[:]for t in me.loop_triangles],np.int32);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],np.int32);uv=np.array([[me.uv_layers.active.data[l].uv[:]for l in t.loops]for t in me.loop_triangles],np.float32)if me.uv_layers.active else np.zeros((len(f),3,2));fn=f'EXTRA_{len(out)}.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);out.append({'name':o.name,'file':fn,'bounds':[v.min(0).tolist(),v.max(0).tolist()],'materials':[m.name for m in me.materials],'triangles':len(f)})
(D/'Extra_Index.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8');report={}
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry']:
 o=bpy.data.objects[n];report[n]={'attributes':[(a.name,a.domain,a.data_type)for a in o.data.attributes]}
 for a in o.data.attributes:
  if a.domain=='POINT'and a.data_type=='FLOAT':
   vals=np.array([d.value for d in a.data]);np.save(D/('ATTRIBUTE_'+n+'_'+a.name+'.npy'),vals);report[n][a.name]=[float(vals.min()),float(vals.max())]
mat=bpy.data.materials['M_V24_20_Continuous_AsBuilt_Perimeter'];report['material']={'nodes':[{ 'name':n.name,'type':n.type,'attribute':getattr(n,'attribute_name',''),'inputs':[(i.name,str(i.default_value))for i in n.inputs if hasattr(i,'default_value')]}for n in mat.node_tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in mat.node_tree.links]};(D/'Extra_Probe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('EXTRA_DONE',len(out),flush=True)
