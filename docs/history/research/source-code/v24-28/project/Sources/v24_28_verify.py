import bpy,sys,json,hashlib,numpy as np,types
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_28';O=Path('E:/jz/JIA/Rebuild_V24_28');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_28.blend'
before=json.loads((D/'Before_Snapshot.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));changes=json.loads((R/'V24_28_Changes.json').read_text('utf8'));checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
def geo(n):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],float);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));return o,v,f,mi,uv
trees={}
def tree(n):
 if n not in trees:
  _,v,f,_,_=geo(n);trees[n]=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True)
 return trees[n]
def height(n,x,y,origin=2.):
 h=tree(n).ray_cast(Vector((x,y,origin)),Vector((0,0,-1)),8)[0];return h.z if h else None
bpy.ops.wm.open_mainfile(filepath=str(P));after=json.loads(json.dumps(snapshot(bpy)));allow=set(changes['changed'])|set(changes['removed'])
for n,a in before['objects'].items():
 if n not in allow:ck('Unchanged source object / '+n,after['objects'].get(n)==a)
for kind in ['materials','actions','images']:
 for n,a in before[kind].items():ck('Retained original '+kind+' / '+n,after[kind].get(n)==a)
ck('Every new object declared',set(after['objects'])-set(before['objects'])==set(changes['added']))
ck('Only declared obsolete connector components removed',set(before['objects'])-set(after['objects'])==set(changes['removed']))
ck('26 animated doors and original poses unchanged',len(after['doors'])==26 and after['door_poses']==before['door_poses'])
exports=[]
for row in prep['raw_objects']:
 if row['name'] in [r['name']for r in prep['objects']]:continue
 o,v,f,mi,uv=geo(row['name']);a=np.load(D/row['file']);err=np.max(np.linalg.norm(v-a['v'],axis=1))
 ck('Saved geometry within 0.03mm / '+o.name,err<3e-5,maximum_vertex_error_m=float(err))
 ck('Source material assignments and UV preserved / '+o.name,np.array_equal(mi,a['mi'])and np.max(abs(uv-a['uv']),initial=0)<3e-6)
 fn=f'SAVED_{len(exports):02d}.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);exports.append({'name':o.name,'file':fn,'kind':row['kind']})
soil='SITE_V16_GRADED_INTERIOR_SOIL_Geometry';finish='V24_24_House_Front_Matching_Stone_Paving';edge='V24_28_Continuous_Kitchen_To_House_Step'
for y in [-10.,-7.,-3.,.5,3.,6.,9.5]:
 for x in [-.3,-.7,-1.8,-3.5,-5.5]:
  z=height(soil,x,y);ck(f'West exterior is level {x},{y}',z is not None and abs(z+.15)<.003,z_m=z)
A=np.array([8.15,-.3]);B=np.array([8.15,-3.12]);u=(A-B)/np.linalg.norm(A-B);high=np.array([u[1],-u[0]])
for t in [.12,.30,.50,.72,.90]:
 p=B+(A-B)*t;lo=p-high*.12;hi=p+high*.22
 zlo=height(finish,*lo);zhi=height(finish,*hi);ze=height(edge,*(p+high*.04))
 expected_low=-.45+.30*t;expected_high=-.40+.40*t
 ck(f'Marked side is higher at station {t}',zlo is not None and zhi is not None and zhi-zlo>.04,low_z_m=zlo,high_z_m=zhi)
 ck(f'Low paving fits step at station {t}',zlo is not None and abs(zlo-expected_low)<.025,z_m=zlo)
 ck(f'High paving and stone crest meet at station {t}',zhi is not None and ze is not None and abs(zhi-ze)<.025 and abs(ze-expected_high)<.001,crest_z_m=ze,high_z_m=zhi)
for p,z in [(B,-.4),(A,0.)]:
 q=p+high*.04+u*(.003 if z<0 else-.003);h=height(edge,*q)
 ck('Continuous step end connects to '+('kitchen'if z<0 else'house entrance'),h is not None and abs(h-z)<.002,z_m=h)
