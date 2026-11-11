import bpy,sys,json,hashlib,shutil,math,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
from v24_18_finish import ArcMap
D=W/'v24_32';O=Path('E:/jz/JIA/Rebuild_V24_32');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_32.blend';SOURCE=Path('E:/jz/JIA/Rebuild_V24_31/Blender/Architecture_Complete_V24_31.blend')
for p in [R,O/'Blender',O/'Roam',O/'References']:p.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));sc=bpy.context.scene;before=snapshot(bpy);(D/'Before_Snapshot.json').write_text(json.dumps(before,ensure_ascii=False),encoding='utf8');(D/'Source.json').write_text(json.dumps({'model':str(SOURCE),'sha256':sha(SOURCE)}),encoding='utf8');sc.frame_set(40);bpy.context.view_layer.update()
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));col=bpy.data.collections.new('V24_32_平整外墙去重完整扶手开向修正');sc.collection.children.link(col);changed=[];added=[];removed=[]
for n in prep['remove']:
 o=bpy.data.objects.get(n)
 if o:removed.append(n);bpy.data.objects.remove(o,do_unlink=True)
for row in prep['raw_objects']:
 n=row['name'];a=np.load(D/row['file']);o=bpy.data.objects.get(n)
 if o is None:o=bpy.data.objects.new(n,bpy.data.meshes.new(n+'_Initial'));col.objects.link(o);added.append(n)
 else:changed.append(n)
 me=bpy.data.meshes.new(n+'_V24_32');iv=o.matrix_world.inverted();me.from_pydata([iv@Vector(p)for p in a['v']],[],a['f']);o.data=me
 for name in row['materials']:me.materials.append(bpy.data.materials[name])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));me.update();layer=me.uv_layers.new(name='Model_World_Metre_UV')
 for face,tex in zip(me.polygons,a['uv']):
  for k,t in zip(face.loop_indices,tex):layer.data[k].uv=t
 if row.get('smooth_wood'):
  for p in me.polygons:p.use_smooth=True
  me.set_sharp_from_angle(angle=math.radians(42))
 o['V24_32_Source_Geometry']=row['file']
terrace=[prep['proof']['terrace_panel']]
# Flip the marked honey-coloured room door as a full handedness change.
# Copy its animation so all other doors and the original action stay intact.
door=bpy.data.objects['DOOR_STUDY_F3__LEAF'];meshes=[o for o in door.children_recursive if o.type=='MESH'];oldworld={o.name:[o.matrix_world@v.co for v in o.data.vertices]for o in meshes};center=8.45;door.location.x=2*center-door.location.x;actions=[]
for tr in door.animation_data.nla_tracks:
 for st in tr.strips:
  old=st.action;old.use_fake_user=True;act=old.copy();act.name='V24_32_Opposite_Hinge_'+old.name;st.action=act
  if act.slots:st.action_slot=act.slots[0]
  for layer in act.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      if fc.data_path=='rotation_euler'and fc.array_index==2:
       for p in fc.keyframe_points:p.co.y=-p.co.y;p.handle_left.y=-p.handle_left.y;p.handle_right.y=-p.handle_right.y
       fc.update()
  actions.append({'old':old.name,'new':act.name})
sc.frame_set(40);bpy.context.view_layer.update()
for o in meshes:
 me=o.data.copy();o.data=me;iv=o.matrix_world.inverted()
 for v,q in zip(me.vertices,oldworld[o.name]):v.co=iv@Vector((2*center-q.x,q.y,q.z))
 # Reflection changes handedness; restore outward polygon winding.
 for p in me.polygons:p.flip()
 me.update();changed.append(o.name)
