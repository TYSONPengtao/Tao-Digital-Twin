"""Lower the complete house to the existing courtyard datum; undo grade compensation."""
import bpy,sys,json,hashlib,shutil,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_29';D.mkdir(exist_ok=True)
O=Path('E:/jz/JIA/Rebuild_V24_29');R=O/'Reports'
for p in [R,O/'Blender',O/'Roam',O/'References']:p.mkdir(parents=True,exist_ok=True)
SOURCE=Path('E:/jz/JIA/Rebuild_V24_28/Blender/Architecture_Complete_V24_28.blend')
P=O/'Blender/Architecture_Complete_V24_29.blend';LEVEL=-.45
def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));sc=bpy.context.scene
before=snapshot(bpy);(D/'Before_Snapshot.json').write_text(json.dumps(before,ensure_ascii=False),encoding='utf8')
(D/'Source.json').write_text(json.dumps({'model':str(SOURCE),'sha256':sha(SOURCE)},ensure_ascii=False),encoding='utf8')
col=bpy.data.collections.new('V24_29_三层楼整体降至原院坪');sc.collection.children.link(col)
changed=[];added=[];removed=[];exports=[]

# Select complete architectural assemblies, not a spatial slice of their meshes.
# The kitchen, storage, court drainage and perimeter are independent buildings.
base=bpy.data.collections['V24_现场建筑_完整基地']
excluded=('SITE_','GATE_','KITCHEN_','CONTEXT','Native','V23_','DOOR_COURTYARD_KITCHEN_','DOOR_STORAGE_','V24_Kitchen_','CONSTRUCTION_COURTYARD_DRAINAGE_','CONSTRUCTION_RAINWATER_RECEIVER_')
roots={o for o in base.objects if o.parent is None and not o.name.startswith(excluded)}
roots.update(o for o in bpy.data.objects if o.parent is None and o.name.startswith(('V24_20_House_Unified_Pan_Barrel_Slope_','V24_18_BAY_WINDOW_','V24_18_WINDOW_')))
assert all(o.type=='EMPTY' or o.name.startswith('V24_20_House_')for o in roots)
house=set(roots)
for o in roots:house.update(o.children_recursive)
assert all(bpy.data.objects[n]in house for n in ['SLAB_JOINED_F1_Geometry','SLAB_JOINED_F2_Geometry','SLAB_JOINED_F3_Geometry','ROMAN_COLUMN_X3.9_Z0_Geometry','ROOF_MAIN_JOINED_Geometry','DOOR_FRONT_CENTER_F1__LEAF_1'])
assert not any(o.name.startswith(('SITE_KITCHEN_','SITE_GAZEBO_','DOOR_COURTYARD_KITCHEN_'))for o in house)
root=bpy.data.objects.new('V24_29_Three_Storey_House_Datum',None);col.objects.link(root);added.append(root.name)
for o in roots:
    m=o.matrix_world.copy();o.parent=root;o.matrix_world=m
root.location.z=LEVEL
root['Lowered_m']=abs(LEVEL);root['Datum']='Original courtyard nominal finish -0.45m'
changed.extend(o.name for o in house)
print('HOUSE_LOWERED',len(house),'objects',len(roots),'roots',LEVEL,flush=True)

def geo(o):
    me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices],float)
    f=np.array([t.vertices[:]for t in me.loop_triangles],int)
    mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles],int)
    uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2))
    return v,f,mi,uv

