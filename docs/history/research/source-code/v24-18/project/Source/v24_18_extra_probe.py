import bpy,json,numpy as np
from pathlib import Path
D=Path(__file__).parent/'v24_18';P='E:/jz/JIA/Rebuild_V24_17/Blender/Architecture_Complete_V24_17.blend';names=['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','V24_XIESHAN_01_Upper_Two_Main_Slopes','V24_XIESHAN_02_Four_Lower_Hipped_Eaves','V24_XIESHAN_07_Closed_Pale_Ceiling','V24_XIESHAN_08_Five_Continuous_Stepped_Eave_Bands','V24_XIESHAN_09_Continuous_Eave_Bearing_Core','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry']
with bpy.data.libraries.load(P,link=False)as(a,b):b.objects=list(names)
rows=[]
for i,o in enumerate(b.objects):
 bpy.context.scene.collection.objects.link(o);bpy.context.view_layer.update();me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[k].uv[:]for k in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));fn=f'EXTRA_{i:02d}.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);rows.append({'name':o.name,'file':fn,'materials':[m.name for m in me.materials]})
(D/'Extra_Index.json').write_text(json.dumps(rows,indent=2));print('EXTRA_EXPORTED',len(rows),flush=True)