door['hinge_local_m']=json.dumps([door.location.x,door.location.y,door.location.z]);door['open_angle_deg']=90;door['closed_leaf_direction_xy']=json.dumps([-.9974208700627605,-.07177470280848305]);door['V24_32_Reference']='025023: opposite jamb; same inward room swing';params=json.loads(door['Parameters']);params.update(pivot_world_m=[door.location.x,door.location.y,7.05],open_angle_degrees=90,swing_status='User corrected opposite hinge in 025023',current_pose='OPEN_INWARD');door['Parameters']=json.dumps(params,ensure_ascii=False);changed.append(door.name)
doorproof={'name':door.name,'hinge_world_m':[door.matrix_world.translation.x,door.matrix_world.translation.y,door.matrix_world.translation.z],'old_hinge_world_m':[8.04699993133545,6.015999794006348,7.050000190734863],'swing':'opposite jamb, still into the room','actions':actions,'aperture_and_frame_unchanged':True}
# Colour exposed back/return faces of the white inner finish as the adjoining
# original blue masonry, with the same metre UV and height transition field.
# Inward plaster and the separate decorative white coping bands are retained.
segs=json.loads((W/'v16/Drain_Segments.json').read_text('utf8'));rs=[r for r in segs if not(r['ci']==0 and r['j']in [60,61])];a=np.array([r['a']for r in rs]);d=np.array([r['b']for r in rs])-a;ll=np.einsum('ij,ij->i',d,d);tangent=d/np.sqrt(ll)[:,None];norm=np.c_[tangent[:,1],-tangent[:,0]];hint=np.array([r['outer_a']for r in rs])-a;norm*=np.where(np.einsum('ij,ij->i',norm,hint)>0,1,-1)[:,None];za=np.array([r['za']for r in rs]);zb=np.array([r['zb']for r in rs]);mapper=ArcMap(json.loads((W/'v24_20/Prepared_Geometry.json').read_text('utf8'))['wall_uv_route']);brick=bpy.data.materials['M_V24_20_Continuous_AsBuilt_Perimeter'];blueproof=[]
for name in ['SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry','V24_28_Continuous_White_Courtyard_Wall_Face']:
 o=bpy.data.objects[name];me=o.data.copy();o.data=me;v=np.array([o.matrix_world@p.co for p in me.vertices]);ii=[];zz=[]
 for p in v:
  tt=np.clip(np.einsum('ij,ij->i',p[:2]-a,d)/ll,0,1);dist=np.linalg.norm(a+d*tt[:,None]-p[:2],axis=1);j=int(np.argmin(dist));ii.append(j);zz.append(za[j]+tt[j]*(zb[j]-za[j]))
 att=me.attributes.get('V24_20_Height_Above_Finish_Division')or me.attributes.new('V24_20_Height_Above_Finish_Division','FLOAT','POINT');att.data.foreach_set('value',(v[:,2]-np.array(zz)-.2).astype(np.float32));me.materials.append(brick);idx=len(me.materials)-1;uv=me.uv_layers.active or me.uv_layers.new(name='Masonry_Arc_Length_Metres');count=0
 for p in me.polygons:
  c=o.matrix_world@p.center;no=(o.matrix_world.to_3x3()@p.normal).normalized();tt=np.clip(np.einsum('ij,ij->i',np.array(c[:2])-a,d)/ll,0,1);j=int(np.argmin(np.linalg.norm(a+d*tt[:,None]-np.array(c[:2]),axis=1)))
  yes=abs(no.z)<.3 and np.dot(np.array(no[:2]),norm[j])>.25
  if yes:
   p.material_index=idx;pts=v[list(p.vertices)];q=mapper.triangle(pts)
   for li,qq in zip(p.loop_indices,q):uv.data[li].uv=qq
   count+=1
 changed.append(name);blueproof.append({'object':name,'outer_and_end_faces_matching_blue_brick':count,'inward_plaster_geometry_retained':True})
# Refresh the collision cache from the repaired native geometry.
bad=['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','_TREES','_TREE_','TILE_ROWS','TILE_COURSES','_COPING','COVER_TILES','PAN_TILES','DRIP_ENDS','UNIFIED_PAN_BARREL','RIDGE_CAP','END_ORNAMENT','FLORAL','FRETWORK','STEPPED_FRAMES','MOULDED_FRAMES','REFERENCE_RELIEF','CARVED','BLINDS','_PLASTER_STEPPED_RELIEF','PERIMETER_EAVE_BANDS'];verts=[];faces=[];coll=[]
for o in list(bpy.data.objects):
 if o.type!='MESH'or o.hide_render or o.name.startswith('V24_21_')or any(k in o.name.upper()for k in bad):continue
 if len(o.data.polygons)>80000 and o.name not in changed and not any(k in o.name.upper()for k in ['GROUND','SOIL','ROAD','TERRAIN','FACADE','PARTITION','SLAB','FOUNDATION']):continue
 me=o.data;me.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@q.co)for q in me.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles);coll.append({'name':o.name,'triangles':len(me.loop_triangles)})
