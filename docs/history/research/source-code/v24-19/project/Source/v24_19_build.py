import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_03_junction_blender import _mesh
from v24_18_finish import ArcMap,apply_exterior,BRICK,DARK,RUBBLE
D=W/'v24_19';O=Path('E:/jz/JIA/Rebuild_V24_19');R=O/'Reports';R.mkdir(parents=True,exist_ok=True);(O/'Blender').mkdir(exist_ok=True)
P=O/'Blender/Architecture_Complete_V24_19.blend';src=json.loads((D/'Source.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text())
bpy.ops.wm.open_mainfile(filepath=src['model']);sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();col=bpy.data.collections.new('V24_19_实景瓦挑檐与墙边地坪纠正');sc.collection.children.link(col)
changed=[];added=[];removed=[]
for ma in bpy.data.materials:ma.use_fake_user=True
for n in prep['remove']:
 o=bpy.data.objects[n];bpy.data.objects.remove(o,do_unlink=True);removed.append(n)
def replace(n,v,f):
 o=bpy.data.objects[n];old=o.data;iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V24_19');me.from_pydata([iv@Vector(p)for p in v],[],f);me.update();o.data=me
 for m in old.materials:me.materials.append(m)
 if not old.users:bpy.data.meshes.remove(old)
 changed.append(n);return o
route=json.loads((W/'v24_18/Prepared_Geometry.json').read_text())['uv_route'];mapper=ArcMap(route)
def uv_metres(o,brick=False):
 me=o.data;uv=me.uv_layers.active or me.uv_layers.new(name='Metres')
 for f in me.polygons:
  pts=np.array([o.matrix_world@me.vertices[j].co for j in f.vertices]);normal=o.matrix_world.to_3x3()@f.normal
  coords=mapper.triangle(pts)if brick else pts[:,[1,2]]if abs(normal.x)>abs(normal.y)else pts[:,[0,2]]
  if not brick and abs(normal.z)>.8:coords=pts[:,:2]
  for li,q in zip(f.loop_indices,coords):uv.data[li].uv=q
for row in prep['objects']:
 ma=bpy.data.materials[row['material']]
 if row['new']:o=_mesh(bpy,col,row['name'],row['v'],row['f'],ma);added.append(o.name)
 else:o=replace(row['name'],row['v'],row['f'])
 o.data.materials.clear();o.data.materials.append(ma);uv_metres(o,row['material']=='M_V24_18_Continuous_Blue_Brick')
 if 'TILE_COURSES'in o.name or 'Tiled_Verge_Courses'in o.name:
  for f in o.data.polygons:f.use_smooth=True
uv_report=[]
for row in prep['objects']:
 if row['material']!=BRICK:continue
 uv_report.append(apply_exterior(bpy.data.objects[row['name']],route,{n:bpy.data.materials[n]for n in [BRICK,DARK,RUBBLE]},mapper))
for row in prep['raw_objects']:
 o=replace(row['name'],row['v'],row['f']);me=o.data;uv=me.uv_layers.new(name='Preserved_Source_UV')
 for f,mi,tuv in zip(me.polygons,row['mi'],row['uv']):
  f.material_index=mi
  if row['smooth_top']and f.normal.z>.7:f.use_smooth=True
  for li,q in zip(f.loop_indices,tuv):uv.data[li].uv=q
# Retain the original slab geometry and threshold, while its exposed 60 mm
# edge receives the same plain finish as the facade above it.
o=bpy.data.objects['SLAB_JOINED_F1_Geometry'];o.data=o.data.copy();me=o.data;finish=bpy.data.materials['M_Wall_Exterior'];j=len(me.materials);me.materials.append(finish)
for f in me.polygons:
 if abs(f.normal.z)<.6:f.material_index=j
changed.append(o.name)
views=[('Gable_East',(25,-20,6.8),(16.6,-13.2,3.15),46),('Gable_Detail',(22.4,-17.0,6.0),(18.6,-12.15,4.1),55),('Gable_West',(7.2,-19.0,8.3),(13.4,-12.4,3.4),48),('Kitchen_North',(16,2.2,6.0),(11.8,-3.1,3.4),52),('House_Foot',(-2.,7.8,1.),(0,7.8,.45),24),('House_Front',(20,-18,12.8),(6.8,2.,5.5),48),('Entry_Grade',(6.5,-3.,1.4),(6.5,1.2,0.),24),('Screen_Valley',(13.,-19.3,7.4),(10.30,-17.05,4.0),54),('Whole_Site',(28,-32,18),(5,-7,1.3),47)]
for n,pos,target,lens in views:
 name='V24_19_'+n;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.04;c.data.clip_end=300;added.append(name)
sc.camera=bpy.data.objects['V24_19_House_Front'];sc.frame_set(40);bpy.context.view_layer.update();sc['Version']='V24_19_PHOTO_TILED_GABLE_VERGES_CORRECTED_HOUSE_GRADE_NO_BRICK_SKIRT'
t=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');t.clear();t.write('V24.19：撤除被用户否定的V24.18整圈砖勒脚。原三层建筑不整体移动，楼层、门窗、楼梯和入口踏步保持原位置；修正V16假定地坪与首层零标高的脱接，墙边地坪拟合至-0.060m，向院内旧地面平缓衔接，入口台阶及其前方原标高保留。首层楼板几何不变，竖向薄边与既有白墙同饰面。储藏房和厨房为青砖封闭山墙、薄压边、实际外挑的筒板瓦檐，镬耳为窄直立折角头、短平顶、分层灰白边框。参考211108、211128、211336，瓦挑出墙约170至190mm。V24.18已完成的凹照壁、连续外墙贴图、10处假白柱移除、12扇外开窗及26扇原门动画保持。第1帧关窗、第20帧半开、第40帧全开。尺寸为照片与既有模型拟合，非新增实测标高。')
def write(n,a):(R/n).write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
write('V24_19_Changes.json',{'changed':sorted(set(changed)),'added':sorted(set(added)),'removed':removed});write('V24_19_Corrections.json',prep['proof']);write('V24_19_Gable_UV.json',{'route':route,'surfaces':uv_report});bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
write('V24_19_Build.json',{'source':src['model'],'source_sha256':src['sha256'],'model':str(P),'sha256':h});print('V19_SAVED',h,flush=True)
