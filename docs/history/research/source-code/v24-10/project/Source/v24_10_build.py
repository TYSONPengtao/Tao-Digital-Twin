import bpy,bmesh,sys,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W))
from v24_03_junction_blender import _mesh,_box,_bounds,_closed_stats,_difference
from v24_06_common import snapshot
from v24_09_roof import Batch
D=W/'v24_10';O=Path('E:/jz/JIA/Rebuild_V24_10');R=O/'Reports';R.mkdir(parents=True,exist_ok=True);(O/'Blender').mkdir(exist_ok=True);(O/'Source').mkdir(exist_ok=True);(O/'References').mkdir(exist_ok=True)
B=Path('E:/jz/JIA/Rebuild_V24_09/Blender/Architecture_Complete_V24_09.blend');P=O/'Blender/Architecture_Complete_V24_10.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.open_mainfile(filepath=str(B));sc=bpy.context.scene
before=snapshot(bpy);write('V24_10_Before_Snapshot.json',before);sc.frame_set(1);bpy.context.view_layer.update()
co=json.loads((W/'v14/Roof_Junction_QA.json').read_text());oldS=np.array(co['inner_south_top_plane']);oldN=np.array(co['inner_north_top_plane']);fit=json.loads((D/'AsBuilt_Fit.json').read_text());newS=np.array(fit['south']['plane_z_ax_by_c']);newN=np.array(fit['north']['plane_z_ax_by_c']);prep=json.loads((D/'Prepared_Geometry.json').read_text())
col=bpy.data.collections.new('V24_10_储藏房地块与小入口');sc.collection.children.link(col);changed=[];added=[];removed=[];proof={}
def ry(x,S,N):return float(-((N[0]-S[0])*x+N[2]-S[2])/(N[1]-S[1]))
def hh(x,y,S,N):return float(np.dot([x,y,1],S if y<ry(x,S,N)else N))
def xf(p):
 x,y,z=p;weight=max(0,min(1,(x-11.515)/(13.421809-11.515)))
 if x<=11.515:return np.array(p,float)
 nx=x-.121809*weight if x<13.421809 else 13.3+(x-13.421809)*5.35/(18.9-13.421809)
 ro=ry(x,oldS,oldN);rn=ry(nx,newS,newN);sf=-16.35+.012*(nx-13.3);nf=-8.90-.30*(nx-13.3)
 yn=rn+(y-ro)*((rn-sf)/(ro+16.45)if y<ro else (nf-rn)/(-9.45-ro));ny=y+weight*(yn-y)
 dh=hh(nx,ny,newS,newN)-hh(x,y,oldS,oldN);q=max(0,min(1.15,(z+.4)/(hh(x,y,oldS,oldN)+.4)));nz=z+weight*dh*q
 return np.array([nx,ny,nz])
def move(o,scope=None,world=None):
 old=o.data;o.data=old.copy();wm=o.matrix_world.copy()if world is None else world;inv=o.matrix_world.inverted();cnt=0;maxd=0
 for v in o.data.vertices:
  p=np.array(wm@v.co)
  if scope and not scope(p):continue
  q=xf(p);v.co=inv@Vector(q);cnt+=1;maxd=max(maxd,float(np.linalg.norm(q-p)))
 o.data.update()
 if not old.users:bpy.data.meshes.remove(old)
 o['V24_10_AsBuilt_Storage']='Original 3dm registered outline / fitted roof planes and source-video entry relationship'
 changed.append({'name':o.name,'operation':'registered plot and source roof fit','changed_vertices':cnt,'maximum_move_m':maxd,'bounds':_bounds(o)})
 return o
