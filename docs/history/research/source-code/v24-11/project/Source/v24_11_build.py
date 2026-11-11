import bpy,bmesh,sys,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_03_junction_blender import _bounds,_closed_stats,_mesh,_box,_difference
from v24_06_common import snapshot
from v24_09_roof import Batch,h,ring
from v24_11_geometry import warp,structure_warp
D=W/'v24_11';O=Path('E:/jz/JIA/Rebuild_V24_11');R=O/'Reports';R.mkdir(parents=True,exist_ok=True);(O/'Blender').mkdir(exist_ok=True)
B=Path('E:/jz/JIA/Rebuild_V24_10/Blender/Architecture_Complete_V24_10.blend');P=O/'Blender/Architecture_Complete_V24_11.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene;before=snapshot(bpy);write('V24_11_Before_Snapshot.json',before);sc.frame_set(40);bpy.context.view_layer.update()
col=bpy.data.collections.new('V24_11_双柱斜廊与连续弧墙');sc.collection.children.link(col);changed=[];added=[];removed=[]
prep=json.loads((D/'Prepared_Geometry.json').read_text(encoding='utf8'));proof=prep['proof']
def plain(name,color,rough=.88):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1);bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Specular IOR Level'].default_value=.23;return m
white=plain('M_V24_11_Plain_White_Limewash',(.76,.77,.75),.96)
stone=plain('M_V24_11_Screenwall_Dressed_Stone',(.34,.35,.335),.86)
cornice_mat=plain('M_V24_11_Screenwall_Crisp_Soffit_Stone',(.43,.44,.425),.93)
for n in ['V24_10_Entry_Metal_Canopy_Sheet','V24_10_Entry_Canopy_Attached_Frame']:
 assert n in bpy.data.objects;bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True);removed.append(n)
def uv_metric(o):
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='V24_11_Metric_UV')
 for f in o.data.polygons:
  no=o.matrix_world.to_3x3()@f.normal;ma=o.data.materials[f.material_index].name
  rep=(3.2,2.3)if'Rubble'in ma else(4.3,.64)if'Dark_Courses'in ma else(1.6,.9)if'Brick'in ma else(1,1)
  for li in f.loop_indices:
   p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=((p.y if abs(no.x)>abs(no.y)else p.x)/rep[0],p.z/rep[1])if abs(no.z)<.75 else(p.x,p.y)
def transfer_timber(o,source):
 d=np.load(D/(source+'.npz'));v=np.array([structure_warp(p)for p in d['v']]);f=d['f'];mi=d['mi'];uv=d['uv'];tr=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True)
 o.data.materials.clear()
 for name in next(r['materials']for r in json.loads((D/'Inventory.json').read_text(encoding='utf8'))if r['name']==source):o.data.materials.append(bpy.data.materials[name])
 layer=o.data.uv_layers.active
 for face in o.data.polygons:
  p=o.matrix_world@face.center;hit=tr.find_nearest(p)
  if hit[2]is None:continue
  ti=hit[2];face.material_index=int(mi[ti]);a,b,c=v[f[ti]];v0=b-a;v1=c-a;den=(v0@v0)*(v1@v1)-(v0@v1)**2
  if abs(den)<1e-18:continue
  for li in face.loop_indices:
   pp=np.array(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co)-a;u=((v1@v1)*(pp@v0)-(v0@v1)*(pp@v1))/den;vv=((v0@v0)*(pp@v1)-(v0@v1)*(pp@v0))/den;layer.data[li].uv=uv[ti,0]*(1-u-vv)+uv[ti,1]*u+uv[ti,2]*vv
