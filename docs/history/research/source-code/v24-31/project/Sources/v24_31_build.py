import bpy,sys,json,hashlib,shutil,math,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_31';O=Path('E:/jz/JIA/Rebuild_V24_31');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_31.blend';SOURCE=Path('E:/jz/JIA/Rebuild_V24_30/Blender/Architecture_Complete_V24_30.blend')
for p in [R,O/'Blender',O/'Roam',O/'References']:p.mkdir(parents=True,exist_ok=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));sc=bpy.context.scene
(D/'Before_Snapshot.json').write_text(json.dumps(snapshot(bpy),ensure_ascii=False),encoding='utf8');(D/'Source.json').write_text(json.dumps({'model':str(SOURCE),'sha256':sha(SOURCE)}),encoding='utf8')
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));col=bpy.data.collections.new('V24_31_补洞重面白天花完整窗下墙实景木扶手');sc.collection.children.link(col);changed=[];added=[];removed=[]
def principled(name,color,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;m.diffuse_color=(*color,1);return m,b
white,_=principled('M_V24_31_White_Painted_Ceiling',(.88,.88,.86),.85)
wood,b=principled('M_V24_31_Polished_Dark_Red_Stair_Wood',(.075,.008,.004),.29);b.inputs['Coat Weight'].default_value=.23;b.inputs['Coat Roughness'].default_value=.23
ns=wood.node_tree.nodes;lk=wood.node_tree.links;tc=ns.new('ShaderNodeTexCoord');scale=ns.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(26.,26.,1.4);lk.new(tc.outputs['Generated'],scale.inputs[0]);noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.;noise.inputs['Detail'].default_value=2.;lk.new(scale.outputs['Vector'],noise.inputs[0]);ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.028,.003,.0015,1);ramp.color_ramp.elements[1].color=(.10,.012,.006,1);lk.new(noise.outputs['Fac'],ramp.inputs[0]);lk.new(ramp.outputs['Color'],b.inputs['Base Color'])
marble,b=principled('M_V24_31_Stair_Gray_Marble',(.32,.34,.34),.34);ns=marble.node_tree.nodes;lk=marble.node_tree.links;tc=ns.new('ShaderNodeTexCoord');mp=ns.new('ShaderNodeVectorMath');mp.operation='MULTIPLY';mp.inputs[1].default_value=(2.0,6.,1.0);lk.new(tc.outputs['Object'],mp.inputs[0]);noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5.;noise.inputs['Detail'].default_value=3.;noise.inputs['Roughness'].default_value=.72;lk.new(mp.outputs[0],noise.inputs['Vector']);ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(.18,.20,.20,1);ramp.color_ramp.elements[1].position=.72;ramp.color_ramp.elements[1].color=(.43,.45,.44,1);lk.new(noise.outputs['Fac'],ramp.inputs[0]);lk.new(ramp.outputs['Color'],b.inputs['Base Color'])
for n in prep['remove']:
 o=bpy.data.objects.get(n)
 if o:removed.append(n);bpy.data.objects.remove(o,do_unlink=True)
for row in prep['raw_objects']:
 n=row['name'];a=np.load(D/row['file']);o=bpy.data.objects.get(n)
 if o is None:o=bpy.data.objects.new(n,bpy.data.meshes.new(n+'_Initial'));col.objects.link(o);added.append(n)
 else:changed.append(n)
 old=o.data;me=bpy.data.meshes.new(n+'_V24_31');iv=o.matrix_world.inverted();me.from_pydata([iv@Vector(p)for p in a['v']],[],a['f']);o.data=me
 for name in row['materials']:me.materials.append(bpy.data.materials[name])
 me.polygons.foreach_set('material_index',a['mi'].astype(np.int32));me.update();layer=me.uv_layers.new(name='Model_World_UV')
 for face,tex in zip(me.polygons,a['uv']):
  for k,t in zip(face.loop_indices,tex):layer.data[k].uv=t
 if row.get('smooth_wood'):
  for p in me.polygons:p.use_smooth=True
  if hasattr(me,'set_sharp_from_angle'):me.set_sharp_from_angle(angle=math.radians(42))
 o['V24_31_Source_Geometry']=row['file']
 if n=='V24_30_Outer_Yard_White_Building_Pad':o['Top_Area_m2']=prep['proof']['pad_curb']['pad_area_m2']

# Paint the actual slab underside polygons. Floors keep their existing grey
# finish, and there is no second coplanar sheet used as a false ceiling.
painted={}
ceiling_names=['SLAB_JOINED_F2_Geometry','SLAB_JOINED_F3_Geometry','ROOF_MAIN_JOINED_Geometry','UTILITY_FLAT_ROOF_WEST_Geometry']
ceiling_names +=[o.name for o in bpy.data.objects if o.name.startswith('STAIR_F') and '_FLIGHT' in o.name and o.name.endswith('_Geometry')]+['STAIR_LANDING_F1_Geometry','STAIR_LANDING_F2_Geometry']
for n in ceiling_names:
 o=bpy.data.objects[n];me=o.data;idx=len(me.materials);me.materials.append(white);N=o.matrix_world.to_3x3().inverted().transposed();count=0
 if n.startswith('STAIR_'):
  # The reference treads are grey marble, with a white finished soffit.
  grayidx=len(me.materials);me.materials.append(marble)
 for p in me.polygons:
  normal=(N@p.normal).normalized()
  if normal.z<-.15:p.material_index=idx;count+=1
  elif n.startswith('SLAB_JOINED_')and abs(normal.z)<.15:
   center=o.matrix_world@p.center;wallmat=bpy.data.materials['M_Wall_Interior'if 3.99<center.x<4.01 and 7.29<center.y<9.71 else'M_Wall_Exterior']
   if wallmat.name not in me.materials:me.materials.append(wallmat)
   p.material_index=me.materials.find(wallmat.name)
  elif n.startswith('STAIR_'):p.material_index=grayidx
 changed.append(n);painted[n]=count
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith(('BEAM_','KZ_')) and o.name.endswith('_Geometry'):
  o.data.materials.clear();o.data.materials.append(white)
  for p in o.data.polygons:p.material_index=0
  changed.append(o.name)
