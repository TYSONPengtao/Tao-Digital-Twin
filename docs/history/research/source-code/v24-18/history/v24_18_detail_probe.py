import bpy,numpy as np,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;D=W/'v24_18';P='E:/jz/JIA/Rebuild_V24_17/Blender/Architecture_Complete_V24_17.blend'
bpy.ops.wm.open_mainfile(filepath=P);bpy.context.scene.frame_set(40);bpy.context.view_layer.update();out={}
names=['SITE_V16_GRADED_INTERIOR_SOIL_Geometry','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','WINDOW_FRONT_CENTER_F3_Geometry']
for i,n in enumerate(names):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[k].uv[:]for k in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));fn=f'DETAIL_{i:02d}.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv)
 out[n]={'file':fn,'materials':[m.name for m in me.materials]};q=v[f].mean(1);out[n]['material_ranges']={m.name:{'faces':int((mi==j).sum()),'z_range':[float(q[mi==j,2].min()),float(q[mi==j,2].max())]}for j,m in enumerate(me.materials)if(mi==j).any()}
 if 'SOIL'in n:
  tree=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True);out['grade_samples']=[]
  for x,y in [(-.4,3),(-.1,3),(0,5),(6,5),(13,5),(13.4,5),(6,10.2),(6,9.8),(1,.8),(12,.8),(6,-.5),(6,1),(3,9),(12,9)]:
   hit=tree.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),8);out['grade_samples'].append({'xy':[x,y],'z':hit[0].z if hit[0]else None})
for n in ['M_V19_Perimeter_Brick','M_V19_Perimeter_Rubble','M_V19_Perimeter_Dark_Courses','M_V18_Storage_Rubble','M_V18_Storage_Dark_Courses','M_V24_17_Stable_Exterior_Blue_Brick']:
 m=bpy.data.materials.get(n)
 if not m:continue
 out[n]={'nodes':[{'name':nd.name,'type':nd.type,'inputs':{s.name:list(s.default_value)if hasattr(s.default_value,'__len__')else s.default_value for s in nd.inputs if hasattr(s,'default_value')and s.type in ['VALUE','VECTOR']}}for nd in m.node_tree.nodes],'links':[[l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name]for l in m.node_tree.links]}
(D/'Detail_Probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in out.items()if k=='grade_samples'or k in names},ensure_ascii=False),flush=True)
