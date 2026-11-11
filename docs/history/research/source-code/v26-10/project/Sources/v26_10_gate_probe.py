import bpy,numpy as np
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V26_10/Blender/Architecture_Complete_V26_10.blend');sc=bpy.context.scene;sc.frame_set(1);bpy.context.view_layer.update()
def tree(n):
 o=bpy.data.objects[n];eo=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eo.to_mesh();me.calc_loop_triangles();v=np.array([eo.matrix_world@q.co for q in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);eo.to_mesh_clear();return BVHTree.FromPolygons(v,f,all_triangles=True),v,f
a,av,af=tree('V26_10_Inner_Gate_Rectangular_Stone_Piers')
for n in ['SITE_V20_INNER_GATE__LEAF_L_Geometry','SITE_V20_INNER_GATE__LEAF_R_Geometry']:
 b,bv,bf=tree(n);pairs=b.overlap(a);print('PROBE',n,'bounds',bv.min(0),bv.max(0),'pairs',len(pairs),flush=True)
 for i,j in pairs[:15]:print('PAIR',i,j,'leaf',bv[bf[i]].tolist(),'pier',av[af[j]].tolist(),flush=True)
