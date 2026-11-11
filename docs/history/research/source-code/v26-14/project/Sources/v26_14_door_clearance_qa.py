import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V26_14');P=O/'Blender/Architecture_Complete_V26_14.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;ch=json.loads((O/'Reports/V26_14_Changes.json').read_text('utf8'));regions=ch['proof']['patches']+ch['proof']['head_seats'];faces=[[0,1,3],[0,3,2],[4,6,7],[4,7,5],[0,4,5],[0,5,1],[2,3,7],[2,7,6],[0,2,6],[0,6,4],[1,5,7],[1,7,3]];fixed=[]
for r in regions:
 lo,hi=map(np.asarray,r['bounds_m']);vs=[Vector((x,y,z))for z in[lo[2],hi[2]]for y in[lo[1],hi[1]]for x in[lo[0],hi[0]]];fixed.append((r,BVHTree.FromPolygons(vs,faces,all_triangles=True),lo,hi))
leaves=[o for o in sc.objects if o.type=='MESH'and o.name.startswith('DOOR_BATH_')and o.name.endswith('__LEAF_Geometry')];bad=[];poses=0
for frame in range(1,41):
 sc.frame_set(frame);bpy.context.view_layer.update()
 for ob in leaves:
  eo=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eo.to_mesh();me.calc_loop_triangles();v=np.array([eo.matrix_world@v.co for v in me.vertices]);f=[t.vertices[:]for t in me.loop_triangles];tree=BVHTree.FromPolygons([Vector(p)for p in v],f,all_triangles=True);lo,hi=v.min(0),v.max(0);poses+=1
  for r,solid,mn,mx in fixed:
   if np.any(hi<mn)or np.any(lo>mx):continue
   inside=np.all((v>mn+1e-6)&(v<mx-1e-6),axis=1)
   if tree.overlap(solid)or inside.any():bad.append({'frame':frame,'leaf':ob.name,'floor':r['floor'],'side':r['side']})
  eo.to_mesh_clear()
checks=[{'check':'Five WC leaves clear all four wall-end repairs and four completed heads throughout40 evaluated frames','pass':not bad and poses==200,'poses':poses,'invalid':bad}]
(O/'Reports/V26_14_Door_Clearance_QA.json').write_text(json.dumps({'status':'PASS'if all(r['pass']for r in checks)else'FAIL','model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'checks':checks,'failures':[r for r in checks if not r['pass']]},ensure_ascii=False,indent=2),'utf8');print('DOOR_CLEARANCE',poses,not bad,flush=True)
