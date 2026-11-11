"""Surface collision checks also support the retained open CAD door skins."""
import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;D=W/'v26_10';O=Path('E:/jz/JIA/Rebuild_V26_10');P=O/'Blender/Architecture_Complete_V26_10.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene
def tree(o):
 deps=bpy.context.evaluated_depsgraph_get();eo=o.evaluated_get(deps);me=eo.to_mesh();me.calc_loop_triangles();v=[eo.matrix_world@q.co for q in me.vertices];f=[t.vertices[:]for t in me.loop_triangles];b=BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0.);used=np.unique(np.asarray(f));eo.to_mesh_clear();return b,[v[i]for i in used]
def inside(t,p):
 origin=Vector(p);direction=Vector((.8731,.4517,.1834)).normalized();count=0
 for k in range(64):
  hit,no,index,dist=t.ray_cast(origin,direction,100.)
  if hit is None:return count%2==1
  count+=1;origin=hit+direction*.0001
 raise RuntimeError('Unresolved ray parity')
sc.frame_set(40);bpy.context.view_layer.update();obs=['V26_10_Inner_Gate_Rectangular_Stone_Piers','SITE_V21_GATE_REFERENCE_LAYER_01_Geometry'];fixed=[(n,*tree(bpy.data.objects[n]))for n in obs];bad=[];clearance=1e9;details=[]
for fr in range(1,41):
 sc.frame_set(fr);bpy.context.view_layer.update()
 for n in ['SITE_V20_INNER_GATE__LEAF_L_Geometry','SITE_V20_INNER_GATE__LEAF_R_Geometry']:
  b,v=tree(bpy.data.objects[n]);row={'leaf':n,'frame':fr,'intersections':[]}
  for other,t,verts in fixed:
   pairs=b.overlap(t)
   if pairs:row['intersections'].append({'fixed':other,'triangle_pairs':len(pairs)})
   # Ray parity handles the disjoint two-pier union and the concave waist
   # returns. Nearest-face normal signs are ambiguous between two solids.
   aa=np.asarray(verts);groups=[aa[aa[:,0]<6.6],aa[aa[:,0]>6.6]]if 'Rectangular_Stone_Piers'in other else[aa];bounds=[(g.min(0),g.max(0))for g in groups]
   for p in v:
    near=t.find_nearest(p)
    if near[0]is None:continue
    clearance=min(clearance,near[3])
    if any(np.all(np.asarray(p)>lo+1e-6)and np.all(np.asarray(p)<hi-1e-6)for lo,hi in bounds)and inside(t,p):
     row['intersections'].append({'fixed':other,'inside_vertex_m':list(p)});break
  if row['intersections']:bad.append(row)
  details.append(row)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
checks=[{'check':'Both evaluated gate leaves clear rectangular piers, waist, flared feet and tread at every frame1to40','pass':not bad,'poses':80,'minimum_vertex_surface_distance_m':clearance,'invalid':bad}]
out={'status':'PASS'if not bad else'FAIL','model_sha256':h,'checks':checks,'failures':[]if not bad else checks,'method':'Evaluated native CAD door surface BVH triangles plus inside-solid vertex checks; does not assume raw inherited open skins are watertight solids.'};(O/'Reports/V26_10_Gate_Clearance_QA.json').write_text(json.dumps(out,indent=2),'utf8');print('GATE_CLEARANCE',not bad,len(bad),clearance,flush=True)
