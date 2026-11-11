import bpy,sys,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_03_junction_blender import _mesh
from v24_06_common import snapshot
D=W/'v24_15';O=Path('E:/jz/JIA/Rebuild_V24_15');R=O/'Reports';R.mkdir(parents=True,exist_ok=True);(O/'Blender').mkdir(exist_ok=True)
B=Path('E:/jz/JIA/Rebuild_V24_14/Blender/Architecture_Complete_V24_14.blend');P=O/'Blender/Architecture_Complete_V24_15.blend'
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;write('V24_15_Before_Snapshot.json',snapshot(bpy));sc.frame_set(40);bpy.context.view_layer.update();col=bpy.data.collections.new('V24_15_储藏房传统梁檩椽_四组横披');sc.collection.children.link(col)
for ma in bpy.data.materials:ma.use_fake_user=True
wood=bpy.data.materials['M_V21_Storage_Old_Warm_Window_Timber'].copy();wood.name='M_V24_15_Traditional_Storage_Wood';wood.use_fake_user=True;nt=wood.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.56
link=next((l for l in nt.links if l.to_node==bs and l.to_socket==bs.inputs['Base Color']),None)
if link:
 src=link.from_socket;nt.links.remove(link);h=nt.nodes.new('ShaderNodeHueSaturation');h.inputs['Saturation'].default_value=1.05;h.inputs['Value'].default_value=.54;nt.links.new(src,h.inputs['Color']);nt.links.new(h.outputs['Color'],bs.inputs['Base Color'])
glass=bpy.data.materials.new('M_V24_15_Amber_Transom_Glass');glass.use_nodes=True;glass.use_fake_user=True;bs=next(n for n in glass.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.43,.32,.19,1);bs.inputs['Roughness'].default_value=.29;bs.inputs['IOR'].default_value=1.46
if 'Transmission Weight'in bs.inputs:bs.inputs['Transmission Weight'].default_value=.58
if 'Coat Weight'in bs.inputs:bs.inputs['Coat Weight'].default_value=.12
changes=[];added=[];removed=[];prep=json.loads((D/'Prepared_Geometry.json').read_text())
def wood_uv(o,axis):
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='V24_15_Wood_Grain_Along_Member')
 for face in o.data.polygons:
  for li in face.loop_indices:
   p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
   if axis=='X':q=((p.y+p.z)*1.6,p.x*.64)
   elif axis=='Y':q=((p.x+p.z*.4)*1.6,p.y*.64)
   else:q=((p.x+p.y)*1.6,p.z*.64)
   uv.data[li].uv=q
def replace(n,v,f):
 o=bpy.data.objects[n];old=o.data;iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V24_15');me.from_pydata([iv@Vector(p)for p in v],[],f);me.update()
 for ma in old.materials:me.materials.append(ma)
 o.data=me
 if not old.users:bpy.data.meshes.remove(old)
 changes.append(n);return o
for row in prep['objects']:
 if row['new']:
  o=_mesh(bpy,col,row['name'],row['v'],row['f'],bpy.data.materials[row['material']]);added.append(o.name)
 else:
  o=replace(row['name'],row['v'],row['f'])
  if not row['transfer']:o.data.materials.clear();o.data.materials.append(bpy.data.materials[row['material']])
 wood_uv(o,row['axis'])
 if row['transfer']:
  src=np.load(D/(row['name']+'.npz'));v=src['v'];f=src['f'];mi=src['mi'];uv=src['uv'];tree=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True);layer=o.data.uv_layers.active
  for face in o.data.polygons:
   hit=tree.find_nearest(o.matrix_world@face.center);ti=hit[2]
   if ti is None:continue
   face.material_index=int(mi[ti]);a,b,c=v[f[ti]];u=b-a;vv=c-a;den=(u@u)*(vv@vv)-(u@vv)**2
   if abs(den)<1e-18:continue
   for li in face.loop_indices:
    q=np.array(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co)-a;s=((vv@vv)*(q@u)-(u@vv)*(q@vv))/den;t=((u@u)*(q@vv)-(u@vv)*(q@u))/den;layer.data[li].uv=uv[ti,0]*(1-s-t)+uv[ti,1]*s+uv[ti,2]*t
 else:
  # Keep planar joinery flat; only cylindrical sides receive smooth shading.
  if any(k in o.name for k in ['Round_Rafter','Round_Purlin','Round_Post','Carved_Scroll']):
   for p in o.data.polygons:p.use_smooth=True
 n=o.name;o['V24_15_Photo_Fitted']='123950 / 124130 / 124221 traditional storage roof frame'
for i in [1,2]:
 n=f'V24_11_Storage_Veranda_Column_{i}';o=bpy.data.objects[n];old=o.data;o.data=old.copy();T=o.matrix_world.copy();iv=T.inverted();z0=min((T@v.co).z for v in o.data.vertices);z1=max((T@v.co).z for v in o.data.vertices)
 for v in o.data.vertices:p=T@v.co;p.z=z0+(p.z-z0)*(2.89-z0)/(z1-z0);v.co=iv@p
 o.data.update();o.data.materials.clear();o.data.materials.append(wood);wood_uv(o,'Z');changes.append(n)
n='V24_14_Storage_Curved_Carved_Haunches';bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True);removed.append(n)
views=[('User_Front',(24,-29,5.1),(13.7,-13.4,2.3),45,None),('Eave_Front',(15.94,-19.4,1.85),(15.94,-14.0,2.65),32,None),('Eave_Underside',(14.5,-15.9,1.20),(16,-15.15,3.00),26,None),('Interior_Front',(15.94,-10.75,1.15),(15.94,-14.28,1.68),24,None),('Interior_Roof',(16.0,-11.65,.62),(15.8,-12.05,3.95),18,None),('Gallery',(17.75,-15.45,1.30),(13.5,-15.7,1.60),25,None),('Whole_Site',(28,-32,18),(5,-7,1.3),47,None)]
for n,pos,tar,lens,ortho in views:
 name='V24_15_'+n;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;added.append(name)
sc.camera=bpy.data.objects['V24_15_Eave_Front'];sc.frame_set(40);sc['Version']='V24_15_TRADITIONAL_STORAGE_ROOF_FRAME';sc.render.resolution_x=1600;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
guide='V24.15：参考123950、124130、124221照片，清除储藏房旧屋架残件，重建三榀传统梁架、短柱、七道圆檩及密排圆椽和连续木望板；梁头收在山墙内。两根檐廊圆柱平面位置保留，柱头统一接入水平檐枋，增加挑檐梁、雀替和通透挂落。后退后的门窗位置与开合动作不变，门上增加四组八角花格玻璃横披、木封板和承梁框。广角照片的整体弯曲没有照搬为梁架歪斜。屋顶两坡、瓦面、封闭镬耳山墙、次照壁、厨房地块及全场地保留。全部26扇门的动画动作和1/20/40帧姿态保留。构件按照片近似拟合，非新增现场实测。'
t=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');t.clear();t.write(guide);write('V24_15_Changes.json',{'changed':changes,'added':added,'removed':removed});write('V24_15_Corrections.json',prep['proof']);bpy.ops.wm.save_as_mainfile(filepath=str(P));write('V24_15_Build.json',{'source':str(B),'source_sha256':sha(B),'model':str(P),'sha256':sha(P)});print('SAVED V24.15',str(P),flush=True)