bpy.context.view_layer.update()

# Use the repaired architectural meshes in the collision cache.
bad=['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','_TREES','_TREE_','TILE_ROWS','TILE_COURSES','_COPING','COVER_TILES','PAN_TILES','DRIP_ENDS','UNIFIED_PAN_BARREL','RIDGE_CAP','END_ORNAMENT','FLORAL','FRETWORK','STEPPED_FRAMES','MOULDED_FRAMES','REFERENCE_RELIEF','CARVED','BLINDS','_PLASTER_STEPPED_RELIEF','PERIMETER_EAVE_BANDS']
verts=[];faces=[];coll=[]
for o in list(bpy.data.objects):
 if o.type!='MESH' or o.hide_render or o.name.startswith('V24_21_'):continue
 if any(k in o.name.upper() for k in bad):continue
 if len(o.data.polygons)>80000 and o.name not in changed and not any(k in o.name.upper() for k in ['GROUND','SOIL','ROAD','TERRAIN','FACADE','PARTITION','SLAB','FOUNDATION']):continue
 me=o.data;me.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@q.co) for q in me.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles);coll.append({'name':o.name,'triangles':len(me.loop_triangles)})
cache=bpy.data.objects['V24_21_Navigation_Collision'];me=bpy.data.meshes.new('V24_31_Navigation_Collision');me.from_pydata(verts,[],faces);me.update();cache.data=me;changed.append(cache.name)
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
 (O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')
views=[('Storage_Ground_Closed',(10.8,-15.3,2.4),(8.7,-12.5,-.50),24),('Gallery_Closed_Riser',(6.5,-9.5,.6),(8.4,-6.8,-.42),24),('Outer_Pad_Curb',(-3.8,-12.8,1.1),(-8.,-6.5,-.6),24),('Outer_Gate_Road',(-10.3,-11.9,1.1),(-3.,-12.3,-.5),24),('Bay_Left_Complete',(3.7,-.35,.60),(1.95,1.1,-.12),28),('Bay_Right_Complete',(9.2,-.20,.60),(10.9,1.1,-.12),28),('White_Ceiling',(7.7,4.6,1.2),(6.5,5.9,3.3),24),('Stair_Lower_Reference',(8.3,9.3,.95),(5.4,8.5,1.9),24),('Stair_Upper_Reference',(8.55,7.95,4.9),(5.3,8.3,3.1),24),('Stair_Smooth_White_Wall',(7.2,9.10,2.2),(5.8,9.7,3.35),24),('Bathroom_Smooth_Wall',(11.6,7.8,.9),(13.,8.55,1.2),28),('F3_Gray_Floor',(10.4,4.3,8.6),(11.5,6.3,7.05),24),('Whole_Site',(-16.,-28.,22.),(0.,-2.,.7),30)]
for tag,loc,aim,lens in views:
 c=bpy.data.objects.new('V24_31_'+tag,bpy.data.cameras.new('V24_31_'+tag));col.objects.link(c);c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.035;c.data.clip_end=200;added.append(c.name)
for t in ['002132','002346','002425','002719','003000','003056','003114','003331','003716','003738','003813','003911','004025','004154']:
 p=Path('D:/Desktop/屏幕截图 2026-10-21 '+t+'.jpg')
 if p.exists():im=bpy.data.images.load(str(p),check_existing=True);im.pack();shutil.copy2(p,O/'References'/p.name)
note=bpy.data.texts.new('V24_31_补洞与模型清理说明');note.write('补齐储藏间前至内门的连续浅灰道路，删除旧重叠道路层和路下旧土层；白色建模场地让出路沿顶面，消除共面重叠；加深厨房廊前原楼板基体以封闭台阶下缝隙。五组飘窗下墙完整接至楼板边，移除五个卫生间高窗旧翻边。屋内楼板及屋顶真实下表面涂白，楼梯灰石面与深红车木扶手按实景照片拟合，保留全部楼梯与26扇门动画。楼梯后墙露出的结构梁收回完成墙面内，删除三楼右卧室多余红色面层，保留结构楼板。扶手细部尺寸根据照片及既有模型拟合，未经新增现场测量。')
sc.camera=bpy.data.objects['V24_31_Stair_Lower_Reference'];sc['Version']='V24_31_CLOSED_GROUND_UNIQUE_SURFACES_WHITE_CEILINGS_PHOTO_STAIRS'
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
sc.frame_set(40);bpy.context.view_layer.update()
write('V24_31_Changes.json',{'changed':sorted(set(changed)),'added':added,'removed':removed,'geometry':prep['raw_objects'],'painted_underside_faces':painted,'proof':prep['proof'],'source':str(SOURCE)})
write('V24_31_Collision_Index.json',{'objects':coll,'vertices':len(verts),'triangles':len(faces),'frame':40});(D/'Views.json').write_text(json.dumps(views,ensure_ascii=False),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
write('V24_31_Build.json',{'source':str(SOURCE),'source_sha256':sha(SOURCE),'model':str(P),'sha256':sha(P)});print('V31_SAVED',sha(P),flush=True)