ground=['SITE_V16_GRADED_INTERIOR_SOIL_Geometry','SITE_V12_REBUILT_COURT_-20_-20_0_Geometry','SITE_V12_REBUILT_COURT_-20_0_0_Geometry','SITE_V12_REBUILT_COURT_0_-20_0_Geometry','SITE_V12_REBUILT_COURT_0_0_0_Geometry','V24_24_House_Front_Matching_Stone_Paving']
for name in ground:
    o=bpy.data.objects[name];sv,f,mi,uv=geo(o);v=sv.copy();soil='SOIL'in name;finish='Matching_Stone'in name
    xy,inv=np.unique(np.round(sv[:,:2],6),axis=0,return_inverse=True)
    if finish:
        joints=np.zeros(len(v),bool)
        for face,mat in zip(f,mi):
            if 'joint'in o.data.materials[int(mat)].name.lower():joints[face]=True
        t=np.clip((sv[:,1]+3.12)/2.82,0,1);lo=-.45+.30*t;hi=np.minimum(-.012,-.40+.40*t)
        old_side=(sv[:,0]>8.15001)|((abs(sv[:,0]-8.15)<.00001)&(sv[:,2]>(lo+hi)/2))
        # The retained paving is a thin solid. Keep upper and lower faces
        # separated, including at the old high/low duplicated seam vertices.
        _,inv=np.unique(np.c_[np.round(sv[:,:2],6),old_side,joints],axis=0,return_inverse=True)
        tops=np.full(inv.max()+1,-1e10);np.maximum.at(tops,inv,sv[:,2]);top=tops[inv]
    else:
        tree=BVHTree.FromPolygons([Vector(p)for p in sv],f.tolist(),all_triangles=True,epsilon=.00001)
        start_z=float(sv[:,2].max())+1.;distance=start_z-float(sv[:,2].min())+2.;tops=[]
        for xx,yy in xy:
            point=tree.ray_cast(Vector((xx,yy,start_z)),Vector((0,0,-1)),distance)[0]
            if point is None:point=tree.find_nearest(Vector((xx,yy,start_z)))[0]
            assert point is not None
            tops.append(point.z)
        # Boundary rays may return a lower shell face at imported seams.
        # A vertex can never lie above the surface used as its deformation datum.
        group_top=np.full(inv.max()+1,-1e10);np.maximum.at(group_top,inv,sv[:,2])
        top=np.maximum(np.array(tops),group_top)[inv]
    bottom=float(sv[:,2].min());mask=np.zeros(len(v),bool);wanted=top.copy()
    x,y,z=sv.T
    if soil:
        mask=(x>-14.00001)&(x<.250001)&(y>-11.60001)&(y<11.90001)
        w=np.clip((x+14.)/1.5,0,1)*np.clip((y+11.6)/.2,0,1)*np.clip((11.9-y)/.25,0,1)
        # Keep the distant sloping site at the outer perimeter unchanged.
        # The complete photographed west yard, through x=-12.5m, is level.
        wanted[mask]=top[mask]+(LEVEL-.002-top[mask])*w[mask]
    else:
        mask=(x>=-.125001)&(x<14.10001)&(y>=-3.6001)&(y<=1.9001)
        wanted[mask]=LEVEL if finish else LEVEL-.002
        if not finish:wanted[mask&(x>.125)&(x<13.10001)]=LEVEL-.010
        # The continuous exterior finish underlaps the lowered floor by 12mm;
        # interior rooms continue to use their unchanged, rigidly moved slabs.
        under=((x>=3.75)&(x<=9.25)&(y>=-.29999))|((x>=-.20)&(x<=13.20)&(y>=0.))
        wanted[mask&under]=LEVEL-.012 if finish else LEVEL-.020
    if finish:
        offset=np.where(joints,-.0015,0.)
        v[mask,2]=wanted[mask]+(sv[mask,2]-top[mask])+offset[mask]
    else:
        factor=np.clip((z-bottom)/np.maximum(1e-7,top-bottom),0,1)
        v[mask,2]+=(wanted[mask]-top[mask])*factor[mask]
    if np.max(abs(v-sv))<1e-8:continue
    # Keep native topology, per-loop UVs and material slots exactly.
    old=o.data;me=old.copy();o.data=me;iv=o.matrix_world.inverted()
    for q,p in zip(me.vertices,v):q.co=iv@Vector(p)
    me.update();changed.append(name)
    np.savez_compressed(D/('GROUND_'+str(len(exports))+'.npz'),source_v=sv,v=v,f=f,mi=mi,uv=uv)
    exports.append({'name':name,'file':'GROUND_'+str(len(exports))+'.npz','kind':'ground','vertices':len(v),'faces':len(f)})
    print('GROUND',name,float(np.max(abs(v-sv))),flush=True)