core=['SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry','SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry','SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry','SITE_V14_KITCHEN_STORAGE_DIAGONAL_VALLEY_Geometry','SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry','SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES_Geometry','SITE_V17_STORAGE_VERANDA_TIMBER_ENTRY_FRONT_Geometry','SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry']
for n in core:move(bpy.data.objects[n])
move(bpy.data.objects['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'],lambda p:p[0]>13.32 and p[1]<-9.40)
# Animate the fitted door leaves around fitted hinge origins, keeping the original actions.
doors=[]
for root in list(bpy.data.objects):
 if 'STORAGE'in root.name and root.get('UE_Interaction')in ['HINGED_INWARD','SLIDING']:
  children=[o for o in root.children_recursive if o.type=='MESH'];wms={o.name:o.matrix_world.copy()for o in children};oldp=root.matrix_world.translation.copy();m=root.matrix_world.copy();m.translation=Vector(xf(oldp));root.matrix_world=m;bpy.context.view_layer.update()
  for o in children:move(o,world=wms[o.name])
  doors.append({'root':root.name,'old_hinge':list(oldp),'new_hinge':list(m.translation)})
proof['moving_storage_doors']=doors
def metric_uv(o,kind='metric'):
 uv=o.data.uv_layers.active or o.data.uv_layers.new(name='V24_10_Metric_Surface')
 for f in o.data.polygons:
  no=o.matrix_world.to_3x3()@f.normal;c=o.matrix_world@f.center;mat=o.data.materials[f.material_index];name=mat.name
  bay=None
  if kind=='guard_atlas':
   def distance(r):
    a=np.array(r['a']);b=np.array(r['b']);p=np.array(c)[:2];u=b-a;t=max(0,min(1,float((p-a)@u/(u@u))));return np.linalg.norm(p-a-u*t)
   bay=min(prep['guard_bays'],key=distance);a=np.array(bay['a']);b=np.array(bay['b']);d=(b-a)/np.linalg.norm(b-a)
  for li in f.loop_indices:
   p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
   if bay is not None:
    ss=float((np.array(p)[:2]-a)@d)/bay['length'];uv.data[li].uv=(.032+.75*ss,.0625+.75*(p.z+.253)/.447)if -.255<p.z<.195 else(.90,.92)
   else:
    repeat=(3.2,2.3)if 'Rubble'in name else(4.3,.64)if 'Dark_Courses'in name else(1.6,.9)if'Brick'in name else(1,1)
    u=p.y if abs(no.x)>abs(no.y)else p.x;uv.data[li].uv=(u/repeat[0],p.z/repeat[1])if abs(no.z)<.7 else(p.x,p.y)
def replace(n,parts,new=False,kind='metric'):
 oldob=bpy.data.objects.get(n);V=[];F=[];MI=[];mats=[]
 for part in parts:
  mat=bpy.data.materials[part['material']]
  if mat not in mats:mats.append(mat)
  start=len(V);V+=part['v'];F+=[tuple(start+i for i in ff)for ff in part['f']];MI.extend([mats.index(mat)]*len(part['f']))
 if oldob:
  inv=oldob.matrix_world.inverted();V=[inv@Vector(p)for p in V]
 me=bpy.data.meshes.new(n+'_V24_10');me.from_pydata(V,[],F);me.update()
 for m in mats:me.materials.append(m)
 for f,i in zip(me.polygons,MI):f.material_index=i
 if oldob:
  old=oldob.data;oldob.data=me;o=oldob
  if not old.users:bpy.data.meshes.remove(old)
  changed.append({'name':n,'operation':'replace with closed as-built plot geometry','bounds':_bounds(o)})
 else:o=bpy.data.objects.new(n,me);col.objects.link(o);added.append(n)
 if kind=='base_band':
  o.data.materials.append(bpy.data.materials['M_V18_Storage_Dark_Courses']);bm=bmesh.new();bm.from_mesh(o.data);iv=o.matrix_world.inverted();pt=iv@Vector((0,0,-1.05));no=o.matrix_world.to_3x3().transposed()@Vector((0,0,1));bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=pt,plane_no=no,dist=1e-7,clear_inner=False,clear_outer=False)
  for f in bm.faces:f.material_index=int((o.matrix_world@f.calc_center_median()).z>-1.049999)
  bm.to_mesh(o.data);bm.free();o.data.update()
 metric_uv(o,kind);return o
