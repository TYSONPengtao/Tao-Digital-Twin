import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_03_junction_blender import _mesh
from v24_06_common import snapshot
D=W/'v24_17';O=Path('E:/jz/JIA/Rebuild_V24_17');R=O/'Reports';R.mkdir(parents=True,exist_ok=True);(O/'Blender').mkdir(exist_ok=True)
B=Path('E:/jz/JIA/Rebuild_V24_16/Blender/Architecture_Complete_V24_16.blend');P=O/'Blender/Architecture_Complete_V24_17.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;write('V24_17_Before_Snapshot.json',snapshot(bpy));sc.frame_set(40);bpy.context.view_layer.update();col=bpy.data.collections.new('V24_17_青砖封边大镬耳与次照壁收口');sc.collection.children.link(col)
for m in bpy.data.materials:m.use_fake_user=True
prep=json.loads((D/'Prepared_Geometry.json').read_text());index={r['name']:r for r in json.loads((D/'Inventory.json').read_text())};changes=[];added=[];removed=[]
stable={}
for src,name in [('M_Roof','M_V24_17_Stable_Gray_Ceramic'),('M_V24_08_AsBuilt_Kitchen_Exterior_Brick','M_V24_17_Stable_Exterior_Blue_Brick')]:
 m=bpy.data.materials[src].copy();m.name=name;m.use_fake_user=True;stable[src]=m
 if m.use_nodes:
  for nd in m.node_tree.nodes:
   if nd.type=='TEX_IMAGE':nd.interpolation='Linear'
   if nd.type=='BSDF_PRINCIPLED':nd.inputs['Roughness'].default_value=max(.84,nd.inputs['Roughness'].default_value);nd.inputs['Metallic'].default_value=0;nd.inputs['Specular IOR Level'].default_value=.20
   if nd.type=='BUMP':nd.inputs['Distance'].default_value=min(.0007,nd.inputs['Distance'].default_value);nd.inputs['Strength'].default_value=min(.25,nd.inputs['Strength'].default_value)
def metric(o):
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='V24_17_Metric_UV')
 for face in o.data.polygons:
  no=o.matrix_world.to_3x3()@face.normal
  for li in face.loop_indices:
   p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
   uv.data[li].uv=((p.y if abs(no.x)>abs(no.y)else p.x)/1.6,p.z/.9)if abs(no.z)<.75 else(p.x,p.y)
def replace(n,v,f):
 o=bpy.data.objects[n];old=o.data;iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V24_17');me.from_pydata([iv@Vector(p)for p in v],[],f);me.update()
 for ma in old.materials:me.materials.append(ma)
 o.data=me
 if not old.users:bpy.data.meshes.remove(old)
 changes.append(n);return o
for row in prep['objects']:
 ma=stable.get(row['material'],bpy.data.materials.get(row['material']))
 if row['new']:o=_mesh(bpy,col,row['name'],row['v'],row['f'],ma);added.append(o.name)
 else:o=replace(row['name'],row['v'],row['f'])
 if not row['transfer']:o.data.materials.clear();o.data.materials.append(ma)
 metric(o)
 if row['transfer']:
  src=np.load(D/index[row['name']]['file']);v=src['v'];f=src['f'];mi=src['mi'];su=src['uv'];tree=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True);layer=o.data.uv_layers.active
  for face in o.data.polygons:
   ti=tree.find_nearest(o.matrix_world@face.center)[2]
   if ti is None:continue
   face.material_index=int(mi[ti]);a,b,c=v[f[ti]];u=b-a;vv=c-a;den=(u@u)*(vv@vv)-(u@vv)**2
   if abs(den)<1e-18:continue
   for li in face.loop_indices:
    q=np.array(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co)-a;s=((vv@vv)*(q@u)-(u@vv)*(q@vv))/den;t=((u@u)*(q@vv)-(u@vv)*(q@u))/den;layer.data[li].uv=su[ti,0]*(1-s-t)+su[ti,1]*s+su[ti,2]*t
  for i,m in enumerate(o.data.materials):
   if m.name in stable:o.data.materials[i]=stable[m.name]
 if any(k in o.name for k in ['TILE_COURSES','Barrel_and_Pan','Eave_Disks','Level_Ridge']):
  for f in o.data.polygons:f.use_smooth=True
 o['V24_17_Correction']='Continuous brick verge and enlarged gable ears / layered roof / secondary screen cap'