# Excavate the old raised soil under the lowered slab. The imported soil was
# deliberately filled to -0.06m inside the former 0m floor; moving the house
# without this local excavation would leave earth protruding into its rooms.
soil=bpy.data.objects['SITE_V16_GRADED_INTERIOR_SOIL_Geometry']
def trim_box(v,f,mi,uv,lo,hi):
    # Imported terrain contains legacy open and overlapping shells. Clip only
    # the triangles under the foundation, keeping every exterior face and UV.
    lo=np.array(lo);hi=np.array(hi);vv=v.tolist();ff=[];mm=[];uu=[]
    cache={tuple(np.round(p,8)):i for i,p in enumerate(v)}
    def add(poly,mat):
        for j in range(1,len(poly)-1):
            ps=[poly[0],poly[j],poly[j+1]];ids=[]
            for p,tex in ps:
                key=tuple(np.round(p,8))
                if key not in cache:cache[key]=len(vv);vv.append(p.tolist())
                ids.append(cache[key])
            if len(set(ids))<3:continue
            ff.append(ids);mm.append(mat);uu.append([q[1]for q in ps])
    for face,mat,tuv in zip(f,mi,uv):
        tri=v[face]
        if ((tri.max(0)<lo)|(tri.min(0)>hi)).any():ff.append(face);mm.append(mat);uu.append(tuv);continue
        poly=[(p.copy(),t.copy())for p,t in zip(tri,tuv)]
        for axis in range(3):
            for limit,sign in [(lo[axis],1.),(hi[axis],-1.)]:
                if not poly:break
                inside=[];outside=[]
                for (p,tp),(q,tq)in zip(poly,poly[1:]+poly[:1]):
                    dp=sign*(p[axis]-limit);dq=sign*(q[axis]-limit);a=dp>=-1e-10;b=dq>=-1e-10
                    (inside if a else outside).append((p,tp))
                    if a!=b:
                        t=dp/(dp-dq);item=(p+t*(q-p),tp+t*(tq-tp));inside.append(item);outside.append(item)
                add(outside,mat);poly=inside
    return np.array(vv),np.array(ff),np.array(mm),np.array(uu)
row=next(r for r in exports if r['name']==soil.name);path=D/row['file'];a=np.load(path);sv=a['source_v'].copy();sf=a['f'].copy();v,f,mi,uv=geo(soil)
for lo,hi in [([-.20,0.,-.62],[13.20,10.0,1.]),([3.75,-.30,-1.12],[9.25,2.10,1.]),([.125,-3.60,-.47],[14.10,1.90,1.])]:v,f,mi,uv=trim_box(v,f,mi,uv,lo,hi)
old=soil.data;me=bpy.data.meshes.new('V24_29_Excavated_Soil_Surface');iv=soil.matrix_world.inverted();me.from_pydata([iv@Vector(p)for p in v],[],f)
for mat in old.materials:me.materials.append(mat)
soil.data=me;me.update();layer=me.uv_layers.new(name='Original_Affine_UV')
for face,mat,tuv in zip(me.polygons,mi,uv):
    face.material_index=int(mat)
    for i,q in zip(face.loop_indices,tuv):layer.data[i].uv=q
np.savez_compressed(path,source_v=sv,source_f=sf,v=v,f=f,mi=mi,uv=uv);row.update(terrain_cavity=True,vertices=len(v),faces=len(f))
print('FOUNDATION_CAVITY',len(v),len(f),flush=True)

