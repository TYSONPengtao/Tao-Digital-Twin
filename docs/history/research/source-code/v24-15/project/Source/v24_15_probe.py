import bpy,sys,json,numpy as np
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));D=W/'v24_15';D.mkdir(exist_ok=True)
from v24_06_common import snapshot
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_14/Blender/Architecture_Complete_V24_14.blend')
bpy.context.scene.frame_set(40);bpy.context.view_layer.update();(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False,indent=2),encoding='utf8')
names=['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry','SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES_Geometry','SITE_V17_STORAGE_VERANDA_TIMBER_ENTRY_FRONT_Geometry','V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails','V24_11_Storage_Veranda_Column_1','V24_11_Storage_Veranda_Column_2','V24_14_Storage_Curved_Carved_Haunches','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry','V24_14_Storage_West_Sealed_Gable','V24_14_Storage_East_Sealed_Gable','SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry','DOOR_STORAGE_V20_L__LEAF_Geometry','DOOR_STORAGE_V20_R__LEAF_Geometry']
rows=[]
for n in names:
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[k].uv[:]for k in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));np.savez_compressed(D/(n+'.npz'),v=v,f=f,mi=mi,uv=uv);rows.append({'name':n,'bounds':[v.min(0).tolist(),v.max(0).tolist()],'vertices':len(v),'faces':len(f),'materials':[m.name for m in me.materials]})
 if 'COLUMNS_AND_STONE_BASES'in n:
  print('BASE_VERTICES',v.tolist(),flush=True)
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(rows,ensure_ascii=False),flush=True)