def replace(row,new=False):
 n=row['name'];ob=bpy.data.objects.get(n);old=ob.data if ob else None;V=[];F=[];MI=[];mats=[]
 for p in row['parts']:
  ma=bpy.data.materials[p['material']]
  if ma not in mats:mats.append(ma)
  k=len(V);V+=p['v'];F+=[tuple(k+i for i in ff)for ff in p['f']];MI.extend([mats.index(ma)]*len(p['f']))
 if row.get('materials'):
  mats=[bpy.data.materials[name]for name in row['materials']];MI=row['parts'][0]['face_material']
 if ob:V=[ob.matrix_world.inverted()@Vector(p)for p in V]
 me=bpy.data.meshes.new(n+'_V24_11');me.from_pydata(V,[],F);me.update()
 for ma in mats:me.materials.append(ma)
 for f,i in zip(me.polygons,MI):f.material_index=i
 if ob:ob.data=me;changed.append({'name':n,'operation':'closed geometry replacement'})
 else:ob=bpy.data.objects.new(n,me);col.objects.link(ob);added.append(n)
 uv_metric(ob)
 if row.get('transfer_original_materials_uv'):transfer_timber(ob,n)
 if old and not old.users:bpy.data.meshes.remove(old)
 ob['V24_11_Correction']='Two vertical veranda posts / diagonal gallery / continuous foundation-following rear masonry'
 return ob
for row in prep['replace']:replace(row)
for row in prep['add']:replace(row,True)
for n in ['SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry','SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry','SITE_V14_KITCHEN_STORAGE_DIAGONAL_VALLEY_Geometry']:
 o=bpy.data.objects[n];old=o.data;o.data=old.copy();wm=o.matrix_world.copy();iv=wm.inverted()
 for v in o.data.vertices:v.co=iv@Vector(warp(wm@v.co))
 o.data.update();changed.append({'name':n,'operation':'roof courses, ridge and valley fit to corrected eave'})
 if not old.users:bpy.data.meshes.remove(old)
# Remove complete obsolete raised-brick units on the corrected east/back
# facade only. Other bare-brick kitchen faces remain identical.
n='SITE_KITCHEN_V11_VISIBLE_BARE_GRAY_BRICK_UNITS_Geometry';o=bpy.data.objects[n];old=o.data;o.data=old.copy();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);left=set(bm.verts);kill=[];nbrick=0
while left:
 v=left.pop();part={v};stack=[v]
 while stack:
  for e in stack.pop().link_edges:
   for q in e.verts:
    if q in left:left.remove(q);part.add(q);stack.append(q)
 pp=[o.matrix_world@v.co for v in part];c=sum(pp,Vector())/len(pp)
 if c.x>13.30 and -8.40<c.y<-3.25:kill.extend(part);nbrick+=1
bmesh.ops.delete(bm,geom=kill,context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update();changed.append({'name':n,'operation':'remove complete outdated relief bricks at the continuous rear facade','removed_brick_components':nbrick})
if not old.users:bpy.data.meshes.remove(old)
# The matching gray mortar backing was another old freestanding facade skin.
# Remove the east strip as a complete closed piece, revealing the continuous
# photographic masonry surface behind it.
n='SITE_KITCHEN_V11_VISIBLE_GRAY_MORTAR_BACKING_Geometry';o=bpy.data.objects[n];old=o.data;o.data=old.copy();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);left=set(bm.verts);kill=[];parts=0
while left:
 v=left.pop();part={v};stack=[v]
 while stack:
  for e in stack.pop().link_edges:
   for q in e.verts:
    if q in left:left.remove(q);part.add(q);stack.append(q)
 pp=[o.matrix_world@v.co for v in part];c=sum(pp,Vector())/len(pp)
 if c.x>13.30 and -8.45<c.y<-3.20:kill.extend(part);parts+=1
