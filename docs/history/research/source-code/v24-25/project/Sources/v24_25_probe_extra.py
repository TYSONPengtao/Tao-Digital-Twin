import bpy,numpy as np,json
from pathlib import Path
D=Path(__file__).parent/'v24_25';bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_24/Blender/Architecture_Complete_V24_24.blend');bpy.context.scene.frame_set(40);bpy.context.view_layer.update();I=json.loads((D/'Inventory.json').read_text('utf8'))
for n in ['V24_20_Two_Rooms_Continuous_Valley_Roof_Bed']:
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[j].uv[:]for j in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));fn='EXTRA_'+n+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);next(r for r in I if r['name']==n)['file']=fn
(D/'Inventory.json').write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf8')
M={}
for n in ['M_V12_Court_Stone','M_V12_Road_Concrete','M_V12_Terrain_Earth','M_V21_Storage_Worn_Cement','M_V24_20_Unified_Weathered_Gray_Clay']:
 m=bpy.data.materials[n];bs=next((q for q in m.node_tree.nodes if q.type=='BSDF_PRINCIPLED'),None)if m.use_nodes else None;M[n]={'diffuse':list(m.diffuse_color),'principled_base':list(bs.inputs['Base Color'].default_value)if bs else None,'users':[o.name for o in bpy.data.objects if o.type=='MESH'and m.name in o.data.materials]};print(n,M[n],flush=True)
(D/'Material_Comparison.json').write_text(json.dumps(M,indent=2))
