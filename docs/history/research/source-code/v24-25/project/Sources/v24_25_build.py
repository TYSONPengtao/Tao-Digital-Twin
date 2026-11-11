import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));D=W/'v24_25';O=Path('E:/jz/JIA/Rebuild_V24_25');R=O/'Reports'
for p in [R,O/'Blender',O/'Roam']:p.mkdir(parents=True,exist_ok=True)
P=O/'Blender/Architecture_Complete_V24_25.blend';src=json.loads((D/'Source.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text(encoding='utf8'))}
bpy.ops.wm.open_mainfile(filepath=src['model']);sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();col=bpy.data.collections.new('V24_25_高窗无缝门墙屋面铺装及测量');sc.collection.children.link(col);changed=[];added=[];removed=[]
for ma in bpy.data.materials:ma.use_fake_user=True
for a in bpy.data.actions:a.use_fake_user=True
def uv_metres(o):
 me=o.data;uv=me.uv_layers.new(name='V24_25_Metres')
 for f in me.polygons:
  pts=np.array([o.matrix_world@me.vertices[j].co for j in f.vertices]);normal=o.matrix_world.to_3x3()@f.normal;coords=pts[:,[1,2]]if abs(normal.x)>abs(normal.y)else pts[:,[0,2]]
  if abs(normal.z)>.65:coords=pts[:,:2]
  for li,q in zip(f.loop_indices,coords):uv.data[li].uv=q
def transfer(o,names):
 vs=[];fs=[];mis=[];uvs=[]
 for name in names:
  d=np.load(D/idx[name]['file']);k=sum(len(v)for v in vs);vs.append(d['v']);fs.append(d['f']+k);mmap=[]
  for mn in idx[name]['materials']:
   i=o.data.materials.find(mn)
   if i<0:i=len(o.data.materials);o.data.materials.append(bpy.data.materials[mn])
   mmap.append(i)
  mis.append(np.array(mmap)[d['mi']]);uvs.append(d['uv'])
 v=np.concatenate(vs);f=np.concatenate(fs);mi=np.concatenate(mis);qvs=np.concatenate(uvs);t=v[f];tr=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True);uv=o.data.uv_layers.new(name='Source_Affine_Metre_UV')
 for face in o.data.polygons:
  pts=np.array([o.matrix_world@o.data.vertices[i].co for i in face.vertices]);j=tr.find_nearest(Vector(pts.mean(0)))[2];face.material_index=int(mi[j]);p=t[j];bc=np.linalg.lstsq(np.c_[p[1]-p[0],p[2]-p[0]],(pts-p[0]).T,rcond=None)[0].T;q=qvs[j];coords=q[0]+bc[:,0,None]*(q[1]-q[0])+bc[:,1,None]*(q[2]-q[0])
  for li,q in zip(face.loop_indices,coords):uv.data[li].uv=q
for n in prep['remove']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True);removed.append(n)
for row in prep['objects']:
 n=row['name'];me=bpy.data.meshes.new(n+'_V24_25')
 if row['new']:
  me.from_pydata(row['v'],[],row['f']);o=bpy.data.objects.new(n,me);col.objects.link(o);added.append(n)
 else:
  o=bpy.data.objects[n];iv=o.matrix_world.inverted();me.from_pydata([iv@Vector(p)for p in row['v']],[],row['f']);old=o.data
  for ma in old.materials:me.materials.append(ma)
  o.data=me;changed.append(n)
  if not old.users:bpy.data.meshes.remove(old)
 me.update()
 if row.get('transfer'):transfer(o,row.get('transfer_sources',[n]))
 else:me.materials.clear();me.materials.append(bpy.data.materials[row['material']]);uv_metres(o)
 if row.get('joint_brick_finish'):
  brick=me.materials.find('M_V24_18_Continuous_Blue_Brick')
  for face in me.polygons:
   c=o.matrix_world@face.center;no=o.matrix_world.to_3x3()@face.normal
   if 8.249<c.x<9.55 and abs(c.y+11.73)<.00005 and no.y<-.5:face.material_index=brick
 if row.get('window_panes'):
  mn='M_Glass_Frosted'
  if me.materials.find(mn)<0:me.materials.append(bpy.data.materials[mn])
  for face in me.polygons:
   c=o.matrix_world@face.center
   if abs(c.x-row['window_x'])<.0061 and any(a-1e-5<c.y<b+1e-5 and z0-1e-5<c.z<z1+1e-5 for a,b,z0,z1 in row['window_panes']):face.material_index=me.materials.find(mn)
  parent=o.parent
  if parent:
   params=json.loads(parent.get('Parameters','{}'));params['origin'][2]=min(p[2]for p in row['window_panes'])-.047;params.update(definition='WINDOW_W1200_H800_HIGH_FROSTED_TWO_VERTICAL_LIGHTS',sill_above_floor_m=1.8,height_m=.8,dimension_confidence='PHOTO_FITTED_HIGH_WINDOW');parent['Parameters']=json.dumps(params,ensure_ascii=False);changed.append(parent.name)
 o['V24_25_Reference']='151458 / 151716 / 175749 / 175946 / 180153 / 180416';print('APPLIED',n,len(me.polygons),flush=True)
