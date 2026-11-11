import bpy,sys,json,hashlib,numpy as np,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_03_junction_blender import _mesh
from v24_18_finish import materials,apply_exterior,ArcMap
D=W/'v24_18';O=Path('E:/jz/JIA/Rebuild_V24_18');R=O/'Reports';R.mkdir(parents=True,exist_ok=True);(O/'Blender').mkdir(exist_ok=True);P=O/'Blender/Architecture_Complete_V24_18.blend';source=json.loads((D/'Source.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text())};idx.update({r['name']:r for r in json.loads((D/'Extra_Index.json').read_text())})
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,a):(R/n).write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=source['model']);sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();col=bpy.data.collections.new('V24_18_贴地窄镬耳凹照壁外开窗');sc.collection.children.link(col);changed=[];added=[]
for m in bpy.data.materials:m.use_fake_user=True
mats=materials(prep['uv_route'])
def replace(n,v,f):
 o=bpy.data.objects[n];old=o.data;iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V24_18');me.from_pydata([iv@Vector(p)for p in v],[],f);me.update()
 for m in old.materials:me.materials.append(m)
 o.data=me
 if not old.users:bpy.data.meshes.remove(old)
 changed.append(n);return o
def metric(o):
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='Metres')
 for face in o.data.polygons:
  no=o.matrix_world.to_3x3()@face.normal
  for li in face.loop_indices:
   p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(p.y,p.z)if abs(no.x)>abs(no.y)else(p.x,p.z)
for row in prep['objects']:
 ma=mats.get(row['material'],bpy.data.materials.get(row['material']))
 if row['new']:o=_mesh(bpy,col,row['name'],row['v'],row['f'],ma);added.append(o.name)
 else:o=replace(row['name'],row['v'],row['f'])
 if not row['transfer']:o.data.materials.clear();o.data.materials.append(ma)
 metric(o)
 if row['transfer']:
  src=np.load(D/idx[row['name']]['file']);v=src['v'];f=src['f'];tree=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True);uv=o.data.uv_layers.active
  for face in o.data.polygons:
   ti=tree.find_nearest(o.matrix_world@face.center)[2]
   if ti is None:continue
   face.material_index=int(src['mi'][ti]);a,b,c=v[f[ti]];u=b-a;vv=c-a;den=(u@u)*(vv@vv)-(u@vv)**2
   if abs(den)<1e-18:continue
   for li in face.loop_indices:
    q=np.array(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co)-a;s=((vv@vv)*(q@u)-(u@vv)*(q@vv))/den;t=((u@u)*(q@vv)-(u@vv)*(q@u))/den;uv.data[li].uv=src['uv'][ti,0]*(1-s-t)+src['uv'][ti,1]*s+src['uv'][ti,2]*t
 if any(s in row['name']for s in ['BARREL_TILE_ROWS','LOTUS_DRIP','Ridge','RIDGE_BORDER']):
  for f in o.data.polygons:f.use_smooth=True
for row in prep['vertex_transforms']:
 o=bpy.data.objects[row['name']];iv=o.matrix_world.inverted();assert len(o.data.vertices)==len(row['v'])
 for p,q in zip(o.data.vertices,row['v']):p.co=iv@Vector(q)
 o.data.update();changed.append(o.name)
def parts_mesh(name,parts,new=False,parent=None,pivot=None):
 v=[];f=[];mi=[]
 for j,part in enumerate(parts):
  off=len(v);v+=part['v'];f +=[[x+off for x in face]for face in part['f']];mi +=[j]*len(part['f'])
 if new:o=_mesh(bpy,col,name,v,f,bpy.data.materials[parts[0]['material']]);added.append(o.name)
 else:o=replace(name,v,f)
 o.data.materials.clear()
 for part in parts:o.data.materials.append(bpy.data.materials[part['material']])
 for face,j in zip(o.data.polygons,mi):face.material_index=j
 if parent:
  # New moving geometry starts in world metres; its parent owns the hinge.
  o.parent=parent;o.matrix_parent_inverse.identity();o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
  for p in o.data.vertices:p.co-=Vector(pivot)
 metric(o);return o
