import bpy,sys,json,hashlib,shutil,math,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_33';O=Path('E:/jz/JIA/Rebuild_V24_33');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_33.blend';SOURCE=Path('E:/jz/JIA/Rebuild_V24_32/Blender/Architecture_Complete_V24_32.blend')
for p in [R,O/'Blender',O/'Roam',O/'References']:p.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));sc=bpy.context.scene;before=snapshot(bpy);(D/'Before_Snapshot.json').write_text(json.dumps(before,ensure_ascii=False),encoding='utf8');(D/'Source.json').write_text(json.dumps({'model':str(SOURCE),'sha256':sha(SOURCE)}),encoding='utf8');sc.frame_set(40);bpy.context.view_layer.update()
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));col=bpy.data.collections.new('V24_33_楼面接缝露台厨房与南侧围墙修正');sc.collection.children.link(col);changed=[];added=[];removed=[]
for n in prep['remove']:
 o=bpy.data.objects.get(n)
 if o:removed.append(n);bpy.data.objects.remove(o,do_unlink=True)
for row in prep['raw_objects']:
 n=row['name'];a=np.load(D/row['file']);o=bpy.data.objects[n];old=o.data;field=None;tr=None;values=None
 if row.get('preserve_height_attribute'):
  attr=old.attributes.get('V24_20_Height_Above_Finish_Division');old.calc_loop_triangles();vv=[o.matrix_world@v.co for v in old.vertices];ff=[t.vertices[:] for t in old.loop_triangles];tr=BVHTree.FromPolygons(vv,ff,all_triangles=True);values=np.array([p.value for p in attr.data]);field=[]
  for p in a['v']:
   q,no,j,dd=tr.find_nearest(Vector(p));ids=list(ff[j]);pts=np.array([vv[k] for k in ids]);A=np.c_[pts[1]-pts[0],pts[2]-pts[0]];bc=np.linalg.lstsq(A,np.array(q)-pts[0],rcond=None)[0];val=values[ids];field.append(float(val[0]+bc[0]*(val[1]-val[0])+bc[1]*(val[2]-val[0])))
 me=bpy.data.meshes.new(n+'_V24_33');iv=o.matrix_world.inverted();me.from_pydata([iv@Vector(p) for p in a['v']],[],a['f']);o.data=me
 for name in row['materials']:me.materials.append(bpy.data.materials[name])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));me.update();layer=me.uv_layers.new(name='V24_33_Source_Continuous_Metre_UV');layer.active_render=True
 for face,tex in zip(me.polygons,a['uv']):
  for k,t in zip(face.loop_indices,tex):layer.data[k].uv=t
 if field is not None:att=me.attributes.new('V24_20_Height_Above_Finish_Division','FLOAT','POINT');att.data.foreach_set('value',np.array(field,dtype=np.float32))
 o['V24_33_Repair_Source']=row['file'];changed.append(n)
# Rebuild the navigation collision source so no deleted overlay or timber
# fragment survives in the roam physics cache.
bad=['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','_TREES','_TREE_','TILE_ROWS','TILE_COURSES','_COPING','COVER_TILES','PAN_TILES','DRIP_ENDS','UNIFIED_PAN_BARREL','RIDGE_CAP','END_ORNAMENT','FLORAL','FRETWORK','STEPPED_FRAMES','MOULDED_FRAMES','REFERENCE_RELIEF','CARVED','BLINDS','_PLASTER_STEPPED_RELIEF','PERIMETER_EAVE_BANDS'];verts=[];faces=[];coll=[]
for o in list(bpy.data.objects):
 if o.type!='MESH' or o.hide_render or o.name.startswith('V24_21_') or any(k in o.name.upper() for k in bad):continue
 if len(o.data.polygons)>80000 and o.name not in changed and not any(k in o.name.upper() for k in ['GROUND','SOIL','ROAD','TERRAIN','FACADE','PARTITION','SLAB','FOUNDATION']):continue
 me=o.data;me.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@q.co) for q in me.vertices);faces.extend(tuple(k+i for i in t.vertices) for t in me.loop_triangles);coll.append({'name':o.name,'triangles':len(me.loop_triangles)})
