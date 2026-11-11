import bpy,sys,json,numpy as np,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;D=W/'v24_32';sys.path.insert(0,str(W));from v24_qa_blender import _animation
bpy.ops.wm.open_mainfile(filepath='E:/jz/JIA/Rebuild_V24_31/Blender/Architecture_Complete_V24_31.blend');sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
ts={}
for o in bpy.data.objects:
 if o.type!='MESH' or o.hide_render or o.name.startswith('V24_21_'):continue
 if any(t in o.name for t in ['PERIMETER','White_Courtyard_Wall','Continuous_White_Courtyard','Level_White_Wall','FACADE_CONTINUOUS','PARTITIONS_JOINED','FLOOR_FASCIA','HOUSE_V21_','HOUSE_V22_','TERRACE_SIDE_','KZ_','BEAM_']):
  me=o.data;me.calc_loop_triangles();ts[o.name]=(BVHTree.FromPolygons([o.matrix_world@p.co for p in me.vertices],[t.vertices[:]for t in me.loop_triangles],all_triangles=True),[me.polygons[t.polygon_index].material_index for t in me.loop_triangles])
def cast(loc,direction,dist,subset):
 out=[]
 for n,(tree,mi)in ts.items():
  if not subset(n):continue
  q,no,k,dd=tree.ray_cast(Vector(loc),Vector(direction),dist)
  if q is not None:out.append((dd,n,k,list(q),bpy.data.objects[n].data.materials[mi[k]].name,list(no)))
 return min(out)if out else None
segs=json.loads((W/'v16/Drain_Segments.json').read_text('utf8'));hits=[]
for r in segs:
 a=np.array(r['a']);b=np.array(r['b']);c=(a+b)/2;n=(np.array(r['outer_a'])-a+np.array(r['outer_b'])-b)/2;n/=np.linalg.norm(n)
 for z in [.25,1.,1.7,2.0]:
  origin=[*(c+n*.9),z];q=cast(origin,[*-n,0],1.8,lambda n:'PERIMETER'in n or'Courtyard_Wall'in n or'White_Courtyard'in n)
  if q:hits.append({'ci':r['ci'],'j':r['j'],'origin':origin,'z':z,'hit':q})
(D/'Perimeter_Exterior_Probe.json').write_text(json.dumps(hits),encoding='utf8')
print('PERIMETER_MATERIALS',collections.Counter(r['hit'][4]for r in hits))
for r in hits:
 if 'White'in r['hit'][4]or'WHITE'in r['hit'][4]or r['hit'][4]=='M_Wall_Exterior':print('WHITE_OUTSIDE',r)
out=[]
for loc,di,label in [([1.5,5.,8.3],[1,0,0],'east wall'),([1.5,5.,8.3],[0,1,0],'north wall'),([1.5,4.,8.3],[0,-1,0],'front')]:
 for dx in [-1.,-.5,0,.5,1.]:
  for dz in [0.,.65,1.3]:
   p=np.array(loc);p[2]+=dz
   if di[0]:p[1]+=dx
   else:p[0]+=dx
   q=cast(p,di,8,lambda n:True);out.append([label,p.tolist(),q])
print('TERRACE_HITS',out);(D/'Terrace_Probe.json').write_text(json.dumps(out),encoding='utf8')
o=bpy.data.objects['DOOR_STUDY_F3__LEAF'];acts=[]
for frame in [1,20,40]:
 sc.frame_set(frame);bpy.context.view_layer.update();acts.append({'frame':frame,'loc':list(o.location),'rot':list(o.rotation_euler),'matrix':list(map(list,o.matrix_world))})
(D/'Target_Door_Before.json').write_text(json.dumps({'animation':_animation(o),'poses':acts,'matrix_parent_inverse':list(map(list,o.matrix_parent_inverse)),'parent':o.parent.name},indent=2),encoding='utf8');print('DOOR',acts)
