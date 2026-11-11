import bpy,sys,json,hashlib,shutil,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_30';O=Path('E:/jz/JIA/Rebuild_V24_30');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_30.blend';SOURCE=Path('E:/jz/JIA/Rebuild_V24_29/Blender/Architecture_Complete_V24_29.blend')
for p in [R,O/'Blender',O/'Roam',O/'References']:p.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));sc=bpy.context.scene
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8');(D/'Source.json').write_text(json.dumps({'model':str(SOURCE),'sha256':sha(SOURCE)}),encoding='utf8')
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));col=bpy.data.collections.new('V24_30_院坪铺装外院白色建模场地与等厚墙');sc.collection.children.link(col);changed=[];added=[];removed=[]
m=bpy.data.materials.new('M_V24_30_White_Building_Pad');m.use_nodes=True;node=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');node.inputs['Base Color'].default_value=(.92,.92,.92,1);node.inputs['Roughness'].default_value=.88;m.diffuse_color=(.92,.92,.92,1)
for n in prep['remove']:
 o=bpy.data.objects.get(n)
 if o:removed.append(n);bpy.data.objects.remove(o,do_unlink=True)
for row in prep['raw_objects']:
 n=row['name'];a=np.load(D/row['file']);o=bpy.data.objects.get(n)
 if o is None:o=bpy.data.objects.new(n,bpy.data.meshes.new(n+'_Initial'));col.objects.link(o);added.append(n)
 else:changed.append(n)
 old=o.data;me=bpy.data.meshes.new(n+'_V24_30');iv=o.matrix_world.inverted();me.from_pydata([iv@Vector(p)for p in a['v']],[],a['f']);o.data=me
 for name in row['materials']:me.materials.append(bpy.data.materials[name])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));me.update();layer=me.uv_layers.new(name='Model_World_Affine_UV')
 for face,tex in zip(me.polygons,a['uv']):
  for k,t in zip(face.loop_indices,tex):layer.data[k].uv=t
 o['V24_30_Source_Geometry']=row['file']
 if n=='V24_30_Outer_Yard_White_Building_Pad':o['Purpose']='Flat white outer yard for future editable buildings';o['Top_Z_m']=-.6;o['Top_Area_m2']=prep['proof']['outer_pad']['area_m2']
for row in prep['offsets']:
 o=bpy.data.objects.get(row['name'])
 if o:o.location+=Vector(row['offset']);changed.append(o.name)
bpy.context.view_layer.update()
# Same human scale, stair and door runtime; update the collision representation.
bad=['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','_TREES','_TREE_','TILE_ROWS','TILE_COURSES','_COPING','COVER_TILES','PAN_TILES','DRIP_ENDS','UNIFIED_PAN_BARREL','RIDGE_CAP','END_ORNAMENT','FLORAL','FRETWORK','STEPPED_FRAMES','MOULDED_FRAMES','REFERENCE_RELIEF','CARVED','BLINDS','_PLASTER_STEPPED_RELIEF','PERIMETER_EAVE_BANDS']
verts=[];faces=[];coll=[]
for o in list(bpy.data.objects):
 if o.type!='MESH'or o.hide_render or o.name.startswith('V24_21_'):continue
 if any(k in o.name.upper()for k in bad):continue
 if len(o.data.polygons)>80000 and o.name not in changed and not any(k in o.name.upper()for k in ['GROUND','SOIL','ROAD','TERRAIN','FACADE','PARTITION','SLAB','FOUNDATION']):continue
 me=o.data;me.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@q.co)for q in me.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles);coll.append({'name':o.name,'triangles':len(me.loop_triangles)})
cache=bpy.data.objects['V24_21_Navigation_Collision'];me=bpy.data.meshes.new('V24_30_Navigation_Collision');me.from_pydata(verts,[],faces);me.update();cache.data=me;changed.append(cache.name)
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 (O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')
views=[('Courtyard_Finish',(5.2,-9.0,6.2),(5.4,-5.5,-.6),27),('Entry_And_High_Lane',(5.6,-4.2,.9),(8.3,-.6,-.1),24),('Inner_Overview',(5.8,-7.4,14.),(6.5,-4.5,-.4),26),('Outer_Gate_Curb',(-16.5,-12.0,1.15),(-4.,-3.5,-.1),24),('Outer_White_Pad',(-13.,-1.0,23.),(-10.,-.5,-.6),30),('Rear_Separation',(-3.5,11.0,5.5),(.8,10.9,.3),26),('Wall_Thickness',(20.,5.,18.),(14.8,4.5,1.2),35),('Whole_Site',(-16.,-28.,22.),(0.,-2.,.7),30),('White_Wall',(9.8,-.4,1.1),(14.,-2.3,1.4),27)]
for tag,loc,aim,lens in views:
 c=bpy.data.objects.new('V24_30_'+tag,bpy.data.cameras.new('V24_30_'+tag));col.objects.link(c);c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=300;added.append(c.name)
for t in ['200800','201009','201723','201633','201940','202115','201=8115']:
 p=Path('D:/Desktop/屏幕截图 2026-10-20 '+t+'.jpg')
 if p.exists():im=bpy.data.images.load(str(p),check_existing=True);im.pack();shutil.copy2(p,O/'References'/p.name)
note=bpy.data.texts.new('V24_30_院内铺装与外部建模场地说明');note.write('按最新标注统一内院灰色条石铺装；主院及外院白色平整场地-0.60m，高的厨房北侧及屋后内区-0.45m。三层楼保持上一版整体降低后的室内水平，入口一个0.15m台阶。外大门至内门道路保留走向并平缓衔接主院，沿场地边建路沿石，入口端露高、随道路逐渐减小。屋后新增内外分隔墙。外围原青砖挡墙及外侧轮廓保持；删除上一版过宽楔形内侧补墙，改为沿原墙的16mm白色内饰面；瓦檐跟随外墙参照并统一宽度0.47m。全部尺寸为依据既有模型及图示拟合，非新增现场测量。')
sc.camera=bpy.data.objects['V24_30_Entry_And_High_Lane'];sc['Version']='V24_30_PAVED_INNER_COURT_FLAT_WHITE_OUTER_PAD_CONSTANT_WALL'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
sc.frame_set(40);bpy.context.view_layer.update()
write('V24_30_Changes.json',{'changed':sorted(set(changed)),'added':added,'removed':removed,'geometry':prep['raw_objects'],'offsets':prep['offsets'],'proof':prep['proof'],'source':str(SOURCE)})
write('V24_30_Collision_Index.json',{'objects':coll,'vertices':len(verts),'triangles':len(faces),'frame':40});(D/'Views.json').write_text(json.dumps(views,ensure_ascii=False),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
write('V24_30_Build.json',{'source':str(SOURCE),'source_sha256':sha(SOURCE),'model':str(P),'sha256':sha(P)});print('V30_SAVED',sha(P),flush=True)