cache=bpy.data.objects['V24_21_Navigation_Collision'];me=bpy.data.meshes.new('V24_32_Navigation_Collision');me.from_pydata(verts,[],faces);me.update();cache.data=me;changed.append(cache.name)
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:(O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')
views=[('Exterior_Right_Flat',(23.,-2.,11.),(12.,6.,4.7),28),('Exterior_Back_Flat',(23.,24.,15.),(6.5,6.,4.3),32),('Exterior_Left_High_Windows',(-5.,8.8,3.),(0.,8.55,4.8),24),('Bay_Floor_Joints',(15.,-2.4,5.4),(11.,1.15,3.5),28),('Stair_Joints',(5.8,8.05,2.85),(5.13,8.55,2.45),24),('F2_Stair_Mouth',(8.7,8.,5.),(7.8,9.2,4.5),22),('F3_Rear_Guard',(8.7,8.,8.6),(7.8,9.2,8.0),22),('F3_Front_Guard',(8.65,6.65,8.7),(5.8,7.3,7.7),22),('Stair_Flush_Front_Wall',(4.5,8.,2.8),(6.,7.3,3.25),20),('F3_Opposite_Door',(8.45,7.0,8.5),(8.45,5.5,8.4),26),('F3_Terrace_Wall',(1.5,8.3,8.5),(3.8,8.3,8.5),18),('Blue_Brick_Return',(17.,-.5,1.4),(14.,-2.3,1.),26),('Whole_Site',(-16.,-28.,22.),(0.,-2.,.7),30)]
for tag,loc,aim,lens in views:
 c=bpy.data.objects.new('V24_32_'+tag,bpy.data.cameras.new('V24_32_'+tag));col.objects.link(c);c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.035;c.data.clip_end=300;added.append(c.name)
refs=['024552','024723','024837','024915','025023','025415','025612','025718','025857','003911']
for t in refs:
 p=Path('D:/Desktop/屏幕截图 2026-10-21 '+t+'.jpg')
 if p.exists():im=bpy.data.images.load(str(p),check_existing=True);im.pack();shutil.copy2(p,O/'References'/p.name)
for name in ['启动漫游.cmd','打开修正版模型.cmd']:(O/name).write_text((SOURCE.parents[1]/name).read_text('utf8').replace('V24_31','V24_32'),encoding='utf8')
note=bpy.data.texts.new('V24_32_外墙扶手与开向修正');note.write('高窗下的112mm多余外饰面补块切回原墙面，移除两圈独立楼层饰带并补齐其后真实墙体、收平梁板边。飘窗窗下墙与石材窗套合并，移除跨楼层的重复墙面。删除两段多余平台短护栏；扶手与端柱布尔连接，补齐三楼楼梯口后侧护栏，二楼通向三楼的后侧梯口保持畅通，保留楼梯出入口。三楼标记蜂蜜色房门换到另一侧铰接，保持向房内打开和原洞口。三楼露台旧门洞形缺口补齐同样的矩形瓷砖饰面；青砖墙外露白色背面改用原青砖照片材质，内侧白墙及装饰顶带保留。删除四棵简单树模型。扶手比例继续依据实景照片拟合，未经新增现场测量。')
sc.frame_set(40);bpy.context.view_layer.update();sc.camera=bpy.data.objects['V24_32_Exterior_Right_Flat'];sc['Version']='V24_32_FLUSH_FACADES_UNIQUE_BAY_JOINTS_CONTINUOUS_RAILING_OPPOSITE_DOOR'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
write('V24_32_Changes.json',{'changed':sorted(set(changed)),'added':added,'removed':removed,'geometry':prep['raw_objects'],'proof':prep['proof'],'terrace_materials':terrace,'blue_brick_returns':blueproof,'door':doorproof,'source':str(SOURCE)})
write('V24_32_Collision_Index.json',{'objects':coll,'vertices':len(verts),'triangles':len(faces),'frame':40});(D/'Views.json').write_text(json.dumps(views,ensure_ascii=False),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True);write('V24_32_Build.json',{'source':str(SOURCE),'source_sha256':sha(SOURCE),'model':str(P),'sha256':sha(P)});print('V32_SAVED',sha(P),flush=True)
