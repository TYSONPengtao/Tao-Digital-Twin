import bpy, sys, json, hashlib, numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;D=W/'v24_28';O=Path('E:/jz/JIA/Rebuild_V24_28');R=O/'Reports'
for p in [R,O/'Blender',O/'Roam']:p.mkdir(parents=True,exist_ok=True)
P=O/'Blender/Architecture_Complete_V24_28.blend'
src=json.loads((D/'Source.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'))
idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))}
bpy.ops.wm.open_mainfile(filepath=src['model']);sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
col=bpy.data.collections.new('V24_28_齐平外院连续台阶平直墙顶');sc.collection.children.link(col)
changed=[];added=[];removed=[]
for ma in bpy.data.materials:ma.use_fake_user=True
for a in bpy.data.actions:a.use_fake_user=True

def clear_old(old):
    if not old.users:bpy.data.meshes.remove(old)

def metre_uv(o):
    me=o.data;uv=me.uv_layers.new(name='V24_28_Metres')
    for f in me.polygons:
        pts=np.array([o.matrix_world@me.vertices[j].co for j in f.vertices]);normal=o.matrix_world.to_3x3()@f.normal
        coords=pts[:,[1,2]]if abs(normal.x)>abs(normal.y)else pts[:,[0,2]]
        if abs(normal.z)>.65:coords=pts[:,:2]
        for li,q in zip(f.loop_indices,coords):uv.data[li].uv=q

def transfer(o,name):
    d=np.load(D/idx[name]['file']);v=d['v'];f=d['f'];t=v[f];mi=d['mi'];qvs=d['uv']
    tree=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True)
    uv=o.data.uv_layers.new(name='Source_Affine_Metre_UV')
    for face in o.data.polygons:
        pts=np.array([o.matrix_world@o.data.vertices[i].co for i in face.vertices]);j=tree.find_nearest(Vector(pts.mean(0)))[2]
        face.material_index=int(mi[j]);p=t[j]
        bc=np.linalg.lstsq(np.c_[p[1]-p[0],p[2]-p[0]],(pts-p[0]).T,rcond=None)[0].T;q=qvs[j]
        coords=q[0]+bc[:,0,None]*(q[1]-q[0])+bc[:,1,None]*(q[2]-q[0])
        for li,q in zip(face.loop_indices,coords):uv.data[li].uv=q

for row in prep['raw_objects']:
    o=bpy.data.objects[row['name']];a=np.load(D/row['file']);old=o.data;iv=o.matrix_world.inverted()
    if row['kind']=='copy_mesh':
        me=old.copy();o.data=me
        assert len(me.vertices)==len(a['v'])
        for vertex,point in zip(me.vertices,a['v']):vertex.co=iv@Vector(point)
    else:
        me=bpy.data.meshes.new(o.name+'_V24_28');me.from_pydata([iv@Vector(v)for v in a['v']],[],a['f'])
        for ma in old.materials:me.materials.append(ma)
        o.data=me;me.update();uv=me.uv_layers.new(name='Source_UV_Retained')
        for face,mi,tuv in zip(me.polygons,a['mi'],a['uv']):
            face.material_index=int(mi)
            for li,q in zip(face.loop_indices,tuv):uv.data[li].uv=q
    me.update();clear_old(old);changed.append(o.name);o['V24_28_Reference']='151433 / 151622 / 151816 / 152427'
    print('RAW',o.name,len(me.polygons),flush=True)

for row in prep['objects']:
    name=row['name'];is_new=row.get('new',False)
    if is_new:
        o=bpy.data.objects.new(name,bpy.data.meshes.new(name+'_V24_28'));col.objects.link(o);added.append(name)
    else:o=bpy.data.objects[name];changed.append(name)
    old=o.data;iv=o.matrix_world.inverted();me=bpy.data.meshes.new(name+'_V24_28')
    me.from_pydata([iv@Vector(v)for v in row['v']],[],row['f']);o.data=me;me.update()
    if row.get('transfer'):
        for ma in old.materials:me.materials.append(ma)
        transfer(o,name)
        if name=='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry':
            brick=me.materials.find('M_V24_18_Continuous_Blue_Brick')
            for f in me.polygons:
                c=o.matrix_world@f.center;n=o.matrix_world.to_3x3()@f.normal
                if abs(c.y+2.855)<.00005 and n.y>.8:f.material_index=brick
                if abs(c.x-8.341)<.00005 and n.x<-.8:f.material_index=brick
    else:me.materials.append(bpy.data.materials[row['material']]);metre_uv(o)
    clear_old(old);o['V24_28_Reference']='151433 / 151622 / 151816 / 152427'
    print('SOLID',name,len(me.polygons),flush=True)
for name in prep['remove']:
    o=bpy.data.objects[name];old=o.data;bpy.data.objects.remove(o,do_unlink=True);clear_old(old);removed.append(name)
