import bpy,bmesh,sys,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_03_junction_blender import _mesh,_bounds
from v24_06_common import snapshot
from v24_09_roof import Batch,h,X0,X1,CY,HY
from v24_13_geometry import roof_z
D=W/'v24_14';O=Path('E:/jz/JIA/Rebuild_V24_14');R=O/'Reports';R.mkdir(parents=True,exist_ok=True);(O/'Blender').mkdir(exist_ok=True)
B=Path('E:/jz/JIA/Rebuild_V24_13/Blender/Architecture_Complete_V24_13.blend');P=O/'Blender/Architecture_Complete_V24_14.blend'
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;write('V24_14_Before_Snapshot.json',snapshot(bpy));sc.frame_set(40);bpy.context.view_layer.update();col=bpy.data.collections.new('V24_14_封闭山墙_后退隔扇_檐廊与卷头');sc.collection.children.link(col)
for ma in bpy.data.materials:ma.use_fake_user=True
changes=[];added=[];removed=[];prep=json.loads((D/'Prepared_Geometry.json').read_text())
def metric(o):
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='V24_14_Metric_UV')
 for p in o.data.polygons:
  no=o.matrix_world.to_3x3()@p.normal;ma=o.data.materials[p.material_index].name;rep=(1.6,.9)if 'Brick'in ma else(1,1)
  for li in p.loop_indices:
   v=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=((v.y if abs(no.x)>abs(no.y)else v.x)/rep[0],v.z/rep[1])if abs(no.z)<.75 else(v.x,v.y)
def replace(n,v,f):
 o=bpy.data.objects[n];old=o.data;iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V24_14');me.from_pydata([iv@Vector(p)for p in v],[],f);me.update()
 for ma in old.materials:me.materials.append(ma)
 o.data=me;metric(o)
 if not old.users:bpy.data.meshes.remove(old)
 changes.append(n);return o
for row in prep['objects']:
 if row['new']:
  o=_mesh(bpy,col,row['name'],row['v'],row['f'],bpy.data.materials[row['material']]);metric(o);added.append(o.name)
 else:o=replace(row['name'],row['v'],row['f'])
 if row['transfer']:
  src=np.load(D/(row['name']+'.npz'));v=src['v'].copy();f=src['f'];mi=src['mi'];uv=src['uv'];sel=(v[:,0]>=13.30)&(v[:,0]<=18.50)&(v[:,1]>=-15.40)&(v[:,1]<=-14.55)&(v[:,2]<=2.470001);v[sel,1]+=.48;tree=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True);layer=o.data.uv_layers.active
  for face in o.data.polygons:
   hit=tree.find_nearest(o.matrix_world@face.center);ti=hit[2]
   if ti is None:continue
   face.material_index=int(mi[ti]);a,b,c=v[f[ti]];u=b-a;vv=c-a;den=(u@u)*(vv@vv)-(u@vv)**2
   if abs(den)<1e-18:continue
   for li in face.loop_indices:
    q=np.array(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co)-a;s=((vv@vv)*(q@u)-(u@vv)*(q@vv))/den;t=((u@u)*(q@vv)-(u@vv)*(q@u))/den;layer.data[li].uv=uv[ti,0]*(1-s-t)+uv[ti,1]*s+uv[ti,2]*t
for n in ['V24_13_Secondary_Screenwall_Concealed_End_Return','V24_13_Secondary_Screenwall_End_Return_Coping']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True);removed.append(n)
# Recess the complete glazed front and both animated hinge roots together.
n='SITE_V17_STORAGE_VERANDA_TIMBER_ENTRY_FRONT_Geometry';o=bpy.data.objects[n];T=o.matrix_world.copy();T.translation.y+=.48;o.matrix_world=T;changes.append(n)
for n in ['DOOR_STORAGE_V20_L__LEAF','DOOR_STORAGE_V20_R__LEAF']:
 o=bpy.data.objects[n];T=o.matrix_world.copy();T.translation.y+=.48;o.matrix_world=T;changes.append(n)
for n in ['V24_11_Storage_Veranda_Column_1','V24_11_Storage_Veranda_Column_Base_1']:
 o=bpy.data.objects[n];T=o.matrix_world.copy();T.translation.x+=.30;o.matrix_world=T;changes.append(n)
# Remove the isolated tall roof finials; the ridge terminates in the masonry ears.
n='SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry';src=np.load(D/(n+'.npz'));v=src['v'];f=src['f'];adj=[set()for _ in v]
for tri in f:
 for a,b in zip(tri,np.roll(tri,-1)):adj[a].add(b);adj[b].add(a)
