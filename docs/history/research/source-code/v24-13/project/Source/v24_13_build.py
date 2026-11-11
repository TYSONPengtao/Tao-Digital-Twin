import bpy,bmesh,sys,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W0=Path(__file__).parent;sys.path.insert(0,str(W0))
from v24_03_junction_blender import _mesh,_bounds,_closed_stats
from v24_06_common import snapshot
from v24_09_roof import Batch
from v24_13_geometry import *
D=W0/'v24_13';O=Path('E:/jz/JIA/Rebuild_V24_13');R=O/'Reports';R.mkdir(parents=True,exist_ok=True);(O/'Blender').mkdir(exist_ok=True)
B=Path('E:/jz/JIA/Rebuild_V24_12/Blender/Architecture_Complete_V24_12.blend');P=O/'Blender/Architecture_Complete_V24_13.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;before=snapshot(bpy);write('V24_13_Before_Snapshot.json',before);sc.frame_set(40);bpy.context.view_layer.update();col=bpy.data.collections.new('V24_13_水平次照壁与平整储藏房屋顶');sc.collection.children.link(col)
# Preserve prior unused reference shaders as well as assigned shaders on save.
for ma in bpy.data.materials:ma.use_fake_user=True
changes=[];added=[];proof=json.loads((D/'Prepared_Geometry.json').read_text())['proof']
def changed(n,op,**extra):changes.append({'name':n,'operation':op,**extra})
def metric(o):
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='V24_13_Metric_UV')
 for p in o.data.polygons:
  no=o.matrix_world.to_3x3()@p.normal;ma=o.data.materials[p.material_index].name;rep=(1.6,.9)if'Brick'in ma else(1,1)
  for li in p.loop_indices:
   v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=((v.y if abs(no.x)>abs(no.y)else v.x)/rep[0],v.z/rep[1])if abs(no.z)<.75 else(v.x,v.y)
def replacement(n,v,f):
 ob=bpy.data.objects[n];old=ob.data;iv=ob.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V24_13');me.from_pydata([iv@Vector(p)for p in v],[],f);me.update()
 for ma in old.materials:me.materials.append(ma)
 ob.data=me;metric(ob)
 if not old.users:bpy.data.meshes.remove(old)
 ob['V24_13_Correction']='Level secondary screen wall and planar storage roof'
 return ob
def timber_transfer_source():
 o=bpy.data.objects['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry'];me=o.data;me.calc_loop_triangles();v=np.array([timber(o.matrix_world@p.co)for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[li].uv[:]for li in t.loops]for t in me.loop_triangles]);tr=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True);return v,f,mi,uv,tr
transfer=timber_transfer_source()
for row in json.loads((D/'Prepared_Geometry.json').read_text())['objects']:
 if row.get('new'):
  o=_mesh(bpy,col,row['name'],row['v'],row['f'],bpy.data.materials[row['material']]);metric(o);added.append(o.name)
 else:
  o=replacement(row['name'],row['v'],row['f']);changed(row['name'],'analytical closed solid replacement',closed_bodies=row['bodies'],volume_m3=row['volume_m3'])
 if row['name']=='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry':
  v,f,mi,uv,tr=transfer;layer=o.data.uv_layers.active
  for face in o.data.polygons:
   hit=tr.find_nearest(o.matrix_world@face.center)
   if hit[2]is None:continue
   ti=hit[2];face.material_index=int(mi[ti]);a,b,c=v[f[ti]];u=b-a;vv=c-a;den=(u@u)*(vv@vv)-(u@vv)**2
   if abs(den)<1e-18:continue
   for li in face.loop_indices:
    q=np.array(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co)-a;s=((vv@vv)*(q@u)-(u@vv)*(q@vv))/den;t=((u@u)*(q@vv)-(u@vv)*(q@u))/den;layer.data[li].uv=uv[ti,0]*(1-s-t)+uv[ti,1]*s+uv[ti,2]*t
def mutate(n,fn):
 ob=bpy.data.objects[n];old=ob.data;ob.data=old.copy();T=ob.matrix_world.copy();iv=T.inverted();cnt=0;maxd=0
 for v in ob.data.vertices:
  p=T@v.co;q=Vector(fn(p));delta=(q-p).length
  if delta>1e-7:v.co=iv@q;cnt+=1;maxd=max(maxd,delta)
 ob.data.update()
 if not old.users:bpy.data.meshes.remove(old)
 changed(n,'local native vertex correction; original face materials and UVs retained',changed_vertices=cnt,maximum_move_m=maxd)
 return ob
# Existing lower joinery and the vertical post axes stay in place.
# The prepared timber assembly is already refitted and clipped to the soffit.
for i,(x,y)in enumerate([(13.42,-14.65),(18.26,-15.60)],1):
 n=f'V24_11_Storage_Veranda_Column_{i}';ob=bpy.data.objects[n];z0,z1=np.array(_bounds(ob))[:,2];newtop=roof_z(x,y)-.120
 mutate(n,lambda p,lo=z0,hi=z1,top=newtop:np.array([p.x,p.y,lo+(p.z-lo)*(top-lo)/(hi-lo)]))