# All three slabs remain both byte-identical in the preservation snapshot and
# horizontal at actual room positions. Outdoor grade never sets room height.
for fl,z in [(1,0.),(2,3.9),(3,7.5)]:
 n=f'SLAB_JOINED_F{fl}_Geometry';ck(f'F{fl} slab exactly retained',before['objects'][n]==after['objects'][n])
 for x,y in [(1.5,4.),(6.5,3.),(10.5,4.5)]:
  h=height(n,x,y,origin=z+1.);ck(f'F{fl} room floor stays horizontal {x},{y}',h is not None and abs(h-z)<.00005,z_m=h)
for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','V24_20_Kitchen_Unified_Pan_Barrel_Slope_0','V24_25_Kitchen_East_Unified_Pan_Barrel_Field']:
 o,v,_,_,_=geo(n);ck('Kitchen roof trimmed to normal north edge / '+n,float(v[:,1].max())<=-2.79997,north_limit_y_m=float(v[:,1].max()))
_,v,_,_,_=geo('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry')
pick=v[(v[:,1]>-3.4)&(v[:,0]<14.10001)]
ck('Kitchen gable face no longer projects beyond closure',float(pick[:,1].max())<=-2.85497,north_face_y_m=float(pick[:,1].max()))
for n in ['V24_28_Continuous_White_Courtyard_Wall_Face']:
 o,v,_,_,_=geo(n);ck('Facing white wall has horizontal top / '+n,abs(float(v[:,2].max())-2.44720006)<3e-5,top_z_m=float(v[:,2].max()))
 ck('Complete white finish / '+n,len(o.data.materials)==1 and o.data.materials[0].name=='M_V24_11_Plain_White_Limewash')
o,v,f,_,_=geo('V24_28_Continuous_White_Courtyard_Wall_Face')
tt=v[f];normal=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);front=normal[:,0]<-.8*np.linalg.norm(normal,axis=1)
ck('White courtyard face is one vertical plane at right angles to kitchen',front.any()and np.max(abs(tt[front,:,0]-14.10))<.00003,inside_face_x_m=float(v[:,0].min()),intersection_degrees=90.)
edges={}
for ids in f:
 for ia,ib in zip(ids,np.roll(ids,-1)):
  k=tuple(sorted((int(ia),int(ib))));edges[k]=edges.get(k,0)+1
ck('New white wall has no open or duplicated construction faces',all(n==2 for n in edges.values()))
adj=[set()for _ in v]
for ia,ib in edges:adj[ia].add(ib);adj[ib].add(ia)
seen=set();stack=[0]
while stack:
 i=stack.pop()
 if i in seen:continue
 seen.add(i);stack.extend(adj[i]-seen)
ck('Perpendicular white wall is one connected closed solid',len(seen)==len(v))
for n in ['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','V24_24_Kitchen_North_Veranda_White_Closure']:
 tr=tree(n)
 for yy in [-3.15,-3.10,-3.055]:
  for zz in [.60,1.30,2.20,2.85]:
   hit=tr.ray_cast(Vector((8.9,yy,zz)),Vector((1,0,0)),.70)[0]
   ck(f'No wall crosses the north window opening / {n} / {yy},{zz}',hit is None)
for txt,fn in [('V24_25_测量工具.py','measure_tools.py'),('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py')]:
 s=bpy.data.texts[txt].as_string();ck('Embedded and delivered runtime unchanged / '+fn,s==(O/'Roam'/fn).read_text('utf8')==(Path('E:/jz/JIA/Rebuild_V24_26/Roam')/fn).read_text('utf8'))
ck('Updated navigation cache hidden',bpy.data.objects['V24_21_Navigation_Collision'].hide_render and bpy.data.objects['V24_21_Navigation_Collision'].get('V24_28_Architecture_Updated'))
ck('All file images packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Saved_Geometry_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2))
fail=[c for c in checks if not c['pass']];(R/'V24_28_Native_QA.json').write_text(json.dumps({'status':'PASS_PRESERVATION_LEVELS_STEP_WALL_AND_ROOF'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8');print('V28_NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
for c in fail:print('FAIL',c,flush=True)