bmesh.ops.delete(bm,geom=kill,context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update();changed.append({'name':n,'operation':'remove obsolete separate east mortar backing','removed_components':parts})
o.data.materials.append(bpy.data.materials['M_V24_08_AsBuilt_Kitchen_Exterior_Brick']);nf=0
for f in o.data.polygons:
 c=o.matrix_world@f.center
 if c.x>13.30 and -8.45<c.y<-3.20:f.material_index=len(o.data.materials)-1;nf+=1
uv_metric(o);changed[-1]['continuous_east_finish_faces']=nf
if not old.users:bpy.data.meshes.remove(old)
# Old courtyard paving extended into the external re-entrant foundation
# corner. Trim only that obsolete exterior tongue, leaving the court intact.
cut=_box(bpy,col,'TEMP_V11_Old_Exterior_Paving',[13.05,-9.15,-.90],[14.50,-8.20,-.30],bpy.data.materials['M_Stone']);res=_difference(bpy,bpy.data.objects['SITE_V12_REBUILT_COURT_0_-20_0_Geometry'],cut);changed.append(res);bpy.data.objects.remove(cut,do_unlink=True)
poly=[(13.07,-8.86),(13.47,-8.276),(14.184,-3.282),(14.20,-2.83),(16.50,-2.83),(16.50,-8.86)];N=len(poly);V=[(x,y,z)for z in[-.95,-.30]for x,y in poly];F=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(j,(j+1)%N,(j+1)%N+N,j+N)for j in range(N)];cut=_mesh(bpy,col,'TEMP_V11_Kitchen_Rear_Obsolete_Paving_Slivers',V,F,bpy.data.materials['M_Stone']);res=_difference(bpy,bpy.data.objects['SITE_V12_REBUILT_COURT_0_-20_0_Geometry'],cut);res['operation']='trim old paving tongues 60mm behind the continuous kitchen rear face';changed.append(res);bpy.data.objects.remove(cut,do_unlink=True)
# Plain white native shader replaces the projected photographic plaster only.
o=bpy.data.objects['SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry'];o.data=o.data.copy();slots=[]
for i,ma in enumerate(o.data.materials):
 if ma and ma.name=='M_V24_09_Screenwall_Aged_Lime':o.data.materials[i]=white;slots.append(i)
assert slots;changed.append({'name':o.name,'operation':'replace projected photo-plaster slot with untextured white limewash','slots':slots})
# Firm continuous masonry seat: top meets the roof, bottom is level across
# its depth. It steps inward in three crisp courses, like the inner gate.
outer=[3.01,-17.54,11.04,-16.26];mid=[3.10,-17.40,10.95,-16.40];inner=[3.20,-17.23,10.85,-16.57];N=len(ring(outer));V=[];F=[]
def zedge(x):return h(x,-17.64)-.075
profiles=[(outer,None),(outer,.060),(mid,.060),(mid,.155),(inner,.155),(inner,.270)]
for rect,drop in profiles:
 for x,y in ring(rect):V.append((x,y,h(x,y)-.075 if drop is None else zedge(x)-drop))
for j in range(len(profiles)-1):
 for k in range(N):F.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
for rect,drop,top in[(outer,None,True),(inner,.270,False)]:
 x,y,X,Y=rect;off=len(V);ny=33
 for i in range(129):
  for j in range(ny):
   xx=x+(X-x)*i/128;yy=y+(Y-y)*j/32;V.append((xx,yy,h(xx,yy)-.075 if drop is None else zedge(xx)-drop))
 for i in range(128):
  for j in range(32):a=off+i*ny+j;ff=(a,a+ny,a+ny+1,a+1);F.append(ff if top else ff[::-1])
batch=Batch();batch.add(V,F);n='SITE_SOUTH_SCREENWALL_V12_STEPPED_MASONRY_UNDEREAVE_Geometry';ob=batch.object(col,n,[cornice_mat],True,True);changed.append({'name':n,'operation':'continuous thick masonry cornice, depth-level underside, three inward steps'});proof['screenwall_cornice_stats']=_closed_stats(ob)
# Keep the decorative frieze immediately below the deeper structural seat.
for n in ['V24_09_Screenwall_Curved_Panel_Backings','V24_09_Screenwall_Long_Short_Moulded_Frames','V24_09_Screenwall_Triangular_Frieze','V24_09_Screenwall_End_Panel_Stone_Frames','V24_09_Screenwall_White_End_Inset_Panels']:
 o=bpy.data.objects[n];old=o.data;o.data=old.copy()
 for v in o.data.vertices:v.co.z-=.17
 o.data.update();changed.append({'name':n,'operation':'frieze adjusted below the deeper cornice seat'})
 if not old.users:bpy.data.meshes.remove(old)
