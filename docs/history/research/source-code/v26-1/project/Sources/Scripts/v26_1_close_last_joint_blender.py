from pathlib import Path
import bpy,numpy as np,json,hashlib
from mathutils import Vector
W=Path(__file__).parent;D=W/'v26_1';O=Path('E:/jz/JIA/Rebuild_V26_1');R=O/'Reports';P=O/'Blender/Architecture_Complete_V26_1.blend';bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);bpy.context.preferences.filepaths.save_version=0
r=json.loads((D/'Last_Joint.json').read_text('utf8'))['object'];a=np.load(D/r['file']);o=bpy.data.objects[r['name']];iv=o.matrix_world.inverted();me=bpy.data.meshes.new(o.name+'_Closed_End_Notch');me.from_pydata([iv@Vector(p)for p in a['v']],[],a['f']);o.data=me
for n in r['materials']:me.materials.append(bpy.data.materials[n])
me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));uv=me.uv_layers.new(name='V26_1_Source_UV');uv.data.foreach_set('uv',a['uv'].astype(np.float32).ravel());me.update();o['V26_1_Repair']=r['reason']
# A narrow MB7 strip still floated outside the modeled gate pier. Remove
# only this redundant high fragment; the original photographed ramp is not
# selected and its vertices, material and UV are never edited.
name='V24_34_MB7_Model_L23_00034100';ob=bpy.data.objects[name];old=ob.data;old.calc_loop_triangles();v=np.array([ob.matrix_world@p.co for p in old.vertices]);f=np.array([t.vertices[:]for t in old.loop_triangles]);tex=np.array([[old.uv_layers.active.data[l].uv[:]for l in t.loops]for t in old.loop_triangles]);mi=np.array([old.polygons[t.polygon_index].material_index for t in old.loop_triangles]);lo=np.array([-12.97,-13.26,.30]);hi=np.array([-12.29,-12.95,2.96]);vv=v.tolist();ff=[];uu=[];mm=[];changed=0
def split(poly,axis,z,sign):
 inside=[];outside=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  a=sign*(p[0][axis]-z);b=sign*(q[0][axis]-z);pin=a>=-1e-9;qin=b>=-1e-9;(inside if pin else outside).append(p)
  if pin!=qin:
   t=a/(a-b);r=(p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1]));inside.append(r);outside.append(r)
 return inside,outside
def emit(poly,mat):
 for j in range(1,len(poly)-1):
  p=[poly[0],poly[j],poly[j+1]];t=np.array([q[0]for q in p])
  if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))<1e-10:continue
  k=len(vv);vv.extend(t);ff.append([k,k+1,k+2]);uu.append([q[1]for q in p]);mm.append(mat)
for face,u,mat in zip(f,tex,mi):
 t=v[face]
 if ((t.max(0)<lo)|(t.min(0)>hi)).any():ff.append(face);uu.append(u);mm.append(mat);continue
 poly=[(p,uv)for p,uv in zip(t,u)];keep=[]
 for k in range(3):
  for z,s in [(lo[k],1),(hi[k],-1)]:
   if not poly:break
   poly,side=split(poly,k,z,s)
   if len(side)>2:keep.append(side)
 if poly:
  changed+=1
  for pp in keep:emit(pp,int(mat))
 else:ff.append(face);uu.append(u);mm.append(mat)
me=bpy.data.meshes.new(name+'_Clean_Gate_Pier');me.from_pydata(vv,[],ff)
for m in old.materials:me.materials.append(m)
me.polygons.foreach_set('material_index',np.array(mm,np.int32));uv=me.uv_layers.new(name='Preserved_Context_Photo_UV');uv.data.foreach_set('uv',np.array(uu,np.float32).ravel());me.update();ob.data=me;ob['V26_1_Repair']='Remove redundant high MB7 scan fragment outside the modeled outer-gate pier; original ramp unchanged'
cache=bpy.data.objects['V24_21_Navigation_Collision'];me=cache.data;me.calc_loop_triangles();v=np.array([p.co[:]for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);data=json.loads((R/'V26_1_Collision_Index.json').read_text('utf8'));vv=[];ff=[];ci=[]
for q in data['objects']:
 n=q['name'];k=len(vv);first=len(ff)
 if n in [r['name'],name]:
  obj=bpy.data.objects[n];m=obj.data;m.calc_loop_triangles();nv=np.array([obj.matrix_world@p.co for p in m.vertices]);nf=np.array([t.vertices[:]for t in m.loop_triangles])
 else:
  fs=f[q['first_triangle']:q['first_triangle']+q['triangles']];ix,inv=np.unique(fs.ravel(),return_inverse=True);nv=v[ix];nf=inv.reshape(-1,3)
 vv.extend(nv);ff.extend(nf+k);ci.append(dict(q,first_triangle=first,triangles=len(nf)))
me=bpy.data.meshes.new('V26_1_Final_Gate_And_Wall_Collision');me.from_pydata(vv,[],ff);me.update();cache.data=me;data.update(objects=ci,triangles=len(ff));(R/'V26_1_Collision_Index.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');ch=json.loads((R/'V26_1_Changes.json').read_text('utf8'));ch['final_visual_repairs']+=['Close the small inherited notch at the secondary brick wall joint','Remove the remaining high MB7 fragment beside the outer gate pier; original ramp protected'];ch['last_joint']=json.loads((D/'Last_Joint.json').read_text('utf8'));ch['last_gate_fragment_triangles_trimmed']=changed;(R/'V26_1_Changes.json').write_text(json.dumps(ch,ensure_ascii=False,indent=2),encoding='utf8');sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
b=json.loads((R/'V26_1_Build.json').read_text('utf8'));b.update(sha256=h,bytes=P.stat().st_size,last_brick_joint_closed=True);(R/'V26_1_Build.json').write_text(json.dumps(b,indent=2),encoding='utf8');print('LAST_JOINT_SAVED',h,'SCAN_TRIANGLES',changed,flush=True)
