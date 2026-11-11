import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));D=W/'v24_22';O=Path('E:/jz/JIA/Rebuild_V24_22');R=O/'Reports'
for p in [R,O/'Blender',O/'Roam']:p.mkdir(parents=True,exist_ok=True)
P=O/'Blender/Architecture_Complete_V24_22.blend'
src=json.loads((D/'Source.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text())}
bpy.ops.wm.open_mainfile(filepath=src['model']);sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
col=bpy.data.collections.new('V24_22_厨房实景山墙梁架挂落');sc.collection.children.link(col)
changed=[];added=[];removed=[]
for ma in bpy.data.materials:ma.use_fake_user=True
for a in bpy.data.actions:a.use_fake_user=True
ma=bpy.data.materials.new('M_V24_22_Gable_Gray_Lime');ma.use_nodes=True;ma.diffuse_color=(.22,.215,.20,1)
bs=ma.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=ma.diffuse_color;bs.inputs['Roughness'].default_value=.93

def uv_metres(o):
 me=o.data;uv=me.uv_layers.active or me.uv_layers.new(name='V24_22_Metres')
 for f in me.polygons:
  pts=np.array([o.matrix_world@me.vertices[j].co for j in f.vertices]);normal=o.matrix_world.to_3x3()@f.normal;coords=pts[:,[1,2]]if abs(normal.x)>abs(normal.y)else pts[:,[0,2]]
  if abs(normal.z)>.65:coords=pts[:,:2]
  for li,q in zip(f.loop_indices,coords):uv.data[li].uv=q

def transfer(o):
 d=np.load(D/idx[o.name]['file']);v=d['v'];f=d['f'];mi=d['mi'];t=v[f];tr=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True);uv=o.data.uv_layers.new(name='Source_Affine_Metre_UV')
 for face in o.data.polygons:
  pts=np.array([o.matrix_world@o.data.vertices[i].co for i in face.vertices]);j=tr.find_nearest(Vector(pts.mean(0)))[2];face.material_index=int(mi[j]);p=t[j];A=np.c_[p[1]-p[0],p[2]-p[0]];bc=np.linalg.lstsq(A,(pts-p[0]).T,rcond=None)[0].T;q=d['uv'][j];coords=q[0]+bc[:,0,None]*(q[1]-q[0])+bc[:,1,None]*(q[2]-q[0])
  for li,q in zip(face.loop_indices,coords):uv.data[li].uv=q

for n in prep['remove']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True);removed.append(n)
for row in prep['objects']:
 n=row['name'];me=bpy.data.meshes.new(n+'_V24_22')
 if row['new']:
  me.from_pydata(row['v'],[],row['f']);o=bpy.data.objects.new(n,me);col.objects.link(o);added.append(n)
 else:
  o=bpy.data.objects[n];iv=o.matrix_world.inverted();me.from_pydata([iv@Vector(p)for p in row['v']],[],row['f']);old=o.data
  for ma in old.materials:me.materials.append(ma)
  o.data=me;changed.append(n)
  if not old.users:bpy.data.meshes.remove(old)
 me.update()
 if row.get('transfer'):transfer(o)
 else:me.materials.clear();me.materials.append(bpy.data.materials[row['material']]);uv_metres(o)
 if row.get('wall_finish'):
  white=me.materials.find('M_V24_11_Plain_White_Limewash');brick=me.materials.find('M_V24_18_Continuous_Blue_Brick')
  gray=len(me.materials);me.materials.append(bpy.data.materials['M_V24_22_Gable_Gray_Lime'])
  for face in me.polygons:
   c=o.matrix_world@face.center;no=o.matrix_world.to_3x3()@face.normal
   inside=(-11.96<c.y<-2.49 and c.x>12.7 and no.x<-.25)or(-3.6<c.y<-2.80 and 8.05<c.x<14.3 and no.y<-.35)or(-11.72<c.y<-10.6 and 8.05<c.x<13.44 and no.y>.35)
   if inside:face.material_index=white
   if (c.y<-11.93 and no.y<-.5)or(c.y>-2.58 and no.y>.5):face.material_index=brick
   if 7.42<c.x<8.16 and 1.60<c.z<2.27 and no.x<-.05 and no.z<-.05:face.material_index=gray
 if row.get('frame_base_material_by_z'):
  for face in me.polygons:face.material_index=1 if (o.matrix_world@face.center).z<-.19998 else 0
 o['V24_22_Photo_Fitted']=True;o['V24_22_Reference']='084908 / 083528 / 083630 / 084117 / DJI_0114 / DJI_0116'
 print('APPLIED',n,len(me.polygons),flush=True)

