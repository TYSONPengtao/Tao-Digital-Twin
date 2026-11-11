import bpy,sys,json,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_13';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_12/Blender/Architecture_Complete_V24_12.blend')
sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
names=['SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry','SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry','SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry','SITE_V14_KITCHEN_STORAGE_DIAGONAL_VALLEY_Geometry','SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry','V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry','V24_11_Storage_Curved_Rear_Interior_White_Finish','V24_11_Storage_Veranda_Column_1','V24_11_Storage_Veranda_Column_2','SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_0_TILE_COPING_Geometry','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry','SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES_Geometry','V24_10_Secondary_Screenwall_Closed_Panel_Band','V24_10_Secondary_Screenwall_Panel_Mouldings']
rows=[]
for n in names:
 o=bpy.data.objects.get(n)
 if not o:continue
 me=o.data;me.calc_loop_triangles();v=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);T=np.array(o.matrix_world);v=v@T[:3,:3].T+T[:3,3]
 f=np.array([t.vertices[:] for t in me.loop_triangles]);pi=np.array([t.polygon_index for t in me.loop_triangles]);mi=np.array([p.material_index for p in me.polygons])[pi]
 np.savez_compressed(D/(n+'.npz'),v=v,f=f,mi=mi)
 mask=(v[:,0]>10.79)&(v[:,0]<13.35)&(v[:,1]<-16.0)&(v[:,1]>-17.4)&(v[:,2]>1.9)
 rows.append({'name':n,'vertices':len(v),'faces':len(f),'bounds':[v.min(0).tolist(),v.max(0).tolist()],'materials':[m.name if m else None for m in me.materials],'secondary_region_count':int(mask.sum()),'secondary_region_bounds':[v[mask].min(0).tolist(),v[mask].max(0).tolist()]if mask.any()else None})
(D/'Inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(rows,ensure_ascii=False,indent=2),flush=True)