# Rebuild courses on the two actual planes. Each tile follows the roof slope,
# and all front tile ends share the same level eave baseline.
tiles=Batch();lat=Vector((1,AXIS,0)).normalized();tilecount=0
def arch(batch,x,ya,yb,rx=.054,thick=.010):
 global tilecount
 v=[];f=[];n=11
 for u in[0,.5,1]:
  yy=ya+(yb-ya)*u;z=surface_z(x,yy);eps=.00001;a=(surface_z(x+eps,yy)-surface_z(x-eps,yy))/(2*eps);bb=(surface_z(x,yy+eps)-surface_z(x,yy-eps))/(2*eps);normal=Vector((-a,-bb,1)).normalized()
  for rr in[rx,rx-thick]:
   for k in range(n):
    an=math.pi*k/(n-1);p=Vector((x,yy,z-.005))+lat*(rr*math.cos(an))+normal*(rr*math.sin(an));v.append(tuple(p))
 for j in range(2):
  a=j*2*n;b=(j+1)*2*n
  for k in range(n-1):f.extend([(a+k,a+k+1,b+k+1,b+k),(a+n+k,b+n+k,b+n+k+1,a+n+k+1)])
  f.extend([(a,b,b+n,a+n),(a+n-1,a+2*n-1,b+2*n-1,b+n-1)])
 for j in[0,2]:
  a=j*2*n
  for k in range(n-1):f.append((a+k,a+n+k,a+n+k+1,a+k+1))
 batch.add(v,f);tilecount+=1
def flat_strip(batch,x0,x1,ya,yb):
 v=[];f=[];n=7
 for dz in[0,-.011]:
  for u in[0,.5,1]:
   yy=ya+(yb-ya)*u
   for k in range(n):x=x0+(x1-x0)*k/(n-1);v.append((x,yy,surface_z(x,yy)-.016+.016*((x-(x0+x1)/2)/((x1-x0)/2))**2+dz))
 N=3*n
 for j in range(2):
  for k in range(n-1):a=j*n+k;f.extend([(a,a+1,a+n+1,a+n),(a+N,a+n+N,a+n+1+N,a+1+N)])
 ring=list(range(n))+[n+n-1,2*n+n-1]+list(range(3*n-2,2*n-1,-1))+[n]
 for a,b in zip(ring,ring[1:]+ring[:1]):f.append((a,a+N,b+N,b))
 batch.add(v,f)
for side,poly in [('south',proof['roof_polygons']['south']),('north',proof['roof_polygons']['north'])]:
 # The small skewed west edge is clipped per row, not bent out of the plane.
 from mathutils.geometry import intersect_line_line_2d
 for x in np.arange(12.89,E-.065,.158):
  yy=[]
  for aa,bb in zip(poly,poly[1:]+poly[:1]):
   if abs(bb[0]-aa[0])<1e-9:continue
   t=(x-aa[0])/(bb[0]-aa[0])
   if -1e-8<=t<=1+1e-8:yy.append(aa[1]+(bb[1]-aa[1])*t)
  if len(yy)<2:continue
  lo,hi=min(yy)+.006,max(yy)-.006
  if hi-lo<.10:continue
  N=max(1,math.ceil((hi-lo)/.32))
  for j in range(N):
   ya=lo+(hi-lo)*j/N+.0015;yb=lo+(hi-lo)*(j+1)/N-.0015;arch(tiles,x,ya,yb)
   if x+.145<E-.03:flat_strip(tiles,x+.041,x+.117,ya,yb)
# Cover the retained kitchen junction with short rows on its two flat flashing facets.
for tri,pp in ADAPTERS:
 pol=np.array(tri)[:,:2].tolist()
 for x in np.arange(min(p[0]for p in pol)+.065,max(p[0]for p in pol)-.06,.158):
  yy=[]
  for aa,bb in zip(pol,pol[1:]+pol[:1]):
   if abs(bb[0]-aa[0])<1e-9:continue
   t=(x-aa[0])/(bb[0]-aa[0])
   if 0<=t<=1:yy.append(aa[1]+(bb[1]-aa[1])*t)
  if len(yy)<2:continue
  lo,hi=min(yy)+.025,max(yy)-.025
  if hi-lo<.07:continue
  N=max(1,math.ceil((hi-lo)/.32))
  for j in range(N):arch(tiles,x,lo+(hi-lo)*j/N+.002,lo+(hi-lo)*(j+1)/N-.002)
