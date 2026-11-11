import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_27';O=Path('E:/jz/JIA/Rebuild_V24_27');R=O/'Reports'
for p in [R,O/'Blender',O/'Roam']:p.mkdir(parents=True,exist_ok=True)
P=O/'Blender/Architecture_Complete_V24_27.blend';src=json.loads((D/'Source.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))}
bpy.ops.wm.open_mainfile(filepath=src['model']);sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();col=bpy.data.collections.new('V24_27_主屋院坪及外侧高差修正');sc.collection.children.link(col);changed=[];added=[]
for ma in bpy.data.materials:ma.use_fake_user=True
for a in bpy.data.actions:a.use_fake_user=True
for row in prep['raw_objects']:
 o=bpy.data.objects[row['name']];a=np.load(D/row['file']);old=o.data;me=bpy.data.meshes.new(o.name+'_V24_27');iv=o.matrix_world.inverted();me.from_pydata([iv@Vector(v)for v in a['v']],[],a['f'])
 for ma in old.materials:me.materials.append(ma)
 me.update();uv=me.uv_layers.new(name='Source_UV_Retained')
 for face,mi,tuv in zip(me.polygons,a['mi'],a['uv']):
  face.material_index=int(mi)
  if row['smooth_top']:face.use_smooth=face.normal.z>.3
  for li,q in zip(face.loop_indices,tuv):uv.data[li].uv=q
 o.data=me
 if not old.users:bpy.data.meshes.remove(old)
 o['V24_27_Reference']='2026-10-20 123610 / 123632; floor 0.00; one riser 0.15m';changed.append(o.name);print('APPLIED',o.name,len(me.polygons),flush=True)
# Refresh the existing invisible acceleration mesh from the revised model.
bad=['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','_TREES','_TREE_','TILE_ROWS','TILE_COURSES','_COPING','COVER_TILES','PAN_TILES','DRIP_ENDS','UNIFIED_PAN_BARREL','RIDGE_CAP','END_ORNAMENT','FLORAL','FRETWORK','STEPPED_FRAMES','MOULDED_FRAMES','REFERENCE_RELIEF','CARVED','BLINDS','_PLASTER_STEPPED_RELIEF','PERIMETER_EAVE_BANDS']
verts=[];faces=[];coll=[]
for o in list(bpy.data.objects):
 if o.type!='MESH'or o.hide_render or o.name.startswith('V24_21_'):continue
 if any(k in o.name.upper()for k in bad):continue
 if len(o.data.polygons)>80000 and o.name not in [r['name']for r in prep['raw_objects']] and not any(k in o.name.upper()for k in ['GROUND','SOIL','ROAD','TERRAIN','FACADE','PARTITION','SLAB','FOUNDATION']):continue
 me=o.data;me.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@v.co)for v in me.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles);coll.append({'name':o.name,'triangles':len(me.loop_triangles)})
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;me=bpy.data.meshes.new('V24_27_Navigation_Collision_Mesh');me.from_pydata(verts,[],faces);me.update();cache.data=me;changed.append(cache.name);cache['V24_27_Architecture_Updated']=True
if not old.users:bpy.data.meshes.remove(old)
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 (O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')

views=[('West_Exterior_Eye', (-5.5, 6.5, 1.13), (0.0, 5.7, 1.1), 24), ('West_Exterior_Grade', (-6.8, 2.3, 3.1), (-0.25, 5.7, -0.05), 28), ('House_Step_From_Kitchen', (8.8, -6.6, 1.13), (6.7, 0.3, -0.1), 30), ('House_Step_Close', (6.5, -2.3, 0.75), (6.5, -0.1, -0.08), 28), ('Courtyard_Grade_Overview', (5.9, -5.5, 7.5), (6.5, 0.1, -0.15), 30), ('Kitchen_Gutter_Grade', (6.0, -5.1, 1.13), (8.2, -2.7, -0.25), 30)]
for tag,loc,aim,lens in views:
 name='V24_27_'+tag;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=300;added.append(name)
for t in ['123610','123632']:
 im=bpy.data.images.load('D:/Desktop/屏幕截图 2026-10-20 '+t+'.jpg',check_existing=True);im.pack()
sc.camera=bpy.data.objects['V24_27_West_Exterior_Eye'];sc['Version']='V24_27_CORRECTED_HOUSE_COURTYARD_AND_WEST_EXTERIOR_LEVELS'
note=bpy.data.texts.new('V24_27_高差修正说明');note.write('以原一层楼面0.00为基准，近主屋院坪及墙脚接地为-0.15，保留现有一级150毫米台阶。主屋门前院坪按坡面衔接低院坪，厨房檐廊-0.40及原排水边带保留。主屋西侧旧1.65米鼓起坡面改为约5.875米顺坡，近墙-0.15、外侧约-0.504，原地形范围和远处道路、排水沟、实景扫描不变。楼板、门柱、门窗、厨房屋面、内院墙瓦顶及L/P测量程序均保留。高差根据既有模型楼板及实景关系拟合，非新增现场实测。')
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
write('V24_27_Changes.json',{'changed':sorted(set(changed)),'added':added,'removed':[]});write('V24_27_Corrections.json',prep['proof']);write('V24_27_Collision_Index.json',{'objects':coll,'triangles':len(faces),'vertices':len(verts),'frame':40})
(D/'Views.json').write_text(json.dumps(views,ensure_ascii=False),encoding='utf8')
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
write('V24_27_Build.json',{'source':src['model'],'source_sha256':src['sha256'],'model':str(P),'sha256':h});print('V27_SAVED',h,flush=True)
