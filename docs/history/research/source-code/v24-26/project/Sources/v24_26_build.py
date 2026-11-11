import bpy,sys,json,hashlib,numpy as np,shutil
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;D=W/'v24_26';O=Path('E:/jz/JIA/Rebuild_V24_26');R=O/'Reports'
for p in [R,O/'Blender',O/'Roam']:p.mkdir(parents=True,exist_ok=True)
P=O/'Blender/Architecture_Complete_V24_26.blend';src=json.loads((D/'Source.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))}
bpy.ops.wm.open_mainfile(filepath=src['model']);sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();col=bpy.data.collections.new('V24_26_青砖封墙短出檐厚实院墙瓦顶');sc.collection.children.link(col);changed=[];added=[]
for ma in bpy.data.materials:ma.use_fake_user=True
for a in bpy.data.actions:a.use_fake_user=True

def uv_metres(o):
 me=o.data;uv=me.uv_layers.new(name='V24_26_Metres')
 for f in me.polygons:
  pts=np.array([o.matrix_world@me.vertices[j].co for j in f.vertices]);normal=o.matrix_world.to_3x3()@f.normal;coords=pts[:,[1,2]]if abs(normal.x)>abs(normal.y)else pts[:,[0,2]]
  if abs(normal.z)>.65:coords=pts[:,:2]
  for li,q in zip(f.loop_indices,coords):uv.data[li].uv=q

def transfer(o,name):
 d=np.load(D/idx[name]['file']);v=d['v'];f=d['f'];t=v[f];mi=d['mi'];qvs=d['uv'];tr=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True);uv=o.data.uv_layers.new(name='Source_Affine_Metre_UV')
 for face in o.data.polygons:
  pts=np.array([o.matrix_world@o.data.vertices[i].co for i in face.vertices]);j=tr.find_nearest(Vector(pts.mean(0)))[2];face.material_index=int(mi[j]);p=t[j];bc=np.linalg.lstsq(np.c_[p[1]-p[0],p[2]-p[0]],(pts-p[0]).T,rcond=None)[0].T;q=qvs[j];coords=q[0]+bc[:,0,None]*(q[1]-q[0])+bc[:,1,None]*(q[2]-q[0])
  for li,q in zip(face.loop_indices,coords):uv.data[li].uv=q

for row in prep['objects']:
 n=row['name'];o=bpy.data.objects[n];iv=o.matrix_world.inverted();me=bpy.data.meshes.new(n+'_V24_26');me.from_pydata([iv@Vector(p)for p in row['v']],[],row['f']);old=o.data
 for ma in old.materials:me.materials.append(ma)
 o.data=me;me.update();changed.append(n)
 if row.get('transfer'):transfer(o,n)
 else:me.materials.clear();me.materials.append(bpy.data.materials[row['material']]);uv_metres(o)
 if not old.users:bpy.data.meshes.remove(old)
 o['V24_26_Reference']='210606 / 210832 / DJI_0095 / 211022 / 211048';print('APPLIED',n,len(me.polygons),flush=True)
for row in prep['recolor']:
 o=bpy.data.objects[row['name']];old=o.data;o.data=old.copy();o.data.materials.clear();o.data.materials.append(bpy.data.materials[row['material']])
 for f in o.data.polygons:f.material_index=0
 if not old.users:bpy.data.meshes.remove(old)
 o['V24_26_Reference']='210452';changed.append(o.name)

# The exposed narrow return beside the closure is part of the older connected
# masonry, and must share the same brick finish as the new closure face.
o=bpy.data.objects['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'];old=o.data;o.data=old.copy();brick=o.data.materials.find('M_V24_18_Continuous_Blue_Brick');return_faces=[]
for f in o.data.polygons:
 c=o.matrix_world@f.center;n=o.matrix_world.to_3x3()@f.normal
 if abs(c.x-9.43)<.00004 and -3.0<c.y<-2.5 and n.x<-.8:
  f.material_index=brick;return_faces.append(f.index)
if not old.users:bpy.data.meshes.remove(old)
changed.append(o.name);prep['proof']['brick_closure']['adjacent_masonry_return_face_count']=len(return_faces)

# Refresh the existing invisible acceleration mesh from the revised model.
bad=['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','_TREES','_TREE_','TILE_ROWS','TILE_COURSES','_COPING','COVER_TILES','PAN_TILES','DRIP_ENDS','UNIFIED_PAN_BARREL','RIDGE_CAP','END_ORNAMENT','FLORAL','FRETWORK','STEPPED_FRAMES','MOULDED_FRAMES','REFERENCE_RELIEF','CARVED','BLINDS','_PLASTER_STEPPED_RELIEF','PERIMETER_EAVE_BANDS']
verts=[];faces=[];coll=[]
for o in list(bpy.data.objects):
 if o.type!='MESH'or o.hide_render or o.name.startswith('V24_21_'):continue
 if any(k in o.name.upper()for k in bad):continue
 if len(o.data.polygons)>80000 and not any(k in o.name.upper()for k in ['GROUND','SOIL','ROAD','TERRAIN','FACADE','PARTITION','SLAB','FOUNDATION']):continue
 me=o.data;me.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@v.co)for v in me.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles);coll.append({'name':o.name,'triangles':len(me.loop_triangles)})
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;me=bpy.data.meshes.new('V24_26_Navigation_Collision_Mesh');me.from_pydata(verts,[],faces);me.update();cache.data=me;changed.append(cache.name);cache['V24_26_Architecture_Updated']=True
if not old.users:bpy.data.meshes.remove(old)
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 (O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')

views=[('Brick_Closure_Outside',(5.7,.8,1.25),(8.9,-3.,1.3),36),('Brick_Closure_Porch',(8.85,-7.,1.13),(8.91,-3.,1.4),28),('Kitchen_Short_Verge',(9.8,-16.5,1.15),(12.6,-11.73,3.2),24),('Kitchen_Verge_High',(10.,-17.5,8.7),(12.,-11.4,3.5),34),('Courtyard_Wall_Eye',(.5,-14.7,1.15),(2.2,-11.582,1.9),26),('Courtyard_Tiles_Close',(2.,-14.5,2.45),(2.,-11.582,2.38),45),('Courtyard_Mitre',(-2.5,-14.2,3.4),(.1,-11.4,2.4),45),('Kitchen_Roof',(3.,-6.8,10.2),(11.1,-7.2,3.3),32)]
for tag,loc,aim,lens in views:
 name='V24_26_'+tag;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=300;added.append(name)
for fn in ['D:/Desktop/屏幕截图 2026-10-19 '+t+'.jpg'for t in ['210452','210606','210832','211022','211048']]+['D:/DJI/0002/DCIM/101MEDIA/DJI_0095.JPG']:
 im=bpy.data.images.load(fn,check_existing=True);im.pack()
sc.camera=bpy.data.objects['V24_26_Courtyard_Wall_Eye'];sc['Version']='V24_26_BLUE_BRICK_CLOSURE_SHORT_KITCHEN_VERGE_AND_SUBSTANTIAL_COURTYARD_TILED_COPING'
note=bpy.data.texts.new('V24_26_本次修正说明');note.write('厨房北端封墙改为与相邻墙一致的青砖材质。厨房靠储藏房南端瓦面出檐由约0.40米收至约0.12米，山墙灰边和镬耳相应收进；厨房原坡度、瓦列、储藏房屋面不变。内院L形墙瓦顶加宽至约0.90米，瓦下垫层约65毫米，双排搭接筒瓦板瓦、花纹滴水瓦当、花朵与菱形真镂空花脊、圆脊帽；保留原墙体与长短框饰，转角同一45度斜接。新增尺寸依据照片比例拟合。V24.25高窗、门墙封缝、浅灰铺装、门窗动作、1.65米漫游与L/P测量功能保留。')

def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
write('V24_26_Changes.json',{'changed':sorted(set(changed)),'added':added,'removed':[]});write('V24_26_Corrections.json',prep['proof']);write('V24_26_Collision_Index.json',{'objects':coll,'triangles':len(faces),'vertices':len(verts),'frame':40})
(D/'Views.json').write_text(json.dumps(views,ensure_ascii=False),encoding='utf8')
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
write('V24_26_Build.json',{'source':src['model'],'source_sha256':src['sha256'],'model':str(P),'sha256':h});print('V26_SAVED',h,flush=True)