n='SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry';tiles.object(col,n,[bpy.data.materials['M_Roof']],True,True);changed(n,'roof tiles rebuilt on planar slopes and horizontal front eave',tile_units=tilecount)
# New level ridge course; retain the original two end ornaments.
ridgebatch=Batch();u=Vector((1,AXIS,0)).normalized();vlat=Vector((-AXIS,1,0)).normalized();n=13
for a in np.arange(W-.02,E+.02,.275):
 b=min(a+.272,E+.04);V=[];F=[]
 for x in[a,b]:
  for rad in[.100,.084]:
   for k in range(n):an=math.pi*k/(n-1);p=Vector((x,ridge(x),RIDGE_Z+.012))+vlat*rad*math.cos(an)+Vector((0,0,rad*math.sin(an)));V.append(tuple(p))
 for k in range(n-1):F.extend([(k,k+1,2*n+k+1,2*n+k),(n+k,3*n+k,3*n+k+1,n+k+1),(k,n+k,n+k+1,k+1),(2*n+k,2*n+k+1,3*n+k+1,3*n+k)])
 F.extend([(0,2*n,3*n,n),(n-1,2*n-1,4*n-1,3*n-1)]);ridgebatch.add(V,F)
dd=np.load(W0/'v24_11/SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry.npz');vv,ix=np.unique(np.round(dd['v'],6),axis=0,return_inverse=True);ff=ix[dd['f']];adj=[set()for _ in vv]
for tri in ff:
 for a,b in zip(tri,np.roll(tri,-1)):adj[a].add(b);adj[b].add(a)
left=set(range(len(vv)));ornaments=0
while left:
 a=left.pop();part={a};stack=[a]
 while stack:
  for b in adj[stack.pop()]:
   if b in left:left.remove(b);part.add(b);stack.append(b)
 ids=sorted(part)
 if vv[ids,2].max()<4.54:continue
 oldy=lambda x:-12.05440044+(x-W)*(-12.24390030+12.05440044)/(E-W)
 oldz=lambda x:4.32490015+(x-W)*(4.33945990-4.32490015)/(E-W)
 V=[(float(vv[k,0]),ridge(vv[k,0])+vv[k,1]-oldy(vv[k,0]),vv[k,2]+RIDGE_Z-oldz(vv[k,0]))for k in ids];remap={k:i for i,k in enumerate(ids)};F=[[remap[k]for k in tri]for tri in ff if all(k in part for k in tri)];ridgebatch.add(V,F);ornaments+=1
n='SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry';ridgebatch.object(col,n,[bpy.data.materials['M_Roof']],True,True);changed(n,'horizontal ridge course with original end ornament geometry',ornament_components=ornaments)
# Valley flashing preserves the kitchen-side anchor, then terminates on the
# planar north slope. It no longer inherits the main-roof twist.
def valley(p):
 x,y,z=map(float,p);w=max(0,min(1,(x-11.68)/(13.5-11.68)));return (x,y,z+w*(surface_z(x,y)-old_surface_z(x,y)))
mutate('SITE_V14_KITCHEN_STORAGE_DIAGONAL_VALLEY_Geometry',valley)
proof.update(source_version='V24.12',scope='Blue-plan front-roof outline: squared sides and eave; level secondary screen preserved; concealed end tucked under eave')
views=[('User_Front',(24,-29,5.1),(13.7,-13.4,2.3),45,None),('Level_Elevation',(14.7,-32,3.0),(14.7,-14,3.0),45,12.5),('Eave_Junction',(12.10,-18.5,3.55),(13.25,-16.22,2.78),38,None),('Top',(15,-12.6,27),(15,-12.6,0),45,18),('Rear_Arc',(23.2,-5.7,8.7),(15.7,-9.2,.7),42,None),('Whole_Site',(28,-32,18),(5,-7,1.3),47,None)]
for n,pos,tar,lens,ortho in views:
 name='V24_13_'+n;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
 added.append(name)
sc.camera=bpy.data.objects['V24_13_User_Front'];sc.frame_set(40);sc['Version']='V24_13_LEVEL_SECONDARY_SCREENWALL_PLANAR_STORAGE_ROOF';sc.render.resolution_x=1600;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
guide='V24.13按蓝线收正储藏房前坡轮廓，左边收回0.438米，前檐恢复直线，屋脊、两坡、木基层同步更新，次照壁原水平墙冠及装饰带保留，端部转入瓦檐下。此前V24.12：次照壁墙冠、檐带和框线统一调平，储藏房屋脊与前檐水平，两主坡面恢复平面；山墙顶边、屋架、两根竖直廊柱的柱头与椽尾相应校正。两柱斜向平面关系、弧形后墙、连续厨房后墙及此前完整建筑与26扇门动画保留。1/20/40帧分别关门/半开/开门。'
t=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');t.clear();t.write(guide);write('V24_13_Changes.json',{'changed':changes,'added':added,'removed':[]});write('V24_13_Corrections.json',proof)
bpy.ops.wm.save_as_mainfile(filepath=str(P));write('V24_13_Build.json',{'source':str(B),'source_sha256':sha(B),'model':str(P),'sha256':sha(P)});print('SAVED V24.13',str(P),flush=True)