for ob in prep['objects']:replace(ob['name'],ob['parts'],ob['new'],ob['uv'])
for n in prep['removed']:
 if n in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True);removed.append(n)
# Open the full west eave end, up to the wooden entry front. No false brick slit.
cut=_box(bpy,col,'TEMP_Entry_Open',[13.10,-16.78,-.43],[13.69,-14.79,3.45],bpy.data.materials['M_Grey_Brick'])
for n in ['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry']:
 o=bpy.data.objects[n];r=_difference(bpy,o,cut);changed.append(r)
bpy.data.objects.remove(cut,do_unlink=True);metric_uv(bpy.data.objects['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'])
# Remove obsolete outer toes/road ties only at the resized storage plot.
cut=_box(bpy,col,'TEMP_Storage_Old_Road',[12.50,-19.4,-7],[23.4,-8.65,-.65],bpy.data.materials['M_Stone'])
for n in ['SITE_V12_REBUILT_ROAD_0_-20_0_Geometry']:
 changed.append(_difference(bpy,bpy.data.objects[n],cut))
bpy.data.objects.remove(cut,do_unlink=True)
for row in json.loads((D/'Closed_Legacy_Drain_Replacement.json').read_text(encoding='utf8')):replace(row['name'],row['parts'])
cut=_box(bpy,col,'TEMP_Storage_Obsolete_Fill',[13.025,-19.4,-7],[23.4,-7.0,4],bpy.data.materials['M_Stone'])
for n in ['SITE_V16_GRADED_INTERIOR_SOIL_Geometry','SITE_V17_LOWER_EXTERIOR_GARDEN_TERRAIN_Geometry']:changed.append(_difference(bpy,bpy.data.objects[n],cut))
bpy.data.objects.remove(cut,do_unlink=True)
def inside(p,poly):
 x,y=p;flag=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y)and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:flag=not flag
 return flag
outline=prep['plot']['outline'];mask=prep['terrain']['mask_outer'];terrain_changes=[]
for o in list(bpy.data.objects):
 if o.type!='MESH'or not o.name.startswith('SITE_V14_ORIGINAL_EXTERIOR_'):continue
 old=o.data;o.data=old.copy();bm=bmesh.new();bm.from_mesh(o.data);kill=[]
 for f in bm.faces:
  p=o.matrix_world@f.calc_center_median()
  if p.z<-1 and all(inside(tuple((o.matrix_world@v.co)[:2]),mask)for v in f.verts)and not inside((p.x,p.y),outline):kill.append(f)
 if kill:
  bmesh.ops.delete(bm,geom=kill,context='FACES');wire=[e for e in bm.edges if not e.link_faces]
  if wire:bmesh.ops.delete(bm,geom=wire,context='EDGES')
  bm.to_mesh(o.data);o.data.update();row={'name':o.name,'operation':'remove only local displaced plot road/terrain for original as-built restoration','removed_faces':len(kill)};changed.append(row);terrain_changes.append(row)
 bm.free()
 if not old.users:bpy.data.meshes.remove(old)
# Original source UV/photo remains unchanged on the restored local ground top.
d=np.load(D/'Restored_Original_Ground.npz');o=_mesh(bpy,col,'V24_10_Restored_AsBuilt_Ground',d['v'].tolist(),d['f'].tolist(),bpy.data.materials['M_Stone']);uv=o.data.uv_layers.active
for f in o.data.polygons:
 for j,li in enumerate(f.loop_indices):uv.data[li].uv=d['loop_uv'][f.index,j]