# Keep the original court drainage below the newly level finish instead of
# leaving its old high end as a small obstruction along the entrance route.
drain=bpy.data.objects['CONSTRUCTION_COURTYARD_DRAINAGE_FINISH_Geometry'];sv,f,mi,uv=geo(drain);v=sv.copy();v[:,2]=np.minimum(v[:,2],LEVEL-.002)
me=drain.data.copy();drain.data=me;iv=drain.matrix_world.inverted()
for q,p in zip(me.vertices,v):q.co=iv@Vector(p)
me.update();changed.append(drain.name);fn='COURT_DRAINAGE.npz';np.savez_compressed(D/fn,source_v=sv,v=v,f=f,mi=mi,uv=uv);exports.append({'name':drain.name,'file':fn,'kind':'drainage'})

# Bury the four old outer gallery slabs that now lie under the matching
# forecourt finish; the remaining original gallery drainage band is retained.
for o in list(bpy.data.objects):
    if not o.name.startswith(('V24_08_Exposed_Court_Slab_11_','V24_08_Exposed_Court_Slab_12_')):continue
    sv,f,mi,uv=geo(o);v=sv.copy();trimmed='_Slab_11_'in o.name
    if trimmed:
        # Keep the old band visible south of the new paving boundary. Cropping
        # its covered end avoids exposing the darker backing outside that boundary.
        v[:,1]=np.minimum(v[:,1],-3.6001)
    else:v[:,2]+=min(0.,LEVEL-.002-float(v[:,2].max()))
    me=o.data.copy();o.data=me;iv=o.matrix_world.inverted()
    for q,p in zip(me.vertices,v):q.co=iv@Vector(p)
    me.update();changed.append(o.name);fn='LEGACY_'+str(len(exports))+'.npz';np.savez_compressed(D/fn,source_v=sv,v=v,f=f,mi=mi,uv=uv);exports.append({'name':o.name,'file':fn,'kind':'trimmed_slab'if trimmed else'buried_slab','trimmed_at_y_m':-3.6001 if trimmed else None})

for o in list(bpy.data.objects):
    if not o.name.startswith('V24_28_High_Approach_Stone_'):continue
    sv,f,mi,uv=geo(o);v=sv.copy();_,inv=np.unique(np.round(v[:,:2],6),axis=0,return_inverse=True);tops=np.full(inv.max()+1,-1e10);np.maximum.at(tops,inv,v[:,2]);top=tops[inv]
    bottom=-.65;target=LEVEL-(.0015 if o.name.endswith('Joints')else 0.)
    v[:,2]+=(target-top)*np.clip((v[:,2]-bottom)/np.maximum(1e-7,top-bottom),0,1)
    old=o.data;me=old.copy();o.data=me;iv=o.matrix_world.inverted()
    for q,p in zip(me.vertices,v):q.co=iv@Vector(p)
    me.update();changed.append(o.name)
    fn='INFILL_'+str(len(exports))+'.npz';np.savez_compressed(D/fn,source_v=sv,v=v,f=f,mi=mi,uv=uv);exports.append({'name':o.name,'file':fn,'kind':'infill'})

edge=bpy.data.objects['V24_28_Continuous_Kitchen_To_House_Step'];removed.append(edge.name);bpy.data.objects.remove(edge,do_unlink=True)
planter=bpy.data.objects['SITE_PLANTER_1_Geometry'];old_high=-.40+.40*((-1.+3.12)/2.82);planter.location.z+=LEVEL-old_high;changed.append(planter.name)

# Rebuild navigation from the visible final architecture and the lowered house.
bpy.context.view_layer.update()
bad=['ORIGINAL_EXTERIOR','CONTEXT','REFERENCE_LAYER','_TREES','_TREE_','TILE_ROWS','TILE_COURSES','_COPING','COVER_TILES','PAN_TILES','DRIP_ENDS','UNIFIED_PAN_BARREL','RIDGE_CAP','END_ORNAMENT','FLORAL','FRETWORK','STEPPED_FRAMES','MOULDED_FRAMES','REFERENCE_RELIEF','CARVED','BLINDS','_PLASTER_STEPPED_RELIEF','PERIMETER_EAVE_BANDS']
verts=[];faces=[];coll=[]
for o in list(bpy.data.objects):
    if o.type!='MESH'or o.hide_render or o.name.startswith('V24_21_'):continue
    if any(k in o.name.upper()for k in bad):continue
    if len(o.data.polygons)>80000 and o.name not in changed and not any(k in o.name.upper()for k in ['GROUND','SOIL','ROAD','TERRAIN','FACADE','PARTITION','SLAB','FOUNDATION']):continue
    me=o.data;me.calc_loop_triangles();k=len(verts);verts.extend(tuple(o.matrix_world@p.co)for p in me.vertices);faces.extend(tuple(k+i for i in t.vertices)for t in me.loop_triangles);coll.append({'name':o.name,'triangles':len(me.loop_triangles)})
