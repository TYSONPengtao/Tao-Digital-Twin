import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V26_20');P=O/'Blender/Architecture_Complete_V26_20.blend';D=W/'v26_20';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene
g=bpy.data.objects['V26_2_Continuous_Ground_And_Perimeter_Shell'];g.data.calc_loop_triangles();v=np.array([g.matrix_world@p.co for p in g.data.vertices]);f=np.array([t.vertices[:]for t in g.data.loop_triangles]);t=v[f];mask=np.all(t.max(1)>[14.,-16.5,-.55],1)&np.all(t.min(1)<[18.,-12.,.05],1);tree=BVHTree.FromPolygons([Vector(p)for p in v],f[mask].tolist(),all_triangles=True)
prep=json.loads((D/'Prepared_Doors.json').read_text('utf8'));rows={r['name']:r for r in prep['objects']};minimum={n:10. for n in rows};head={n:10. for n in rows};bad=[];poses=0;proof=[]
for frame in range(1,41):
 sc.frame_set(frame);bpy.context.view_layer.update()
 for name,row in rows.items():
  ob=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());me=ob.to_mesh();me.calc_loop_triangles();vv=[ob.matrix_world@p.co for p in me.vertices];bottom=min(p.z for p in vv);top=max(p.z for p in vv);clearance=bottom+.25;minimum[name]=min(minimum[name],clearance);head[name]=min(head[name],1.774999976-top);leaf=BVHTree.FromPolygons(vv,[q.vertices[:]for q in me.loop_triangles],all_triangles=True);overlap=bool(tree.overlap(leaf))
  if overlap or clearance<.004 or abs(top-row['proof']['old_top_z_m'])>.000005 or head[name]<.015:bad.append({'frame':frame,'leaf':name,'clearance_m':clearance,'header_clearance_m':head[name],'floor_surface_intersection':overlap})
  proof.append({'frame':frame,'leaf':name,'bottom_m':bottom,'top_m':top,'clearance_m':clearance});ob.to_mesh_clear();poses+=1
sc.frame_set(40)
checks=[{'check':'Both storage leaves clear the raised floor throughout40 opening poses with unchanged upper edges','pass':poses==80 and not bad,'poses':poses,'minimum_floor_clearance_m':minimum,'minimum_fixed_header_clearance_m':head,'invalid':bad}, {'check':'Both bottom-trimmed leaf meshes preserve surviving source UV corners exactly','pass':all(r['proof']['uv_proof']['missing_source_corner_uv_pairs']==0 for r in rows.values()),'details':[r['proof']['uv_proof']for r in rows.values()]}]
with P.open('rb')as ff:mh=hashlib.file_digest(ff,'sha256').hexdigest()
fail=[r for r in checks if not r['pass']];(O/'Reports/V26_20_Door_Clearance_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':mh,'checks':checks,'failures':fail,'poses':proof},ensure_ascii=False,indent=2),'utf8');print('DOOR_CLEARANCE_QA',poses,len(fail),flush=True)
if fail:raise AssertionError(fail)
