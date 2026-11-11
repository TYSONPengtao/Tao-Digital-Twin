import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V26_15');P=O/'Blender/Architecture_Complete_V26_15.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;g=bpy.data.objects['V26_2_Continuous_Ground_And_Perimeter_Shell'];g.data.calc_loop_triangles();v=np.array([g.matrix_world@v.co for v in g.data.vertices]);f=np.array([t.vertices[:]for t in g.data.loop_triangles]);t=v[f];mask=np.all(t.mean(1)>[8.0285,-11.6401,-.76],1)&np.all(t.mean(1)<[9.5001,-11.0998,-.3999],1);tree=BVHTree.FromPolygons([Vector(p)for p in v],f[mask].tolist(),all_triangles=True)
names=['DOOR_STORAGE_V20_L__LEAF_Geometry','DOOR_STORAGE_V20_R__LEAF_Geometry','SITE_V20_INNER_GATE__LEAF_L_Geometry','SITE_V20_INNER_GATE__LEAF_R_Geometry'];bad=[];mins={n:10. for n in names};poses=0
for frame in range(1,41):
 sc.frame_set(frame);bpy.context.view_layer.update()
 for name in names:
  ob=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());me=ob.to_mesh();me.calc_loop_triangles();vv=[ob.matrix_world@p.co for p in me.vertices];bottom=min(p.z for p in vv);base=-.4 if'STORAGE'in name else-.5;mins[name]=min(mins[name],bottom-base);leaf=BVHTree.FromPolygons(vv,[q.vertices[:]for q in me.loop_triangles],all_triangles=True)
  if tree.overlap(leaf)or bottom-base<.004:bad.append({'frame':frame,'leaf':name,'floor_clearance_m':bottom-base})
  ob.to_mesh_clear();poses+=1
checks=[{'check':'Both storage leaves and both gate leaves keep positive foot clearance and avoid the repaired floor throughout40 evaluated frames','pass':poses==160 and not bad,'poses':poses,'invalid':bad,'minimum_clearance_m':mins}];fail=[r for r in checks if not r['pass']];(O/'Reports/V26_15_Door_Clearance_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'checks':checks,'failures':fail},ensure_ascii=False,indent=2),'utf8');print('DOOR_CLEARANCE',poses,len(fail),flush=True)