for n in prep['remove']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True);removed.append(n)
# Retire the original secondary-wall tile courses from the merged perimeter
# mesh. Whole original triangles outside this local region keep every vertex,
# UV, normal/smoothing and material assignment. No global weld is performed.
n='SITE_PERIMETER_JOINED_RETAINING_WALL_0_TILE_COPING_Geometry';o=bpy.data.objects[n];old=o.data;NV=len(old.vertices);NP=len(old.polygons);co=np.empty(NV*3,np.float32);old.vertices.foreach_get('co',co);co=co.reshape(-1,3);iv=np.empty(len(old.loops),np.int32);old.loops.foreach_get('vertex_index',iv);tot=np.empty(NP,np.int32);old.polygons.foreach_get('loop_total',tot);assert np.all(tot==3);ff=iv.reshape(-1,3);wm=np.asarray(o.matrix_world);wv=co@wm[:3,:3].T+wm[:3,3];q=wv[ff].mean(1);ret=(q[:,0]>10.79)&(q[:,0]<13.18)&(q[:,1]>-17.20)&(q[:,1]<-16.18)&(q[:,2]>2.47)&(q[:,2]<2.85);keep=~ret;nf=int(keep.sum());me=bpy.data.meshes.new(n+'_V24_17_local_retirement');me.vertices.add(NV);me.vertices.foreach_set('co',co.ravel());me.loops.add(nf*3);me.loops.foreach_set('vertex_index',ff[keep].ravel());me.polygons.add(nf);me.polygons.foreach_set('loop_start',np.arange(nf,dtype=np.int32)*3);me.polygons.foreach_set('loop_total',np.full(nf,3,np.int32))
for ma in old.materials:me.materials.append(ma)
for prop,dt in [('material_index',np.int32),('use_smooth',np.bool_)]:
 a=np.empty(NP,dt);old.polygons.foreach_get(prop,a);me.polygons.foreach_set(prop,a[keep])
for layer in old.uv_layers:
 uv=np.empty(len(old.loops)*2,np.float32);layer.data.foreach_get('uv',uv);new=me.uv_layers.new(name=layer.name);new.data.foreach_set('uv',uv.reshape(-1,3,2)[keep].ravel())
me.update();o.data=me;changes.append(n);write('V24_17_Retired_Coping.json',{'name':n,'original_faces':NP,'retired_secondary_faces':int(ret.sum()),'remaining_faces':nf,'all_original_vertices_preserved':True,'outside_triangle_signature_sha256':hashlib.sha256(np.round(wv[ff[keep]],6).tobytes()).hexdigest()})
if not old.users:bpy.data.meshes.remove(old)
views=[('Storage_Outside',(25,-20,6.8),(16.6,-13.2,3.15),46,None),('Storage_West_Gable',(8.6,-16.3,6.8),(13.3,-12.15,3.8),44,None),('Roof_Junction',(16.2,-18.5,10.7),(12.8,-11.0,3.4),50,None),('Kitchen_Rear',(20,3.2,7.5),(11.7,-3.3,2.8),46,None),('Secondary_Outside',(14.7,-20.0,3.7),(12.0,-16.7,2.45),48,None),('Secondary_Gallery',(16.3,-15.7,1.55),(12.9,-16.6,2.30),32,None),('Entry_White_Bay',(17.65,-15.67,1.38),(13.52,-14.85,1.50),25,None),('Whole_Site',(28,-32,18),(5,-7,1.3),47,None)]
for n,pos,tar,lens,ortho in views:
 name='V24_17_'+n;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.05;c.data.clip_end=300
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
 added.append(name)
for screen in bpy.data.screens:
 for a in screen.areas:
  if a.type=='VIEW_3D':a.spaces.active.clip_start=.05;a.spaces.active.clip_end=300
sc.camera=bpy.data.objects['V24_17_Storage_Outside'];sc.frame_set(40);sc['Version']='V24_17_BRICK_VERGES_LARGE_GABLE_EARS_AND_STABLE_ROOF';sc.render.resolution_x=1600;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
guide='V24.17：储藏房与厨房的外侧山墙、屋顶交接处用青砖封齐，上端连续接入加宽加高的镬耳与灰瓦压顶。檐廊内按实景保留梁柱门窗。储藏房重铺两坡筒板瓦，把基层降至板瓦以下，移除多余斜向小瓦檐及木板；厨房屋面与木基层收进端墙，避免外露梁头。按本轮叉号撤去主照壁两侧凸出底座条。次照壁重做连续双坡瓦帽、平直脊、实体承托、内外白色框带及居中卷头，清除原合并模型中的重复旧瓦。新材质保持原贴图、降低微表面反光；新文件视口采用较合适的近远裁剪范围。全部26扇门、入口两柱与柱后白墙、地基弧墙和完整场地保留。尺寸依据照片拟合，非新增现场实测。'
t=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');t.clear();t.write(guide);write('V24_17_Changes.json',{'changed':changes,'added':added,'removed':removed,'new_materials':[m.name for m in stable.values()]});write('V24_17_Corrections.json',prep['proof']);bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_17_Build.json',{'source':str(B),'source_sha256':sha(B),'model':str(P),'sha256':sha(P)});print('SAVED V24.17',str(P),flush=True)