for row in prep.get('object_offsets',[]):
    o=bpy.data.objects[row['name']];o.location+=Vector(row['translation']);changed.append(o.name)

# Navigation is derived from the final visible surfaces, including the new
# step, changed wall, both paving plateaux and level exterior ground.
bad=['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','_TREES','_TREE_','TILE_ROWS','TILE_COURSES','_COPING','COVER_TILES','PAN_TILES','DRIP_ENDS','UNIFIED_PAN_BARREL','RIDGE_CAP','END_ORNAMENT','FLORAL','FRETWORK','STEPPED_FRAMES','MOULDED_FRAMES','REFERENCE_RELIEF','CARVED','BLINDS','_PLASTER_STEPPED_RELIEF','PERIMETER_EAVE_BANDS']
verts=[];faces=[];coll=[]
for o in list(bpy.data.objects):
    if o.type!='MESH'or o.hide_render or o.name.startswith('V24_21_'):continue
    if any(k in o.name.upper()for k in bad):continue
    if len(o.data.polygons)>80000 and o.name not in changed and not any(k in o.name.upper()for k in ['GROUND','SOIL','ROAD','TERRAIN','FACADE','PARTITION','SLAB','FOUNDATION']):continue
    me=o.data;me.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@v.co)for v in me.vertices)
    faces.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles);coll.append({'name':o.name,'triangles':len(me.loop_triangles)})
cache=bpy.data.objects['V24_21_Navigation_Collision'];old=cache.data
me=bpy.data.meshes.new('V24_28_Navigation_Collision_Mesh');me.from_pydata(verts,[],faces);me.update();cache.data=me;clear_old(old)
changed.append(cache.name);cache['V24_28_Architecture_Updated']=True
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
    (O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')
views=[
 ('West_Exterior_Level',(-7.,5.,1.38),(0.,4.9,1.25),24),
 ('West_Exterior_Overview',(-7.,-2.5,3.1),(0.,4.5,-.05),28),
 ('Continuous_Step_Eye',(7.,-5.6,1.15),(9.3,-1.8,.2),25),
 ('Continuous_Step_Overview',(7.1,-2.1,5.6),(11.3,-1.4,-.15),23),
 ('House_Entry_Level',(6.5,-2.3,.75),(6.5,.3,-.08),28),
 ('Kitchen_End_Recessed',(6.8,-.15,1.25),(10.2,-2.86,1.3),32),
 ('Level_White_Wall',(8.2,-.4,1.25),(13.6,-2.3,1.5),27),
 ('Kitchen_North_Roof',(6.,2.,6.5),(10.9,-3.1,2.7),32)]
for tag,loc,aim,lens in views:
    name='V24_28_'+tag;c=bpy.data.objects.new(name,bpy.data.cameras.new(name));col.objects.link(c)
    c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=300;added.append(name)
for t in prep['proof']['references']:
    path='D:/Desktop/'+t if t.endswith('.png')else'D:/Desktop/屏幕截图 2026-10-20 '+t+'.jpg'
    im=bpy.data.images.load(path,check_existing=True);im.pack()
for filename in prep['proof'].get('reference_files',[]):
    im=bpy.data.images.load(str(D/'References'/filename),check_existing=True);im.pack()
sc.camera=bpy.data.objects['V24_28_Continuous_Step_Eye'];sc['Version']='V24_28_LEVEL_EXTERIOR_CONTINUOUS_STEP_LEVEL_WALL_RECESSED_KITCHEN'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
note=bpy.data.texts.new('V24_28_本次修正说明')
note.write('外部地面齐平；按最后红线，厨房檐廊外台阶沿外缘X=8.15直线接到三层楼入口，取消斜台阶。东侧高、西侧低；各层室内楼板、地坪、门槛及柱体保留。厨房北端山墙及屋檐退回正常端线；封墙在木窗处按180毫米厚度收口，清除穿过窗格的旧厚墙，木窗不移动。对面白墙为单一直面X=14.10，与厨房北墙Y=-2.855形成90度交接；删除斜接段、窄条及多余收口面，墙顶和檐线水平。原外围挡土线保留在墙背。其余前版修正、漫游和L/P测量保留。尺寸依据既有模型和照片标注拟合。')
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
write('V24_28_Changes.json',{'changed':sorted(set(changed)),'added':added,'removed':removed})
write('V24_28_Corrections.json',prep['proof']);write('V24_28_Collision_Index.json',{'objects':coll,'triangles':len(faces),'vertices':len(verts),'frame':40})
(D/'Views.json').write_text(json.dumps(views,ensure_ascii=False),encoding='utf8')
sc.frame_set(40);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
write('V24_28_Build.json',{'source':src['model'],'source_sha256':src['sha256'],'model':str(P),'sha256':h});print('V28_SAVED',h,flush=True)