cache=bpy.data.objects['V24_21_Navigation_Collision'];me=bpy.data.meshes.new('V24_33_Navigation_Collision');me.from_pydata(verts,[],faces);me.update();cache.data=me;changed.append(cache.name)
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:(O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')
views=[('01_Landing_Threshold',(8.5,6.3,4.95),(8.5,8.6,3.85),24),('02_Terrace_Flush_Floor',(1.7,7.,8.55),(1.7,2.,7.7),20),('03_Stair_Flat_Wall',(4.5,8.,6.1),(6.,7.3,6.75),20),('04_F3_Well_Edge',(8.7,8.8,8.6),(5.7,6.7,7.7),20),('05_Kitchen_Clean_Brick',(7.8,-1.8,1.25),(8.9,-2.95,1.5),20),('06_Storage_Flush_Passage',(12.3,-15.,1.05),(13.1,-16.4,-.05),22),('07_F3_Opposite_Door',(8.45,7.,8.5),(8.45,5.5,8.4),26),('08_South_Continuous_Blue_Brick',(12.7,-14.6,1.25),(13.,-16.5,1.),22),('09_Exterior', (23.,-2.,11.),(12.,6.,4.7),28),('10_Whole_Site',(-16.,-28.,22.),(0.,-2.,.7),30)]
for tag,pos,aim,lens in views:
 c=bpy.data.objects.new('V24_33_'+tag,bpy.data.cameras.new('V24_33_'+tag));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=300;added.append(c.name)
for t in ['042455','042534','003911','042615','042705','042738','025023','042922']:
 p=Path('D:/Desktop/屏幕截图 2026-10-21 '+t+'.jpg')
 if p.exists():im=bpy.data.images.load(str(p),check_existing=True);im.pack();shutil.copy2(p,O/'References'/p.name)
for name in ['启动漫游.cmd','打开修正版模型.cmd']:(O/name).write_text((SOURCE.parents[1]/name).read_text('utf8').replace('V24_32','V24_33'),encoding='utf8')
note=bpy.data.texts.new('V24_33_截图逐项修正说明');note.write('042455/042615：把下层楼梯口墙体占据的楼板带归并到真实楼板，统一灰色楼面，保持原楼层标高和楼梯空洞。042534：删除叠加找坡板，露台使用原灰色楼板；裁掉穿进露台的前门廊屋面小角。003911：复核上一版已收平的楼梯墙横带。042705：删除厨房北端穿出砖墙的旧立柱延续段和柱头，收回三条饰条末端；完整屋檐和门廊柱保留。042738：删除旧门槛叠板，将廊下高出6毫米的地面并入连续灰色通道。025023：保留已换到对侧铰链并向室内打开的三楼门，不重复翻转，检查1/20/40帧。042922：删除南侧青砖墙段错误白色覆盖层，恢复原青砖照片贴图；删除打叉的单根石栏端柱，邻接栏板与白色装饰顶带保留。全部修复基于已有模型和标注；未改变原外轮廓登记线和楼梯踏步尺寸。')
sc.frame_set(40);bpy.context.view_layer.update();sc.camera=bpy.data.objects['V24_33_09_Exterior'];sc['Version']='V24_33_CONTINUOUS_FLOORS_CLEAN_KITCHEN_AND_SOUTH_BRICK_WALL'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
write('V24_33_Changes.json',{'changed':sorted(set(changed)),'added':added,'removed':removed,'geometry':prep['raw_objects'],'proof':prep['proof'],'source':str(SOURCE),'door_unchanged_from_correct_opposite_hinge_V32':True});write('V24_33_Collision_Index.json',{'objects':coll,'vertices':len(verts),'triangles':len(faces),'frame':40});(D/'Views.json').write_text(json.dumps(views,ensure_ascii=False),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_33_Build.json',{'source':str(SOURCE),'source_sha256':sha(SOURCE),'model':str(P),'sha256':sha(P)});print('V33_SAVED',sha(P),flush=True)