# Rebuild only the invisible navigation accelerator from the actual edited model.
bad=['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','_TREES','_TREE_','TILE_ROWS','TILE_COURSES','_COPING','COVER_TILES','PAN_TILES','DRIP_ENDS','UNIFIED_PAN_BARREL','RIDGE_CAP','END_ORNAMENT','FLORAL','FRETWORK','STEPPED_FRAMES','MOULDED_FRAMES','REFERENCE_RELIEF','CARVED','BLINDS','_PLASTER_STEPPED_RELIEF','PERIMETER_EAVE_BANDS']
verts=[];faces=[];coll=[]
for o in list(bpy.data.objects):
 if o.type!='MESH'or o.hide_render or o.name.startswith('V24_21_'):continue
 if any(k in o.name.upper()for k in bad):continue
 if len(o.data.polygons)>80000 and not any(k in o.name.upper()for k in ['GROUND','SOIL','ROAD','TERRAIN','FACADE','PARTITION','SLAB','FOUNDATION']):continue
 me=o.data;me.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@v.co)for v in me.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles);coll.append({'name':o.name,'triangles':len(me.loop_triangles)})
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;me=bpy.data.meshes.new('V24_25_Navigation_Collision_Mesh');me.from_pydata(verts,[],faces);me.update();cache.data=me;changed.append(cache.name);cache['V24_25_Architecture_Updated']=True
if not old.users:bpy.data.meshes.remove(old)
for txt,fn in [('V24_25_测量工具.py','v24_25_measure_tools.py'),('V24_21_漫游控制器.py','v24_25_roam_controller.py'),('V24_21_启动漫游.py','v24_25_start_roam.py')]:
 text=bpy.data.texts.get(txt)or bpy.data.texts.new(txt);text.clear();text.write((W/fn).read_text('utf8'))
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 (O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')
sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1.;sc.unit_settings.length_unit='METERS';sc['V24_25_Measurements_JSON']='[]'

views=[('WC_Right_F1', (11.45, 8.5, 1.53), (13.0, 8.55, 2.25), 25), ('WC_Left_F2', (1.55, 8.5, 5.43), (0.0, 8.55, 6.1), 25), ('Gate_Contact', (9.7, -14.2, 1.13), (8.2, -11.65, 1.65), 29), ('Gate_Eave', (10.0, -15.0, 4.9), (8.6, -11.65, 2.8), 35), ('Storage_Entrance', (11.7, -14.95, 2.6), (13.35, -12.5, -0.35), 24), ('Storage_Approach', (12.4, -13.3, 1.3), (13.1, -15.6, -0.4), 22), ('Kitchen_Roof', (3.0, -6.8, 10.2), (11.1, -7.2, 3.3), 32), ('Roof_Valley', (15.8, -18.0, 11.0), (12.7, -11.3, 3.6), 34)]
for tag,loc,aim,lens in views:
 name='V24_25_'+tag;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=300;added.append(name)
for fn in ['D:/Desktop/屏幕截图 2026-10-19 '+t+'.jpg'for t in ['151458','151716','175749','175827','175910','175946','180153','180416']]:
 im=bpy.data.images.load(fn,check_existing=True);im.pack()
sc.camera=bpy.data.objects['V24_25_Kitchen_Roof'];sc['Version']='V24_25_HIGH_WC_WINDOWS_CLOSED_GATE_JOINT_ORDERED_ROOF_AND_MEASUREMENTS'
note=bpy.data.texts.new('V24_25_本次修正说明');note.write('五扇房内卫生间窗改1.8米高窗台、0.8米高磨砂双竖格窗，取消中横档并重切墙洞和窗台。内大门雕花柱后与厨房墙封紧接到檐底，去掉上版前侧平板。厨房瓦面修正为两片平直屋面并统一瓦片起排，保留屋脊镬耳与两房交谷。储藏房入口、过渡地带及檐廊统一现有浅灰地面材质。漫游顶栏新增测长度L、测面积P、撤销及CSV导出；点选模型表面，按Ctrl可吸附顶点，面积Enter完成，Esc回漫游。测量依当前模型米制尺寸；窗位和屋面为照片拟合。')

def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
write('V24_25_Changes.json',{'changed':sorted(set(changed)),'added':added,'removed':removed});write('V24_25_Corrections.json',prep['proof']);write('V24_25_Collision_Index.json',{'objects':coll,'triangles':len(faces),'vertices':len(verts),'frame':40})
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
write('V24_25_Build.json',{'source':src['model'],'source_sha256':src['sha256'],'model':str(P),'sha256':h});print('V23_SAVED',h,flush=True)