# New front/rear comparison cameras are saved in the native model.
views=[('Entry_Approach',(11.65,-15.55,1.20),(14.10,-15.32,1.65),22,None),('Entry_Overlap',(12.05,-18.50,3.65),(13.15,-16.13,2.75),38,None),('Veranda',(13.66,-15.80,1.15),(18.35,-15.40,1.35),24,None),('Outside',(24,-25,8.8),(16,-13.5,.2),43,None),('Top',(15,-12.6,27),(15,-12.6,0),45,18),('Rear_Arc',(23.2,-5.7,8.7),(15.7,-9.2,.7),42,None),('Kitchen_Continuous_Wall',(20,-3.4,4.8),(13.6,-7.4,1.0),38,None),('Screenwall_Inside',(7.025,-12.9,1.45),(7.025,-16.9,1.75),15,None),('Screenwall_Underside',(13.3,-19.5,2.65),(10.15,-16.9,3.80),38,None),('Screenwall_Outside',(7.025,-29.0,3.0),(7.025,-16.9,2.1),40,None),('Whole_Site',(28,-32,18),(5,-7,1.3),47,None)]
for name,pos,tar,lens,ortho in views:
 n='V24_11_'+name;c=bpy.data.objects.new(n,bpy.data.cameras.new(n));col.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
 added.append(n)
sc.camera=bpy.data.objects['V24_11_Outside'];sc.frame_set(40);bpy.context.view_layer.update();sc['Version']='V24_11_TWO_DIAGONAL_GALLERY_POSTS_CONTINUOUS_REAR_WALLS'
sc.render.resolution_x=1600;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
guide='V24.11：删除储藏房小入口的铁皮棚及附属框架，独立外侧储藏间的薄铁皮棚保留。檐廊仅两根竖直木柱：入口柱藏在山墙后，另一根在廊端，两柱平面连线与围栏斜交，入口更宽。瓦檐延伸到次照壁之上并补齐承托。储藏房后墙沿原始场景地基轮廓转弧，厨房后侧补为连续完整墙面。照壁内侧改用原生白灰材质，撤去照片投射效果；照壁檐下改为横向平整的实体叠涩承托，增加连续分层石底座。全套建筑、材质、26扇门动画保留，1帧关门、20帧半开、40帧开门。后墙与檐柱关系依据用户标记、原始3dm及视频拟合，非独立测绘或施工结构设计。'
(O/'README_V24_11.txt').write_text(guide,encoding='utf-8-sig');t=bpy.data.texts.get('V24_使用说明')or bpy.data.texts.new('V24_使用说明');t.clear();t.write(guide)
proof['source_version']='V24.10';proof['unchanged_source_3dm']='E:/jz/实景三维场景模型.3dm';proof['removed_entrance_canopy']=removed;proof['preserved_outer_canopy']='SITE_V18_OUTER_STORAGE_THIN_METAL_CANOPY_Geometry';proof['plain_white_material']=white.name;proof['original_doors']=len(before['doors']);write('V24_11_Corrections.json',proof);write('V24_11_Changes.json',{'changed':changed,'added':added,'removed':removed})
bpy.ops.wm.save_as_mainfile(filepath=str(P));write('V24_11_Build.json',{'source':str(B),'source_sha256':sha(B),'model':str(P),'sha256':sha(P),'changed':len(changed),'added':len(added),'removed':len(removed)});print('SAVED_V24_11',str(P),flush=True)
