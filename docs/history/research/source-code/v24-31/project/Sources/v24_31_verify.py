import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_31';O=Path('E:/jz/JIA/Rebuild_V24_31');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_31.blend';before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));changes=json.loads((R/'V24_31_Changes.json').read_text('utf8'));prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw,flush=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;after=json.loads(json.dumps(snapshot(bpy)));allowed=set(changes['changed'])|set(changes['removed']);diff=[n for n,r in before['objects'].items()if n not in allowed and after['objects'].get(n)!=r];ck('Unrelated native objects retain geometry materials UV transforms and animation',not diff,checked_objects=len(set(before['objects'])-allowed),unexpected_changes=diff)
for key in ['materials','actions','images']:
 diff=[n for n,r in before[key].items()if after[key].get(n)!=r];ck('Original '+key+' preserved',not diff,checked=len(before[key]),unexpected_changes=diff)
ck('Every deletion is declared',set(before['objects'])-set(after['objects'])==set(changes['removed']),removed=len(changes['removed']))
ck('Every new object is declared',set(after['objects'])-set(before['objects'])==set(changes['added']),added=len(changes['added']))
ck('All 26 door rigs and open closed midpoint poses unchanged',len(after['doors'])==len(before['doors'])==26 and after['door_poses']==before['door_poses'])
trees={};export=[]
def geo(n):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();return o,np.array([o.matrix_world@p.co for p in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles])
def tree(n):
 if n not in trees:
  _,v,f=geo(n);trees[n]=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True,epsilon=1e-7)
 return trees[n]
def zhit(n,x,y,z=1.):
 q=tree(n).ray_cast(Vector((x,y,z)),Vector((0,0,-1)),8.)[0];return float(q.z)if q else None
for row in prep['raw_objects']:
 n=row['name'];o,v,f=geo(n);a=np.load(D/row['file']);ck('Readback geometry matches prepared repair / '+n,len(v)==len(a['v'])and len(f)==len(a['f'])and np.max(abs(v-a['v']))<4e-5 and np.array_equal(f,a['f']))
 me=o.data;mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles]);ck('Saved surface material and UV / '+n,(n in changes['painted_underside_faces']or np.array_equal(mi,a['mi']))and np.max(abs(uv-a['uv']))<4e-5)
 if 'SOIL'not in n:
  edges={}
  for face in f:
   for i,j in zip(face,np.roll(face,-1)):k=(int(min(i,j)),int(max(i,j)));edges[k]=edges.get(k,0)+1
  ck('Repair mesh has closed two-face edges / '+n,all(c==2 for c in edges.values()),non_manifold_edges=sum(c!=2 for c in edges.values()))
 fn='FINAL_'+str(len(export))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);export.append({'name':n,'file':fn,'materials':[m.name for m in me.materials]})
# Export every ground or wall partner needed for an independent coplanar audit.
for n in ['V24_30_Individual_Roadside_Curb_Stones','V24_30_Low_Main_Court_Running_Bond_Stone','V24_30_Low_Main_Court_Joint_Base','V24_30_High_North_Lane_And_Rear_Running_Bond_Stone','V24_30_High_North_Lane_And_Rear_Joint_Base','SLAB_JOINED_F1_Geometry','SLAB_JOINED_F2_Geometry','SLAB_JOINED_F3_Geometry']:
 o,v,f=geo(n);fn='FINAL_'+str(len(export))+'.npz';np.savez_compressed(D/fn,v=v,f=f);export.append({'name':n,'file':fn,'materials':[m.name for m in o.data.materials]})
(D/'Final_Geometry_Index.json').write_text(json.dumps(export,ensure_ascii=False),encoding='utf8')
nav='V24_21_Navigation_Collision';road='V24_31_Continuous_Gray_Road_And_Storage_Approach';pad='V24_30_Outer_Yard_White_Building_Pad'
for xy in [(8.1,-12.5),(9.,-13.),(10.,-12.5),(11.,-13.),(12.3,-12.3),(12.8,-14.0),(6.,-14.5),(2.,-14.0),(-9.,-13.6),(-5.,-14.3)]:
 z=zhit(road,*xy);ck('Former hole or road edge has closed grey ground / '+str(xy),z is not None and -1.45<z<-.385,z_m=z)
for xy in [(-4,0),(-10,5),(-15,3),(-10,-5)]:
 z=zhit(pad,*xy);ck('White outer yard remains level / '+str(xy),z is not None and abs(z+.6)<2e-6,z_m=z)