srcmat=bpy.data.materials.new('M_V24_10_Original_AsBuilt_Ground_Photo');srcmat.use_nodes=True;nt=srcmat.node_tree;ns=nt.nodes;bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.97;tx=ns.new('ShaderNodeTexImage');tx.image=bpy.data.images.load('D:/AJAVIS01/ContextCapture/CASES/JIA/Productions/Production_OBJ/Data/Model/Model_0.jpg',check_existing=True);tx.image.pack();vc=ns.new('ShaderNodeVertexColor');vc.layer_name='Original_Source_Ground_Color';nt.links.new(vc.outputs['Color'],bs.inputs['Base Color']);o.data.materials.clear();o.data.materials.append(srcmat)
attr=o.data.color_attributes.new(name='Original_Source_Ground_Color',type='FLOAT_COLOR',domain='CORNER')
for l in o.data.loops:attr.data[l.index].color_srgb=(*d['color'][l.vertex_index],1)
bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
mod=o.modifiers.new('Closed_Local_Terrain_Thickness','SOLIDIFY');mod.thickness=.08;mod.offset=-1;mod.use_even_offset=False;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);added.append(o.name)
proof['terrain_restoration']={k:v for k,v in prep['terrain'].items()if k!='mask_outer'};proof['terrain_restoration']['changed_context']=terrain_changes
tree_changes=[]
for i in range(1,5):
 n=f'SITE_TREE_{i}_Geometry';ob=bpy.data.objects.get(n)
 if not ob:continue
 bb=_bounds(ob);xy=np.mean(np.array(bb)[:,:2],axis=0)
 if not inside(xy,mask)or inside(xy,outline):continue
 dd=np.linalg.norm(d['v'][:,:2]-xy,axis=1);j=int(np.argmin(dd))
 if dd[j]>.40:continue
 dz=float(d['v'][j,2]-bb[0][2]);old=ob.data;ob.data=old.copy();inv=ob.matrix_world.inverted()
 for v in ob.data.vertices:p=ob.matrix_world@v.co;p.z+=dz;v.co=inv@p
 ob.data.update();row={'name':n,'operation':'Seat retained tree on corrected adjacent source terrain; XY unchanged','z_move_m':dz};changed.append(row);tree_changes.append(row)