# The shared storage gable has an exposed kitchen-side face. Its white finish
# ends exactly below the kitchen roof plane, retaining brick above the valley.
for row in prep['material_edits']:
 o=bpy.data.objects[row['name']];o.data=o.data.copy();me=o.data;copies={}
 for face in me.polygons:
  c=o.matrix_world@face.center;no=o.matrix_world.to_3x3()@face.normal
  if not(no.x<-.5 and c.x<13.35):continue
  oldi=face.material_index
  if oldi not in copies:
   m=me.materials[oldi].copy();m.name='M_V24_22_Shared_Gable_Interior_'+str(oldi);ns=m.node_tree.nodes;ls=m.node_tree.links;out=next(n for n in ns if n.type=='OUTPUT_MATERIAL');original=out.inputs['Surface'].links[0].from_socket;mix=ns.new('ShaderNodeMixShader');white=ns.new('ShaderNodeBsdfPrincipled');white.inputs['Base Color'].default_value=(.74,.745,.72,1);white.inputs['Roughness'].default_value=.92;ls.new(original,mix.inputs[1]);ls.new(white.outputs[0],mix.inputs[2]);ls.new(mix.outputs[0],out.inputs['Surface']);geo=ns.new('ShaderNodeNewGeometry');sep=ns.new('ShaderNodeSeparateXYZ');sep.name='V24_22_Shared_Wall_Position';ls.new(geo.outputs['Position'],sep.inputs[0]);mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=.488;ls.new(sep.outputs['X'],mul.inputs[0]);add=ns.new('ShaderNodeMath');add.operation='ADD';ls.new(sep.outputs['Z'],add.inputs[0]);ls.new(mul.outputs[0],add.inputs[1]);mask=ns.new('ShaderNodeMath');mask.operation='LESS_THAN';mask.inputs[1].default_value=4.18+.488*11.7625;ls.new(add.outputs[0],mask.inputs[0]);ls.new(mask.outputs[0],mix.inputs[0]);copies[oldi]=len(me.materials);me.materials.append(m)
  face.material_index=copies[oldi]
 for mi in copies.values():
  m=me.materials[mi];ns=m.node_tree.nodes;ls=m.node_tree.links;mix=next(n for n in ns if n.type=='MIX_SHADER');sep=ns['V24_22_Shared_Wall_Position'];roof_factor=mix.inputs[0].links[0].from_socket
  y_min=ns.new('ShaderNodeMath');y_min.operation='GREATER_THAN';y_min.inputs[1].default_value=-11.64;ls.new(sep.outputs['Y'],y_min.inputs[0])
  y_max=ns.new('ShaderNodeMath');y_max.operation='LESS_THAN';y_max.inputs[1].default_value=-8.8;ls.new(sep.outputs['Y'],y_max.inputs[0])
  both=ns.new('ShaderNodeMath');both.operation='MULTIPLY';ls.new(y_min.outputs[0],both.inputs[0]);ls.new(y_max.outputs[0],both.inputs[1])
  all_masks=ns.new('ShaderNodeMath');all_masks.operation='MULTIPLY';ls.new(both.outputs[0],all_masks.inputs[0]);ls.new(roof_factor,all_masks.inputs[1]);ls.new(all_masks.outputs[0],mix.inputs[0])
 changed.append(o.name)

