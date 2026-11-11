import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;O=Path('E:/jz/JIA/Rebuild_V26_13');P=O/'Blender/Architecture_Complete_V26_13.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;ch=json.loads((O/'Reports/V26_13_Changes.json').read_text('utf8'))
def tree(o):
 eo=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eo.to_mesh();me.calc_loop_triangles();v=[eo.matrix_world@q.co for q in me.vertices];f=[t.vertices[:]for t in me.loop_triangles];b=BVHTree.FromPolygons(v,f,all_triangles=True);used=np.unique(np.asarray(f));a=np.asarray(v)[used];eo.to_mesh_clear();return b,a,a.min(0),a.max(0)
def inside(t,p):
 origin=Vector(p);direction=Vector((.8731,.4517,.1834)).normalized();count=0
 for k in range(64):
  hit,no,index,dist=t.ray_cast(origin,direction,100.)
  if hit is None:return count%2==1
  count+=1;origin=hit+direction*.0001
 raise RuntimeError('Unresolved ray parity')
sc.frame_set(40);bpy.context.view_layer.update();names=['V26_10_Inner_Gate_Rectangular_Stone_Piers','SITE_V21_GATE_REFERENCE_LAYER_01_Geometry','SITE_V21_GATE_REFERENCE_LAYER_05_Geometry']+[q['name']for q in ch['panels']]+[n for n in ch['retained_headers']if n!='SITE_V21_GATE_REFERENCE_LAYER_05_Geometry']+[ch['waist']];fixed=[(n,*tree(bpy.data.objects[n]))for n in names];bad=[];minimum=1e9
for fr in range(1,41):
 sc.frame_set(fr);bpy.context.view_layer.update()
 for name in['SITE_V20_INNER_GATE__LEAF_L_Geometry','SITE_V20_INNER_GATE__LEAF_R_Geometry']:
  b,v,lo,hi=tree(bpy.data.objects[name]);row={'frame':fr,'leaf':name,'intersections':[]}
  for other,t,pts,pmin,pmax in fixed:
   if np.any(hi<pmin)or np.any(lo>pmax):continue
   pairs=b.overlap(t)
   if pairs:row['intersections'].append({'fixed':other,'triangle_pairs':len(pairs)})
   # Piers/platform are broad closed bodies. The narrow photo inserts
   # additionally get direct evaluated-surface intersections above.
   if other.startswith(('V26_13_Photo_Fit_','V26_12_Restored_'))or other==ch['waist']:continue
   groups=[pts[pts[:,0]<6.6],pts[pts[:,0]>6.6]]if'Rectangular_Stone_Piers'in other else[pts];boxes=[(q.min(0),q.max(0))for q in groups]
   for p in v:
    if not any(np.all(p>mn+1e-6)and np.all(p<mx-1e-6)for mn,mx in boxes):continue
    if inside(t,p):row['intersections'].append({'fixed':other,'inside_vertex_m':p.tolist()});break
  if row['intersections']:bad.append(row)
 if fr%10==0:print('GATE_POSES_CHECKED',fr*2,flush=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
checks=[{'check':'Both evaluated gate leaves clear new faceted piers,21 signed-relief inserts, waist, header and narrow platform throughout frames1to40','pass':not bad,'poses':80,'fixed_objects':len(fixed),'invalid':bad}];(O/'Reports/V26_13_Gate_Clearance_QA.json').write_text(json.dumps({'model_sha256':h,'status':'PASS'if not bad else'FAIL','checks':checks,'failures':[]if not bad else checks,'method':'Actual evaluated native surface BVH intersections and closed-body ray parity; retained gate CAD skins are not assumed watertight solids'},indent=2),'utf8');print('GATE_CLEARANCE',not bad,len(bad),flush=True)
