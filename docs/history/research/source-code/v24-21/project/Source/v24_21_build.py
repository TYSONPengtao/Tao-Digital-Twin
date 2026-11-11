import bpy,json,sys,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
W=Path(__file__).parent;sys.path.insert(0,str(W));D=W/'v24_21';O=Path('E:/jz/JIA/Rebuild_V24_21');R=O/'Reports';R.mkdir(parents=True,exist_ok=True);(O/'Blender').mkdir(exist_ok=True);(O/'Roam').mkdir(exist_ok=True)
src=json.loads((D/'Source.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());P=O/'Blender/Architecture_Complete_V24_21.blend'
bpy.ops.wm.open_mainfile(filepath=src['model']);sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update();added=[]
details=bpy.data.collections.new('V24_21_外墙装饰完整保留');sc.collection.children.link(details)
avcol=bpy.data.collections.new('V24_21_165cm人物与漫游');sc.collection.children.link(avcol)
cachecol=bpy.data.collections.new('V24_21_漫游碰撞数据_隐藏');sc.collection.children.link(cachecol)

def material(n,color,rough=.85,weather=False):
 ma=bpy.data.materials.new(n);ma.diffuse_color=(*color,1);ma.use_nodes=True;bs=next(n for n in ma.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough
 if weather:
  ns=ma.node_tree.nodes;ls=ma.node_tree.links;geo=ns.new('ShaderNodeNewGeometry');noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=14;noise.inputs['Detail'].default_value=2;ls.new(geo.outputs['Position'],noise.inputs['Vector']);ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(*(v*.82 for v in color),1);ramp.color_ramp.elements[1].color=(*(v*1.08 for v in color),1);ls.new(noise.outputs['Fac'],ramp.inputs[0]);ls.new(ramp.outputs[0],bs.inputs['Base Color'])
 return ma
lime=material('M_V24_21_Exterior_Aged_Lime',(.62,.60,.55),.96,True);trim=material('M_V24_21_Exterior_Gray_Trim',(.22,.215,.195),.96,True)

def mesh(n,v,f,col,ma=None,parent=None):
 me=bpy.data.meshes.new(n+'_Mesh');me.from_pydata(v,[],f);me.update()
 if ma is not None:me.materials.append(ma)
 ob=bpy.data.objects.new(n,me);col.objects.link(ob)
 if parent is not None:ob.parent=parent
 added.append(ob.name);return ob
for row in prep['objects']:
 ob=mesh(row['name'],row['v'],row['f'],details,bpy.data.materials[row['material']]);ob['Reference']='025022 exterior frieze photograph';ob['Photo_Fitted_Not_Surveyed']=True

# Exact visible architectural triangles, with high-density ornament and roof
# tiles omitted only from the invisible collision accelerator.
bad=['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','_TREES','_TREE_','TILE_ROWS','TILE_COURSES','_COPING','COVER_TILES','PAN_TILES','DRIP_ENDS','UNIFIED_PAN_BARREL','RIDGE_CAP','END_ORNAMENT','FLORAL','FRETWORK','STEPPED_FRAMES','MOULDED_FRAMES','REFERENCE_RELIEF','CARVED','BLINDS','_PLASTER_STEPPED_RELIEF','PERIMETER_EAVE_BANDS']
verts=[];faces=[];collision_rows=[]
for ob in list(bpy.data.objects):
 if ob.type!='MESH'or ob.hide_render or ob.name.startswith('V24_21_'):continue
 u=ob.name.upper()
 if any(k in u for k in bad):continue
 if len(ob.data.polygons)>80000 and not any(k in u for k in ['GROUND','SOIL','ROAD','TERRAIN','FACADE','PARTITION','SLAB','FOUNDATION']):continue
 me=ob.data;me.calc_loop_triangles();k=len(verts);wm=ob.matrix_world;verts.extend(tuple(wm@v.co)for v in me.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles);collision_rows.append({'name':ob.name,'triangles':len(me.loop_triangles)})
cache=mesh('V24_21_Navigation_Collision',verts,faces,cachecol);cache.hide_render=True;cache.hide_viewport=True;cache.display_type='WIRE';cache['Invisible_Accelerator_Only']=True;cache['Source_Model_SHA256']=src['sha256'];print('COLLISION',len(collision_rows),len(verts),len(faces),flush=True)

def empty(n,parent=None,loc=(0,0,0)):
 o=bpy.data.objects.new(n,None);avcol.objects.link(o);o.parent=parent;o.location=loc;added.append(n);return o
root=empty('V24_21_Roam_Person_165cm');root['Height_m']=1.65;root['Eye_Height_m']=1.53;root['Capsule_Radius_m']=.215
blue=material('M_V24_21_Person_Shirt',(.055,.23,.36));navy=material('M_V24_21_Person_Trousers',(.045,.075,.115));skin=material('M_V24_21_Person_Skin',(.60,.37,.23));shoes=material('M_V24_21_Person_Shoes',(.025,.03,.035));hair=material('M_V24_21_Person_Hair',(.025,.018,.013));eyes=material('M_V24_21_Person_Eyes',(.01,.014,.019))

def ellipsoid(n,centre,scale,ma,parent):
 v=[];f=[];rings=10;segments=16
 # Single pole vertices avoid duplicate zero-area triangles.
 v.append((centre[0],centre[1],centre[2]+scale[2]))
 for i in range(1,rings):
  a=math.pi*i/rings
  for j in range(segments):t=2*math.pi*j/segments;v.append((centre[0]+scale[0]*math.sin(a)*math.cos(t),centre[1]+scale[1]*math.sin(a)*math.sin(t),centre[2]+scale[2]*math.cos(a)))
 bottom=len(v);v.append((centre[0],centre[1],centre[2]-scale[2]))
 for j in range(segments):f.append((0,1+j,1+(j+1)%segments))
 for i in range(rings-2):
  for j in range(segments):a=1+i*segments+j;b=1+i*segments+(j+1)%segments;f.append((a,a+segments,b+segments,b))
 for j in range(segments):f.append((bottom,1+(rings-2)*segments+(j+1)%segments,1+(rings-2)*segments+j))
 o=mesh(n,v,f,avcol,ma,parent)
 for p in o.data.polygons:p.use_smooth=True
 return o
def rod(n,a,b,r,ma,parent):
 a=Vector(a);b=Vector(b);z=(b-a).normalized();x=z.cross(Vector((0,1,0))).normalized();y=z.cross(x);v=[];f=[];N=12
 for p in [a,b]:
  for j in range(N):v.append(tuple(p+r*(x*math.cos(j*2*math.pi/N)+y*math.sin(j*2*math.pi/N))))
 f.extend([tuple(range(N-1,-1,-1)),tuple(range(N,2*N))])
 for j in range(N):J=(j+1)%N;f.append((j,J,N+J,N+j))
 o=mesh(n,v,f,avcol,ma,parent)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o
def box(n,lo,hi,ma,parent):
 v=[(x,y,z)for x in [lo[0],hi[0]]for y in [lo[1],hi[1]]for z in [lo[2],hi[2]]];f=[(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)];return mesh(n,v,[tuple(reversed(p))for p in f],avcol,ma,parent)

box('V24_21_Avatar_Pelvis',(-.145,-.09,.855),(.145,.09,1.01),navy,root)
v=[]
for z,w,d in [(.97,.145,.09),(1.12,.16,.09),(1.35,.205,.105),(1.405,.13,.08)]:v.extend([(-w,-d,z),(w,-d,z),(w,d,z),(-w,d,z)])
f=[(3,2,1,0),(12,13,14,15)]
for i in range(3):
 for j in range(4):J=(j+1)%4;f.append((i*4+j,i*4+J,(i+1)*4+J,(i+1)*4+j))
mesh('V24_21_Avatar_Shirt',v,f,avcol,blue,root);rod('V24_21_Avatar_Neck',(0,0,1.37),(0,0,1.455),.045,skin,root);ellipsoid('V24_21_Avatar_Head',(0,0,1.531),(.085,.076,.115),skin,root)
# A cap with a top at exactly 1.650m, separate from the skin surface.
v=[(0,0,1.65)];N=16
for i in range(1,5):
 a=math.radians(72)*i/4
 for j in range(N):t=2*math.pi*j/N;v.append((.088*math.sin(a)*math.cos(t),.079*math.sin(a)*math.sin(t),1.531+.119*math.cos(a)))
f=[(0,1+j,1+(j+1)%N)for j in range(N)]
for i in range(3):
 for j in range(N):a=1+i*N+j;b=1+i*N+(j+1)%N;f.append((a,a+N,b+N,b))
f.append(tuple(1+3*N+j for j in range(N-1,-1,-1)));mesh('V24_21_Avatar_Hair',v,f,avcol,hair,root)
for x in [-.030,.030]:ellipsoid('V24_21_Avatar_Eye_'+str(x),(x,.071,1.55),(.009,.006,.009),eyes,root)
ellipsoid('V24_21_Avatar_Nose',(0,.078,1.525),(.015,.020,.021),skin,root)
for side,sign in [('L',1),('R',-1)]:
 hip=empty('V24_21_Avatar_'+side+'_Hip',root,(.105*sign,0,.92));rod('V24_21_Avatar_'+side+'_Thigh',(0,0,-.015),(0,0,-.42),.067,navy,hip);knee=empty('V24_21_Avatar_'+side+'_Knee',hip,(0,0,-.42));ellipsoid('V24_21_Avatar_'+side+'_Kneecap',(0,0,0),(.058,.058,.06),navy,knee);rod('V24_21_Avatar_'+side+'_Shin',(0,0,0),(0,.015,-.40),.046,navy,knee);box('V24_21_Avatar_'+side+'_Shoe',(-.066,-.075,-.50),(.066,.165,-.40),shoes,knee)
 shoulder=empty('V24_21_Avatar_'+side+'_Shoulder',root,(.215*sign,0,1.355));ellipsoid('V24_21_Avatar_'+side+'_ShoulderJoint',(0,0,-.02),(.055,.055,.065),blue,shoulder);rod('V24_21_Avatar_'+side+'_Sleeve',(0,0,-.025),(.018*sign,0,-.245),.044,blue,shoulder);rod('V24_21_Avatar_'+side+'_Forearm',(.018*sign,0,-.245),(.022*sign,.015,-.49),.032,skin,shoulder);ellipsoid('V24_21_Avatar_'+side+'_Hand',(.022*sign,.015,-.53),(.035,.031,.055),skin,shoulder)

from v24_21_roam_physics import World,Walker
nav=World(verts,faces);walker=Walker(nav,(6.5,-4.8,-.411));root.location=walker.p
camera=bpy.data.objects.new('V24_21_Third_Person_Follow_Camera',bpy.data.cameras.new('V24_21_Third_Person_Follow_Camera'));avcol.objects.link(camera);camera.data.lens=24;camera.data.clip_start=.035;camera.data.clip_end=300;target=root.location+Vector((0,0,1.25));camera.location=target+Vector((0,-2.462,.434));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();added.append(camera.name)
for suffix,pos,aim,lens in [('Exterior_Frieze',(-34,-.5,3.8),(-22.8,6.7,2.4),43),('Exterior_Frieze_Close',(-27.8,7.9,2.7),(-22.8,6.9,2.45),38),('Person',(6.5,-1.5,1.1),(6.5,-4.8,.45),46)]:
 n='V24_21_'+suffix;c=bpy.data.objects.new(n,bpy.data.cameras.new(n));details.objects.link(c);c.location=pos;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.035;c.data.clip_end=300;added.append(n)
for file,n in [('v24_21_roam_physics.py','V24_21_碰撞控制.py'),('v24_21_roam_controller.py','V24_21_漫游控制器.py'),('v24_21_start_roam.py','V24_21_启动漫游.py')]:
 t=bpy.data.texts.new(n);t.write((W/file).read_text(encoding='utf8'));(O/'Roam'/file.removeprefix('v24_21_')).write_text((W/file).read_text(encoding='utf8'),encoding='utf8')
note=bpy.data.texts.new('V24_21_漫游使用说明');note.write('人物身高1.65米，眼高1.53米。双击启动漫游.cmd进入模型；方向键或WASD移动，空格跳跃，Shift快走，鼠标右键拖动调整方向，滚轮调整跟随距离，V切换人眼/第三人称，Home回院落，Esc退出。默认第三人称。N面板的建筑漫游页可选择院落/一楼/二楼/三楼。可沿真实楼梯行走上下楼，保留建筑、地面、栏杆碰撞。M切换材质预览/流畅模式。直接打开blend时，也可在文本编辑器运行V24_21_启动漫游.py。外墙按025022补齐连续白色装饰带、长短阶角框线及叠涩檐口，原瓦当与建筑全部保留。')
sc['V24_21_Roam_Height_m']=1.65;sc['V24_21_Controls']='Arrow / WASD, Space jump, RMB orbit, Wheel zoom, V view, Home reset, Esc stop';sc['Version']='V24_21_NATIVE_HUMAN_SCALE_ROAM_AND_COMPLETE_EXTERIOR_FRIEZE'
# The native file opens with the person framed; the launcher starts movement.
sc.camera=camera
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='MATERIAL';area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.clip_start=.035;area.spaces.active.clip_end=300
ref=bpy.data.images.load('D:/Desktop/屏幕截图 2026-10-19 025022.jpg',check_existing=True);ref.pack();ref.name='V24_21_Exterior_Frieze_Reference_025022'
(R/'V24_21_Collision_Index.json').write_text(json.dumps({'source_sha256':src['sha256'],'objects':collision_rows,'triangles':len(faces),'vertices':len(verts),'accelerator_is_not_rendered':True},ensure_ascii=False,indent=2))
(R/'V24_21_Detail_Proof.json').write_text(json.dumps(prep['proof'],ensure_ascii=False,indent=2));(R/'V24_21_Changes.json').write_text(json.dumps({'added':added,'removed':[],'changed_original_objects':[]},ensure_ascii=False,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(R/'V24_21_Build.json').write_text(json.dumps({'source':src['model'],'source_sha256':src['sha256'],'model':str(P),'sha256':h},indent=2));print('V21_SAVED',h,'SPAWN',list(root.location),flush=True)