proof['retained_trees_reseated']=tree_changes
# Entry canopy seen at MP4 0-12 seconds, tied to the kitchen gable and secondary wall.
metal=bpy.data.materials['M_V18_Metal_Weathered'];wood=bpy.data.materials['M_V18_Aged_Storage_Timber'];stone=bpy.data.materials['M_Stone_Frame']
def beam(batch,a,b,w,h):
 a=Vector(a);b=Vector(b);u=(b-a).normalized();v=u.cross(Vector((0,0,1)))
 if v.length<1e-6:v=Vector((1,0,0))
 v.normalize();n=u.cross(v).normalized();V=[tuple(p+v*s*w/2+n*t*h/2)for p in[a,b]for s,t in[(-1,-1),(1,-1),(1,1),(-1,1)]];batch.add(V,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
def boxbatch(batch,lo,hi):
 x,y,z=lo;X,Y,Z=hi;batch.add([(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
def roofz(y):return 3.04+.018*(y+11.87)
can=Batch();fr=Batch();X0,X1=9.52,13.33;Y0,Y1=-16.55,-11.86
V=[(x,y,roofz(y)+dz)for dz in[-.014,0]for x,y in[(X0,Y0),(X1,Y0),(X1,Y1),(X0,Y1)]];can.add(V,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
for y in np.linspace(Y0+.03,Y1-.03,9):beam(fr,(X0,y,roofz(y)-.055),(X1,y,roofz(y)-.055),.04,.075)
for x in[X0+.025,X1-.025]:beam(fr,(x,Y0,roofz(Y0)-.085),(x,Y1,roofz(Y1)-.085),.06,.10)
for x in np.arange(X0+.13,X1,.38):beam(can,(x,Y0,roofz(Y0)+.004),(x,Y1,roofz(Y1)+.004),.014,.008)
# Front end supports land on the secondary wall cap; back ledger lands in the kitchen gable.
beam(fr,(11.06,-16.51,roofz(-16.51)-.085),(13.28,-16.51,roofz(-16.51)-.085),.06,.10)
for x,z0 in[(11.10,2.62),(13.10,2.61)]:beam(fr,(x,-16.51,z0-.03),(x,-16.51,roofz(-16.51)-.035),.055,.055)
for name,batch in[('V24_10_Entry_Metal_Canopy_Sheet',can),('V24_10_Entry_Canopy_Attached_Frame',fr)]:o=batch.object(col,name,[metal],False);added.append(o.name)
# Continuous entry threshold and floor reach the resized veranda.
o=_box(bpy,col,'V24_10_Entry_Continuous_Threshold',(10.90,-16.40,-.53),(13.62,-14.82,-.40),bpy.data.materials['M_V21_Storage_Worn_Cement']);added.append(o.name)
# Restore only the secondary-wall outer white panel band lost in previous perimeter simplification.
fd=json.loads((W/'v19/Facade_Segments.json').read_text());segs=[r for r in fd['brick']if min(r['a'][1],r['b'][1])<-16 and min(r['a'][0],r['b'][0])<13.35 and max(r['a'][0],r['b'][0])>10.8]
def fy(x):
 rows=[r for r in segs if min(r['a'][0],r['b'][0])-1e-5<=x<=max(r['a'][0],r['b'][0])+1e-5];r=min(rows or segs,key=lambda r:abs((r['a'][0]+r['b'][0])/2-x));a,b=r['a'],r['b'];return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
wall=bpy.data.objects['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry'];tree=BVHTree.FromPolygons([wall.matrix_world@v.co for v in wall.data.vertices],[list(f.vertices)for f in wall.data.polygons])
def head(x):
 y=fy(x)+.13;p=tree.ray_cast(Vector((x,y,6)),Vector((0,0,-1)),9)[0];return p.z if p else 2.61
band=Batch();tr=Batch();xs=np.linspace(10.84,12.99,43);N=len(xs);V=[];F=[]
for dd,dz in[(-.002,-.43),(.012,-.43),(.012,-.11),(-.002,-.11)]:V.extend((float(x),fy(x)-dd,head(x)+dz)for x in xs)
for k in range(4):
 for i in range(N-1):F.append((k*N+i,k*N+i+1,((k+1)%4)*N+i+1,((k+1)%4)*N+i))
F.extend([(3*N,2*N,N,0),(N-1,2*N-1,3*N-1,4*N-1)]);band.add(V,F)
for a,b in[(10.91,12.06),(12.14,12.90)]:
 oo=[];ii=[]
 outer=[(a,-.385),(b,-.385),(b,-.155),(a,-.155)];inner=[(a+.018,-.367),(b-.018,-.367),(b-.018,-.173),(a+.018,-.173)]
 for k in range(4):
  A,Bb=outer[k],outer[(k+1)%4];C,E=inner[k],inner[(k+1)%4];count=max(1,math.ceil(abs(Bb[0]-A[0])/.05))
  for j in range(count):t=j/count;oo.append((A[0]*(1-t)+Bb[0]*t,A[1]*(1-t)+Bb[1]*t));ii.append((C[0]*(1-t)+E[0]*t,C[1]*(1-t)+E[1]*t))
 N=len(oo);V=[];F=[]
 for loop,dd in[(oo,.005),(ii,.005),(oo,.025),(ii,.025)]:V.extend((x,fy(x)-dd,head(x)+z)for x,z in loop)
 for j in range(N):
  J=(j+1)%N;F.extend([(j,J,N+J,N+j),(2*N+j,3*N+j,3*N+J,2*N+J),(j,2*N+j,2*N+J,J),(N+j,N+J,3*N+J,3*N+j)])
 tr.add(V,F)
for name,batch,mat in[('V24_10_Secondary_Screenwall_Closed_Panel_Band',band,bpy.data.materials['M_V24_09_Screenwall_Pale_Panel']),('V24_10_Secondary_Screenwall_Panel_Mouldings',tr,stone)]:o=batch.object(col,name,[mat],False);added.append(o.name)
# Relocate the two exterior downpipes to the actual plinth line; original pipe diameters retained.
n='SITE_V18_PHOTO_EXTERIOR_WHITE_PIPE_LINES_Geometry'
if n in bpy.data.objects:
 old=bpy.data.objects[n];bpy.data.objects.remove(old,do_unlink=True);removed.append(n)
from v24_08_geometry import tube
pp=prep['plot']['outline'];frontY=lambda x:pp[0][1]+(pp[-1][1]-pp[0][1])*(x-pp[0][0])/(pp[-1][0]-pp[0][0])
for i,pts in enumerate([[(18.88,frontY(18.88)-.08,2.35),(18.88,frontY(18.88)-.08,-3.45)],[(20.80,-14.70,2.04),(21.18,-15.10,-3.95)]]):
 o=tube(col,'V24_10_Exterior_Downpipe_'+str(i),pts,.036,.003,bpy.data.materials['M_V18_Exterior_White_Pipe']);added.append(o.name)
sc.frame_set(40);bpy.context.view_layer.update()
cams=[('Top',(15,-12.5,26),(15,-12.5,0),17,40),('Entry_Approach',(11.65,-15.55,1.20),(13.95,-15.45,1.8),None,21),('Entry_Outside',(12.0,-19.1,1.5),(13.8,-14.9,1.1),None,28),('Entry_Overview',(11.6,-17.75,4.6),(12.8,-14.6,1.6),None,30),('Gallery',(13.8,-15.35,1.18),(18.4,-15.35,1.15),None,25),('Storage_Inside',(16,-12.9,1.15),(16,-15.4,1.0),None,23),('Outer_Canopy',(19.5,-14.3,1.1),(18.5,-15.2,1.1),None,25),('Outside',(24,-25,9),(16,-13.3,-.1),None,44),('Whole_Site',(28,-32,18),(5,-7,1.3),None,47)]
for name,pos,tar,ortho,lens in cams:
 n='V24_10_'+name;c=bpy.data.objects.new(n,bpy.data.cameras.new(n));sc.collection.objects.link(c);c.location=pos;c.rotation_euler=(Vector(tar)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
 added.append(n)
sc.camera=bpy.data.objects['V24_10_Entry_Approach'];sc.render.engine='CYCLES';sc.render.resolution_x=1600;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
for im in bpy.data.images:
 if im.source=='FILE'and not im.packed_file:
  try:im.pack()
  except Exception:pass
proof.update(source_3dm=json.loads((D/'AsBuilt_Reference.json').read_text(encoding='utf8'))['source_sha256'],source_geometry_fit=fit,plot=prep['plot'],floor_polygons=prep['floor_polygons'],guard_bays=prep['guard_bays'],drain=prep['drain_stations'],base=prep['base'],removed_obsolete=removed,door_count=len(before['doors']),source_version='V24.09',scope='Storage plot, storage superstructure, entry and local old plot road/terrain only')
write('V24_10_Changes.json',{'changed':changed,'added':added,'removed':removed});write('V24_10_AsBuilt_Storage_and_Entry.json',proof)
bpy.ops.wm.save_as_mainfile(filepath=str(P));write('V24_10_Build.json',{'source':str(B),'source_sha256':sha(B),'model':str(P),'sha256':sha(P),'changed':len(set(r['name']for r in changed)),'added':len(added),'removed':len(removed)})
print('SAVED_V24_10',str(P),len(changed),len(added),len(removed),flush=True)