for row in prep['windows']:
 parts_mesh(row['name'],[dict(row['fixed_frame'],material='M_Metal_Black'),dict(row['fixed_glass'],material='M_Glass_Clear')])
 for s in row['sashes']:
  root=bpy.data.objects.new('V24_18_'+s['name']+'_Outward_Hinge',None);col.objects.link(root);root.location=s['pivot'];root.empty_display_type='ARROWS';root.empty_display_size=.10;added.append(root.name);root['UE_Interaction']='HINGED_OUTWARD';root['OpenAngleDegrees']=s['angle_degrees'];root['ClosedFrame']=1;root['OpenFrame']=40;root['HingeAxis']='WORLD_Z';root['Opening']='Exterior side / red annotation 190829';root.rotation_mode='XYZ'
  for frame,fac in [(1,0),(20,.5),(40,1)]:root.rotation_euler.z=math.radians(s['angle_degrees'])*fac;root.keyframe_insert(data_path='rotation_euler',index=2,frame=frame)
  root.animation_data.action.name=root.name+'_Action'
  parts_mesh(root.name+'_Frame',[dict(s['frame'],material='M_Metal_Black')],True,root,s['pivot']);parts_mesh(root.name+'_Glass',[dict(s['glass'],material='M_Glass_Clear')],True,root,s['pivot'])
exterior=['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','V24_14_Storage_West_Sealed_Gable','V24_14_Storage_East_Sealed_Gable','V24_Kitchen_Gable_Upper_Brick_Infill','V24_03_Kitchen_Rear_Gable_Wall','V24_18_House_Continuous_Grade_Plinth'];uv_report=[]
mapper=ArcMap(prep['uv_route'])
for n in exterior:
 route=prep['house_uv_route']if n=='V24_18_House_Continuous_Grade_Plinth'else prep['uv_route'];uv_report.append(apply_exterior(bpy.data.objects[n],route,mats,None if n=='V24_18_House_Continuous_Grade_Plinth'else mapper));changed.append(n)
views=[('Narrow_Ears',(25,-20,6.8),(16.6,-13.2,3.15),46),('Screen_Valley',(13.0,-19.3,7.4),(10.30,-17.05,4.0),54),('Screen_Outside',(13,-25,5.1),(7.0,-17.0,2.1),48),('Wall_Continuity',(29,-28,4.2),(12.4,-15.6,-.75),43),('Wall_Rear',(26,1.5,4.5),(15.5,-6,-1.1),43),('House_Front',(20,-18,12.8),(6.8,2.0,5.5),48),('Windows_Detail',(15.3,-7.0,7.0),(10.9,1.1,5.8),52),('House_Grade',(-2.0,7.8,1.0),(0,7.8,.45),24),('Whole_Site',(28,-32,18),(5,-7,1.3),47)]
for n,pos,target,lens in views:
 name='V24_18_'+n;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.04;c.data.clip_end=300;added.append(name)
sc.camera=bpy.data.objects['V24_18_House_Front'];sc.frame_set(40);bpy.context.view_layer.update();sc['Version']='V24_18_NARROW_EARS_GROUNDED_HOUSE_RECESSED_FANS_CONTINUOUS_WALL_AND_OUTWARD_WINDOWS';sc.render.resolution_x=1600;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
guide='V24.18：镬耳改窄直立，储藏房砖耳峰由5.25降至4.91m；四处砖封山墙与灰压顶保留。三层楼板底-0.150m，原地坪约-0.462至-0.480m，下方缺少基座形成约0.31至0.33m透空，现按原首层楼板轮廓补连续实体勒脚，主边顶齐楼板底、底-0.72m，内退8mm的舌口伸入楼板12mm，楼层楼梯和门洞不作整体平移。照壁两端分叉脊之间补出下凹三角瓦面，中心向短檐外侧微降。围墙与储藏房按同一弧长和世界Z坐标排材质，石基/条石/青砖分界统一，青砖灰缝使用米制程序纹理，保留原照片风化色，旧材质和原贴图仍内嵌。大窗10处假白柱切除，转角用细黑框衔接，12扇红圈窗左右侧铰向外打开。第1帧关闭，第20帧半开，第40帧65度全开；原26扇门动作保持。尺寸为照片与既有模型拟合。'
t=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');t.clear();t.write(guide);write('V24_18_Changes.json',{'changed':sorted(set(changed)),'added':sorted(set(added)),'removed':[],'new_materials':list(mats),'outward_window_roots':[o.name for o in col.objects if o.get('UE_Interaction')=='HINGED_OUTWARD']});write('V24_18_Corrections.json',prep['proof']);write('V24_18_Exterior_UV.json',{'route':prep['uv_route'],'surfaces':uv_report});bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_18_Build.json',{'source':source['model'],'source_sha256':source['sha256'],'model':str(P),'sha256':sha(P)});print('SAVED_V24_18',flush=True)