o,v,f=geo(pad);ns=np.cross(v[f][:,1]-v[f][:,0],v[f][:,2]-v[f][:,0]);top=v[f][ns[:,2]>1e-8];ck('All buildable pad top vertices remain on one white horizontal plane',np.max(abs(top[:,:,2]+.60))<2e-6 and [m.name for m in o.data.materials]==['M_V24_30_White_Building_Pad'])
n='SITE_KITCHEN_STONE_FLOOR_Geometry';_,v,f=geo(n);ck('Original gallery base reaches below low court without a gap',v[:,2].min()<-.8 and abs(v[:,2].max()+.400024)<2e-6)
for fl,z in [(1,-.45),(2,3.450024414),(3,7.05)]:
 for x,y in [(1.5,4.),(6.5,3.),(10.5,4.5)]:
  h=zhit(f'SLAB_JOINED_F{fl}_Geometry',x,y,z+1);ck('Retained horizontal indoor structural floor '+str((fl,x,y)),h is not None and abs(h-z)<5e-5,z_m=h)
for row in prep['proof']['bay_underwalls']:
 fl=row['floor'];s=row['side'];n=f'V24_31_F{fl}_Complete_Bay_Underwindow_Walls';x=1.95+(9.1 if s=='R'else 0);floor=row['floor_z_m'];samples=[]
 for z in np.linspace(floor-.12,floor+.54,8):
  q=tree(n).ray_cast(Vector((x,.3,float(z))),Vector((0,1,0)),2)[0];samples.append(None if q is None else list(q))
 ck('Window underwall is complete through slab edge '+str((fl,s)),all(q is not None for q in samples),front_samples=samples)
for fl,sides,floor in [(1,['LEFT','RIGHT'],-.45),(2,['LEFT','RIGHT'],3.450024414),(3,['RIGHT'],7.05)]:
 for side in sides:
  n=f'WINDOW_{side}_C1212_F{fl}_Geometry';o,v,f=geo(n);ck('Frosted high bathroom window retained '+str((fl,side)),after['objects'][n]==before['objects'][n] and abs(v[:,2].min()-(floor+1.8))<3e-5 and abs(v[:,2].max()-(floor+2.6))<3e-5)
  old=f'CONSTRUCTION_SILL_{n}';ck('Obsolete bathroom surround and lower fins removed / '+old,old not in bpy.data.objects)
  originx=2.0 if side=='LEFT'else 11.;direction=Vector((-1,0,0))if side=='LEFT'else Vector((1,0,0));xs=[]
  for z in np.linspace(floor+.15,floor+1.70,9):
   q=tree(f'FACADE_CONTINUOUS_F{fl}_Geometry').ray_cast(Vector((originx,8.55,float(z))),direction,3)[0];xs.append(q.x if q else None)
  ck('Wall below high window is continuous and planar '+str((fl,side)),all(x is not None for x in xs)and max(xs)-min(xs)<3e-5,wall_plane_samples_x_m=xs)
for n,count in changes['painted_underside_faces'].items():
 o=bpy.data.objects[n];N=o.matrix_world.to_3x3().inverted().transposed();bad=[];up=[]
 for p in o.data.polygons:
  no=(N@p.normal).normalized();mat=o.data.materials[p.material_index].name
  if no.z<-.15 and mat!='M_V24_31_White_Painted_Ceiling':bad.append(p.index)
  if n.startswith('SLAB_JOINED_')and no.z>.8:up.append(mat)
 ck('Actual ceiling underside is white / '+n,count>0 and not bad,white_faces=count,incorrect_faces=bad)
 if up:ck('White ceiling assignment preserves grey floor top / '+n,all(m=='M_Concrete'for m in up))
ck('Third floor red floor overlay removed and structural slab retained','HOUSE_V20_F3_RIGHT_BEDROOM_RED_BROWN_WOOD_FLOOR_Geometry'not in bpy.data.objects and after['objects']['SLAB_JOINED_F3_Geometry']['matrix']==before['objects']['SLAB_JOINED_F3_Geometry']['matrix'])
ck('Old square stick rail objects retired',not any(o.name.startswith('STAIR_V4_')and o.type=='MESH'for o in bpy.data.objects))
ck('Turned wood railing has balusters spherical newels and continuous swept handrails',prep['proof']['stair_railing']['turned_balusters']>=75 and prep['proof']['stair_railing']['ball_finial_newels']>=8 and all(n in bpy.data.objects for n in ['V24_31_Stair_Turned_Balusters','V24_31_Stair_Ball_Finial_Newels','V24_31_Stair_Rounded_Handrails']))
for fl,z in [(2,3.30),(3,6.90)]:
 n=f'FLOOR_FASCIA_CONTINUOUS_F{fl}_Geometry';q=tree(n).ray_cast(Vector((6.0,9.3,z)),Vector((0,1,0)),.45)[0];ck('Projecting interior stairwell fascia is absent F'+str(fl),q is None)