cache=bpy.data.objects['V24_21_Navigation_Collision'];me=bpy.data.meshes.new('V24_29_Navigation_Collision');me.from_pydata(verts,[],faces);me.update();cache.data=me;cache['V24_29_Architecture_Updated']=True;changed.append(cache.name)
for txt,fn in [('V24_21_启动漫游.py','start_roam.py'),('V24_21_碰撞控制.py','roam_physics.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_25_测量工具.py','measure_tools.py')]:
    (O/'Roam'/fn).write_text(bpy.data.texts[txt].as_string(),encoding='utf8')
views=[('Entry_Flush',(4.5,-3.5,.75),(7.0,.2,.6),27),('Courtyard_Flush',(7.,-5.6,.85),(9.3,-1.8,-.1),25),('Courtyard_Overview',(7.1,-2.1,5.2),(11.3,-1.4,-.40),23),('West_Exterior',(-8.,4.,1.3),(0.,4.,1.0),24),('West_Overview',(-10.,-2.5,3.),(0.,4.5,-.3),28),('White_Wall',(8.2,-.4,1.1),(13.6,-2.3,1.4),27)]
for tag,loc,aim,lens in views:
    c=bpy.data.objects.new('V24_29_'+tag,bpy.data.cameras.new('V24_29_'+tag));col.objects.link(c);c.location=loc;c.rotation_euler=(Vector(aim)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;c.data.clip_start=.025;c.data.clip_end=300;added.append(c.name)
for t in ['175108','180529','180430']:
    p=Path('D:/Desktop/屏幕截图 2026-10-20 '+t+'.jpg');im=bpy.data.images.load(str(p),check_existing=True);im.pack();shutil.copy2(p,O/'References'/p.name)
note=bpy.data.texts.new('V24_29_整体降低楼房说明');note.write('按用户最新说明，三层楼整体下移0.45米，以原院坪为基准。楼板、楼梯、门窗、阳台、屋面、立柱和附属管线作为完整建筑同时移动，保持各层室内水平和原层高。取消为衔接原高楼面而新增的院内分界台阶及抬高铺装，门前院坪统一为-0.45米。西侧外院地面齐平并去掉横向鼓起的坡带。厨房、储藏房、院墙保留原位；前版直角白墙和木窗收口保留。0.45米来自已有模型院坪标高，非新现场实测。')
sc.camera=bpy.data.objects['V24_29_Entry_Flush'];sc['Version']='V24_29_HOUSE_LOWERED_TO_ORIGINAL_LEVEL_COURTYARD'
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
sc.frame_set(40);bpy.context.view_layer.update()
write('V24_29_Changes.json',{'changed':sorted(set(changed)),'added':added,'removed':removed,'house':sorted(o.name for o in house),'house_roots':sorted(o.name for o in roots),'house_offset_m':[0,0,LEVEL],'courtyard_level_m':LEVEL,'exterior_level_m':LEVEL-.002,'ground':exports,'prior_version':str(SOURCE)})
write('V24_29_Collision_Index.json',{'objects':coll,'triangles':len(faces),'vertices':len(verts),'frame':40})
(D/'Views.json').write_text(json.dumps(views,ensure_ascii=False),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(P),compress=True)
write('V24_29_Build.json',{'source':str(SOURCE),'source_sha256':sha(SOURCE),'model':str(P),'sha256':sha(P),'house_translation_m':LEVEL})
print('V29_SAVED',sha(P),flush=True)