# Refresh navigation from edited architecture, retaining the existing avatar,
# physics and all controls. Decorative high density meshes are render-only.
bad=['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','_TREES','_TREE_','TILE_ROWS','TILE_COURSES','_COPING','COVER_TILES','PAN_TILES','DRIP_ENDS','UNIFIED_PAN_BARREL','RIDGE_CAP','END_ORNAMENT','FLORAL','FRETWORK','STEPPED_FRAMES','MOULDED_FRAMES','REFERENCE_RELIEF','CARVED','BLINDS','_PLASTER_STEPPED_RELIEF','PERIMETER_EAVE_BANDS']
verts=[];faces=[];coll=[]
for o in list(bpy.data.objects):
 if o.type!='MESH'or o.hide_render or o.name.startswith('V24_21_'):continue
 if any(k in o.name.upper() for k in bad):continue
 if len(o.data.polygons)>80000 and not any(k in o.name.upper()for k in ['GROUND','SOIL','ROAD','TERRAIN','FACADE','PARTITION','SLAB','FOUNDATION']):continue
 me=o.data;me.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@v.co)for v in me.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles);coll.append({'name':o.name,'triangles':len(me.loop_triangles)})
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data;me=bpy.data.meshes.new('V24_22_Navigation_Collision_Mesh');me.from_pydata(verts,[],faces);me.update();cache.data=me;changed.append(cache.name);cache['V24_22_Architecture_Updated']=True
if not old.users:bpy.data.meshes.remove(old)

# Embed the tested F8/global resume startup from the previous launcher repair.
bootstrap=(W/'v24_21_start_roam.py').read_text(encoding='utf8');t=bpy.data.texts['V24_21_启动漫游.py'];t.clear();t.write(bootstrap)
(O/'Roam/start_roam.py').write_text(bootstrap,encoding='utf8')
for txt,fn in [('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py')]:
 (O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')

views=[('Side_Enclosure',(5.7,-.45,1.13),(9.75,-3.05,1.85),25),('Porch_Eye',(8.82,-3.75,1.13),(8.74,-10.0,2.19),21),('Facade',(4.6,-7.1,1.13),(8.4,-7.1,1.7),25),('Interior_East',(10.03,-7.25,1.13),(13.40,-7.0,1.75),17),('Interior_Gable',(11.40,-6.65,1.13),(11.6,-3.00,2.12),22),('Side_South',(5.6,-14.4,1.13),(9.2,-11.72,2.0),27)]
for tag,loc,aim,lens in views:
 name='V24_22_'+tag;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c);c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=300;added.append(name)

refs=['D:/Desktop/屏幕截图 2026-10-19 '+s+'.jpg'for s in ['083528','083630','084117','084908']]+['D:/DJI/0003/DCIM/101MEDIA/DJI_0114.JPG','D:/DJI/0003/DCIM/101MEDIA/DJI_0116.JPG']
for fn in refs:
 im=bpy.data.images.load(fn,check_existing=True);im.pack()
sc.camera=bpy.data.objects['V24_22_Side_Enclosure'];sc['Version']='V24_22_KITCHEN_PHOTO_ENCLOSURE_SUPPORTED_TIMBER_AND_OUTER_SQUARE_FRET'
note=bpy.data.texts.new('V24_22_厨房修正说明');note.write('按084908山墙实景整理厨房两端围合：山墙顺坡出挑，灰色线脚与弧形收口接回砖墙。清理两套重叠墙及薄饰面，内侧使用实体墙白色饰面。按083528/083630整理靠墙柱列、水平牵枋和上层弧形梁，按084117整理檐廊横梁，每处一根。按DJI_0114/0116补齐外侧连续阶梯方格挂落，实际建模镂空。保留屋瓦交接、门窗动作、外院装饰及1.65米人物漫游。参考尺寸为照片与现有模型拟合，非测绘。漫游请双击启动漫游.cmd，F8进入，方向键/WASD移动，空格跳，V切换人眼/第三人称。')
sc.frame_set(40);bpy.context.view_layer.update()
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
write('V24_22_Changes.json',{'changed':changed,'added':added,'removed':removed});write('V24_22_Corrections.json',prep['proof']);write('V24_22_Collision_Index.json',{'objects':coll,'triangles':len(faces),'vertices':len(verts),'frame':40})
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
write('V24_22_Build.json',{'source':src['model'],'source_sha256':src['sha256'],'model':str(P),'sha256':h});print('V22_SAVED',h,flush=True)