wallverts=[];wallfaces=[]
for o in bpy.data.objects:
 if o.type=='MESH' and o.name.startswith(('FACADE_CONTINUOUS_','PARTITIONS_JOINED_','BEAM_','KZ_','SLAB_JOINED_','FLOOR_FASCIA_')):
  _,v,f=geo(o.name);k=len(wallverts);wallverts.extend(Vector(q)for q in v);wallfaces.extend(tuple(int(i)+k for i in t)for t in f)
walltree=BVHTree.FromPolygons(wallverts,wallfaces,all_triangles=True,epsilon=1e-7)
for fl,floor,ceil in [(1,-.45,3.320019),(2,3.450024,6.919995),(3,7.05,10.220044)]:
 yy=[];xx=[]
 for z in np.linspace(floor+.05,ceil-.01,24):
  q=tree(f'FACADE_CONTINUOUS_F{fl}_Geometry').ray_cast(Vector((6.,9.1,float(z))),Vector((0,1,0)),2)[0];yy.append(q.y if q else None)
  q=tree(f'PARTITIONS_JOINED_F{fl}_Geometry').ray_cast(Vector((4.6,8.5,float(z))),Vector((-1,0,0)),1)[0];xx.append(q.x if q else None)
 ck('Rear stair wall is one continuous plane to ceiling F'+str(fl),all(q is not None for q in yy)and max(yy)-min(yy)<2e-5,plane_y_m=yy)
 ck('Left stair wall is one continuous plane to ceiling F'+str(fl),all(q is not None for q in xx)and max(xx)-min(xx)<2e-5,plane_x_m=xx)
 visible_x=[];visible_y=[]
 for z in np.linspace(floor+.1,ceil+.10 if fl<3 else ceil-.01,37):
  q=walltree.ray_cast(Vector((4.6,8.5,float(z))),Vector((-1,0,0)),1)[0];visible_x.append(q.x if q else None)
  q=walltree.ray_cast(Vector((6.,9.1,float(z))),Vector((0,1,0)),2)[0];visible_y.append(q.y if q else None)
 ck('No other column beam slab or fascia projects past plain left stair wall F'+str(fl),all(q is not None for q in visible_x)and max(abs(q-4.)for q in visible_x)<3e-5,first_visible_x_m=visible_x)
 ck('No other column beam slab or fascia projects past plain rear stair wall F'+str(fl),all(q is not None for q in visible_y)and max(abs(q-9.7)for q in visible_y)<3e-5,first_visible_y_m=visible_y)
 corners=[]
 for y in [7.6,8.5,9.59,9.66]:
  for z in np.linspace(floor+.1,ceil-.01,13):
   q=walltree.ray_cast(Vector((4.6,y,float(z))),Vector((-1,0,0)),1)[0];corners.append(q.x if q else None)
 ck('Built-in facade corner pilasters are flush with the full stair left wall F'+str(fl),all(q is not None for q in corners)and max(abs(q-4.)for q in corners)<3e-5,maximum_error_m=max(abs(q-4.)for q in corners if q is not None))
for txt,fn in [('V24_25_测量工具.py','measure_tools.py'),('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py')]:ck('Roam runtime preserved / '+fn,bpy.data.texts[txt].as_string()==(O/'Roam'/fn).read_text('utf8')==(Path('E:/jz/JIA/Rebuild_V24_30/Roam')/fn).read_text('utf8'))
ck('All file textures and reference images are packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
src=json.loads((D/'Source.json').read_text('utf8'));ck('Previous V24.30 native model remains untouched',sha(src['model'])==src['sha256'])
failed=[r for r in checks if not r['pass']];(R/'V24_31_Native_QA.json').write_text(json.dumps({'status':'PASS_NATIVE_REPAIRS_AND_PRESERVATION'if not failed else'FAIL','model_sha256':sha(P),'checks':checks,'failures':failed},ensure_ascii=False,indent=2),encoding='utf8');print('V31_NATIVE_QA',len(checks),'FAIL',len(failed),flush=True)