left=set(range(len(v)));keep=[]
while left:
 a=left.pop();part={a};stack=[a]
 while stack:
  for b in adj[stack.pop()]:
   if b in left:left.remove(b);part.add(b);stack.append(b)
 ids=np.array(sorted(part));vv=v[ids]
 if vv[:,2].max()<4.54 and 13.52<vv[:,0].mean()<18.40:keep.extend(ids.tolist())
keep=set(keep);F=[tri for tri in f if all(int(k)in keep for k in tri)];ids=sorted(keep);ix={k:i for i,k in enumerate(ids)};replace(n,v[ids],[[ix[int(k)]for k in tri]for tri in F])
# Broader, rounded ceramic branch tips, with continuous closed seats retained.
b=Batch()
for end in [0,1]:
 xe,sg=(X0,-1)if end==0 else(X1,1)
 for side in [-1,1]:
  z=h(xe,CY+side*HY)+.085;V=[];F=[];N=27;S=12
  for j in range(N):
   t=j/(N-1);p=Vector((xe+sg*.055*t*t,CY+side*(HY+.075*t*t),z+.57*t));rad=.025+.055*(1-t)**1.2
   if j==N-1:rad=.018
   for k in range(S):
    a=math.tau*k/S;V.append(tuple(p+Vector((rad*.70*math.cos(a),rad*math.sin(a),0))))
  for j in range(N-1):
   for k in range(S):F.append((j*S+k,j*S+(k+1)%S,(j+1)*S+(k+1)%S,(j+1)*S+k))
  F.extend([tuple(range(S-1,-1,-1)),tuple((N-1)*S+k for k in range(S))]);b.add(V,F)
n='SITE_SOUTH_SCREENWALL_V12_HIGH_RIDGE_FINIALS_Geometry';b.object(col,n,[bpy.data.materials['M_V24_09_Screenwall_Ceramic_0']],True,False,True);changes.append(n)
# Closed fan-tail end rolls give the short hip courses real thickness at their ends.
fans=Batch()
for x in [X0,X1]:
 for y in np.linspace(CY-.61,CY+.61,10):
  z=h(x,y);sg=1 if x==X1 else-1;fans.rod([(x+sg*.005,y,z+.005),(x+sg*.026,y,z+.005)],.041,16)
fans.object(col,'V24_14_Screenwall_Hip_Fan_Tile_End_Disks',[bpy.data.materials['M_V24_09_Screenwall_Ceramic_1']],False,False,True);added.append('V24_14_Screenwall_Hip_Fan_Tile_End_Disks')
# Views include the actual passage, exterior sealed gable and full site.
views=[('User_Front',(24,-29,5.1),(13.7,-13.4,2.3),45,None),('Gallery',(17.75,-15.45,1.30),(13.5,-15.7,1.60),25,None),('Secondary_End',(14.35,-17.15,2.62),(13.10,-16.67,2.72),45,None),('Sealed_Gable',(25,-13.0,4.75),(18.58,-13.1,3.30),45,None),('Screenwall_Roof',(12.8,-21.7,7.5),(7.4,-16.9,3.60),52,None),('Top',(15,-12.6,27),(15,-12.6,0),45,18),('Whole_Site',(28,-32,18),(5,-7,1.3),47,None)]
for n,pos,tar,lens,ortho in views:
 name='V24_14_'+n;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.03
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
 added.append(name)
sc.camera=bpy.data.objects['V24_14_User_Front'];sc.frame_set(40);sc['Version']='V24_14_SEALED_GABLES_RECESSED_STORAGE_VERANDA';sc.render.resolution_x=1600;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
guide='V24.14：按113659、113730、114422等实景照片，储藏房木隔扇、玻璃和两扇门铰链整体后退0.48米，保留两根竖直圆廊柱与斜向柱列。移除入口多余短回墙，重做次照壁白色卷头山花与三层檐口。两侧山墙将梁檩端头封入，增加连续灰色压顶与圆润耳头。去除廊下粗大木封板，改为薄望板、细椽、顺柱梁与曲线托木。主照壁保留分叉屋脊和端部扇形瓦，修整四支圆头翘尖及端瓦收口。储藏房入口铁皮棚继续删除。此前厨房退让、连续后墙、弧形后墙、场地与全部26扇门动画保留。1/20/40帧为关门/半开/开门。数值为配准模型内的修正量，并非新增现场实测。'
t=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');t.clear();t.write(guide);write('V24_14_Changes.json',{'changed':sorted(set(changes)),'added':added,'removed':removed});write('V24_14_Corrections.json',prep['proof'])
bpy.ops.wm.save_as_mainfile(filepath=str(P));write('V24_14_Build.json',{'source':str(B),'source_sha256':sha(B),'model':str(P),'sha256':sha(P)});print('SAVED V24.14',str(P),flush=True)
