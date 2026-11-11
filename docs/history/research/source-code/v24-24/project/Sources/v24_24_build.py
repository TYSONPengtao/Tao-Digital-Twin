import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));D=W/'v24_24';O=Path('E:/jz/JIA/Rebuild_V24_24');R=O/'Reports'
for p in [R,O/'Blender',O/'Roam']:p.mkdir(parents=True,exist_ok=True)
P=O/'Blender/Architecture_Complete_V24_24.blend';src=json.loads((D/'Source.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text(encoding='utf8'))}
bpy.ops.wm.open_mainfile(filepath=src['model']);sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();col=bpy.data.collections.new('V24_24_端部封墙门前退墙及院落补铺');sc.collection.children.link(col);changed=[];added=[];removed=[]
for ma in bpy.data.materials:ma.use_fake_user=True
for a in bpy.data.actions:a.use_fake_user=True
def uv_metres(o):
 me=o.data;uv=me.uv_layers.new(name='V24_24_Metres')
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
 n=row['name'];me=bpy.data.meshes.new(n+'_V24_24')
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
 if row.get('wall_finish'):
  white=me.materials.find('M_V24_11_Plain_White_Limewash');brick=me.materials.find('M_V24_18_Continuous_Blue_Brick')
  for face in me.polygons:
   c=o.matrix_world@face.center;no=o.matrix_world.to_3x3()@face.normal
   if (9.42<c.x<9.44 and c.y>-3.57 and no.x<-.5):face.material_index=white
   if c.y<-11.93 and no.y<-.5:face.material_index=brick
   if 13.19<c.x<13.22 and c.y<-11.62 and no.x<-.5:face.material_index=brick
 if row.get('gate_front_finish'):
  brick=me.materials.find('M_V24_18_Continuous_Blue_Brick')
  for face in me.polygons:
   c=o.matrix_world@face.center;no=o.matrix_world.to_3x3()@face.normal
   if 8.339<c.x<13.206 and abs(c.y+11.73)<.00005 and no.y<-.5:face.material_index=brick
 if row.get('paving_finish'):
  for mn in ['M_V22_Courtyard_Filled_Joint']+['M_V22_Courtyard_Stone_'+str(i)for i in range(4)]:
   if me.materials.find(mn)<0:me.materials.append(bpy.data.materials[mn])
  for face in me.polygons:
   c=o.matrix_world@face.center;iy=int(np.floor((c.y+10.9)/.62));offset=.4-(.56 if iy%2 else 0);ix=int(np.floor((c.x-offset)/1.12));xx=c.x-offset-ix*1.12;yy=c.y+10.9-iy*.62
   mn='M_V22_Courtyard_Stone_'+str((ix+iy*3)%4)if .003-1e-6<xx<1.117+1e-6 and .003-1e-6<yy<.617+1e-6 else'M_V22_Courtyard_Filled_Joint';face.material_index=me.materials.find(mn)
 o['V24_24_Reference']='150017 / 150243 / 150306 / 150819';print('APPLIED',n,len(me.polygons),flush=True)
# Rebuild only the invisible navigation accelerator from the actual edited model.
bad=['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','_TREES','_TREE_','TILE_ROWS','TILE_COURSES','_COPING','COVER_TILES','PAN_TILES','DRIP_ENDS','UNIFIED_PAN_BARREL','RIDGE_CAP','END_ORNAMENT','FLORAL','FRETWORK','STEPPED_FRAMES','MOULDED_FRAMES','REFERENCE_RELIEF','CARVED','BLINDS','_PLASTER_STEPPED_RELIEF','PERIMETER_EAVE_BANDS']
verts=[];faces=[];coll=[]
for o in list(bpy.data.objects):
 if o.type!='MESH'or o.hide_render or o.name.startswith('V24_21_'):continue
 if any(k in o.name.upper()for k in bad):continue
 if len(o.data.polygons)>80000 and not any(k in o.name.upper()for k in ['GROUND','SOIL','ROAD','TERRAIN','FACADE','PARTITION','SLAB','FOUNDATION']):continue
 me=o.data;me.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@v.co)for v in me.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles);coll.append({'name':o.name,'triangles':len(me.loop_triangles)})
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;me=bpy.data.meshes.new('V24_24_Navigation_Collision_Mesh');me.from_pydata(verts,[],faces);me.update();cache.data=me;changed.append(cache.name);cache['V24_24_Architecture_Updated']=True
if not old.users:bpy.data.meshes.remove(old)
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py')]:
 (O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')
views=[('Kitchen_Closure', (8.85, -7.0, 1.13), (8.91, -3.0, 1.3), 28), ('Gate_Front', (6.6, -15.8, 1.13), (6.6, -11.6, 1.3), 25), ('Gate_Junction_High', (10.0, -15.0, 4.9), (8.6, -11.65, 2.8), 35), ('Gate_Back', (8.9, -8.6, 1.13), (8.25, -11.65, 1.45), 25), ('Paving_Overview', (6.4, -7.4, 9.2), (6.4, -0.2, -0.35), 25), ('Paving_Close', (5.6, -2.2, 1.9), (6.6, -0.55, -0.25), 24)]
for tag,loc,aim,lens in views:
 name='V24_24_'+tag;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=300;added.append(name)
for fn in ['D:/Desktop/屏幕截图 2026-10-19 '+t+'.jpg'for t in ['150017','150243','150306','150819']]:
 im=bpy.data.images.load(fn,check_existing=True);im.pack()
sc.camera=bpy.data.objects['V24_24_Kitchen_Closure'];sc['Version']='V24_24_VERANDA_CLOSURE_FRONT_GATE_SETBACK_AND_MATCHING_PAVING'
note=bpy.data.texts.new('V24_24_本次修正说明');note.write('按150017将厨房北端木柱与木立面间的红框封白墙，墙顶随现有斜梁，保留木柱外露。按150243和150306，只把内大门正面砖墙退到现有白墙Y=-11.73面，门后、雕花柱和门楼屋顶保持。按150819将主楼前黄线范围补同款1.12×0.62米错缝石板，沿原坡面贴合，表面加高2毫米；原台阶、地坪基体和排水坡向保留。保留储藏房上版修正及1.65米人物漫游。')
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
write('V24_24_Changes.json',{'changed':sorted(set(changed)),'added':added,'removed':removed});write('V24_24_Corrections.json',prep['proof']);write('V24_24_Collision_Index.json',{'objects':coll,'triangles':len(faces),'vertices':len(verts),'frame':40})
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
write('V24_24_Build.json',{'source':src['model'],'source_sha256':src['sha256'],'model':str(P),'sha256':h});print('V23_SAVED',h,flush=True)
