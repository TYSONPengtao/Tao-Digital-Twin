import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_32';O=Path('E:/jz/JIA/Rebuild_V24_32');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_32.blend';before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));changes=json.loads((R/'V24_32_Changes.json').read_text('utf8'));prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('CHECK',n,bool(p),kw,flush=True)
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;after=json.loads(json.dumps(snapshot(bpy)));allowed=set(changes['changed'])|set(changes['removed']);diff=[n for n,r in before['objects'].items()if n not in allowed and after['objects'].get(n)!=r];ck('Unrelated native meshes transforms materials UV and animation preserved',not diff,checked=len(set(before['objects'])-allowed),unexpected=diff)
for key in ['materials','actions','images']:
 diff=[n for n,r in before[key].items()if after[key].get(n)!=r];ck('Original '+key+' preserved',not diff,checked=len(before[key]),unexpected=diff)
ck('Every native removal is declared',set(before['objects'])-set(after['objects'])==set(changes['removed']),count=len(changes['removed']))
ck('Every new object is declared',set(after['objects'])-set(before['objects'])==set(changes['added']),count=len(changes['added']))
target='DOOR_STUDY_F3__LEAF';poses=[n for n in before['doors']if n!=target];ck('Other 25 doors keep closed middle and open poses',len(poses)==25 and all(before['door_poses'][f][n]==after['door_poses'][f][n]for f in ['1','20','40']for n in poses))
baseI={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};leaf=target+'_Geometry';old=np.load(D/baseI[leaf]['file']);inv=Matrix(before['objects'][target]['matrix']).inverted();local=[inv@Vector(q)for q in old['v']];doorposes=[]
for frame in [1,20,40]:
 sc.frame_set(frame);bpy.context.view_layer.update();o=bpy.data.objects[leaf];actual=np.array([o.matrix_world@p.co for p in o.data.vertices]);M=Matrix(before['door_poses'][str(frame)][target]);expected=np.array([M@p for p in local]);expected[:,0]=16.9-expected[:,0];err=float(abs(actual-expected).max());ck('Marked room door is mirrored to opposite jamb at frame '+str(frame),err<4e-5,maximum_point_error_m=err);doorposes.append({'frame':frame,'matrix':list(map(list,bpy.data.objects[target].matrix_world))})
ck('Marked room door frame and aperture retained',after['objects']['DOOR_STUDY_F3__FRAME_Geometry']==before['objects']['DOOR_STUDY_F3__FRAME_Geometry'])
sc.frame_set(40);bpy.context.view_layer.update();trees={};geos={};export=[]
def geo(n):
 if n not in geos:
  o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();geos[n]=(o,np.array([o.matrix_world@p.co for p in me.vertices]),np.array([t.vertices[:]for t in me.loop_triangles]))
 return geos[n]
def tree(n):
 if n not in trees:
  o,v,f=geo(n);trees[n]=BVHTree.FromPolygons([Vector(p)for p in v],f.tolist(),all_triangles=True,epsilon=1e-8)
 return trees[n]
for row in prep['raw_objects']:
 n=row['name'];o,v,f=geo(n);a=np.load(D/row['file']);ck('Saved geometric repair matches prepared mesh / '+n,len(v)==len(a['v'])and np.array_equal(f,a['f'])and float(abs(v-a['v']).max())<4e-5)
 me=o.data;mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles]);ck('Saved material and metre UV match repair / '+n,np.array_equal(mi,a['mi'])and float(abs(uv-a['uv']).max())<4e-5)
 edges={}
 for face in f:
  for i,j in zip(face,np.roll(face,-1)):k=(int(min(i,j)),int(max(i,j)));edges[k]=edges.get(k,0)+1
 ck('Closed two-face edges / '+n,all(c==2 for c in edges.values()),bad_edges=sum(c!=2 for c in edges.values()))
# Export actual saved meshes for an independent vertical coplanar audit.
partners=[o.name for o in bpy.data.objects if o.type=='MESH'and not o.hide_render and(o.name.startswith(('FACADE_CONTINUOUS','PARTITIONS_JOINED','HOUSE_V21_','HOUSE_V22_','SLAB_JOINED','BEAM_','KZ_','V24_31_F','CONSTRUCTION_SILL_'))or o.name in ['TERRACE_SIDE_CERAMIC_PANEL_GRID_Geometry','V24_32_F3_Terrace_Panel_Recessed_Grout','V24_32_Continuous_Stair_Wood_Railing','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry','V24_28_Continuous_White_Courtyard_Wall_Face'])]
V=[];F=[]
for n in partners:
 if 'Stair_Wood'in n or 'PERIMETER'in n or'White_Courtyard'in n:continue
 o,v,f=geo(n);k=len(V);V.extend(Vector(q)for q in v);F.extend(tuple(int(i)+k for i in q)for q in f)
walltree=BVHTree.FromPolygons(V,F,all_triangles=True,epsilon=1e-8)
for n in partners:
 o,v,f=geo(n);me=o.data;mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:]for i in t.loops]for t in me.loop_triangles])if me.uv_layers.active else np.zeros((len(f),3,2));visible=np.zeros(len(f),bool)
 if n.startswith(('FACADE','PARTITIONS','HOUSE_V21','HOUSE_V22','SLAB','BEAM','KZ','V24_31_F','CONSTRUCTION_SILL')):
  t=v[f];ns=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ns/=np.maximum(np.linalg.norm(ns,axis=1)[:,None],1e-20);cc=t.mean(1)
  for j in np.where(np.max(abs(ns[:,:2]),axis=1)>.999999)[0]:
   hit=walltree.ray_cast(Vector(cc[j]+ns[j]*.00015),Vector(ns[j]),.18)[0];visible[j]=hit is None
 fn='FINAL_'+str(len(export))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv,visible=visible);export.append({'name':n,'file':fn,'materials':[m.name for m in me.materials]})
(D/'Final_Geometry_Index.json').write_text(json.dumps(export,ensure_ascii=False),encoding='utf8')
def wallhits(origin,direction,dist=3.):
 q=walltree.ray_cast(Vector(origin),Vector(direction),dist)[0];return None if q is None else list(q)
for fl,floor,sides in [(1,-.45,['LEFT','RIGHT']),(2,3.450024414,['LEFT','RIGHT']),(3,7.05,['RIGHT'])]:
 for side in sides:
  x=-1.0 if side=='LEFT'else 14.;di=(1,0,0)if side=='LEFT'else(-1,0,0);hits=[wallhits((x,8.55,float(z)),di)for z in np.linspace(floor+.15,floor+1.72,21)];plane=-.104 if side=='LEFT'else 13.104;ck('High window exterior infill is complete and flush '+str((fl,side)),all(q is not None for q in hits)and max(abs(q[0]-plane)for q in hits if q is not None)<3e-5,expected_x_m=plane,range_x_m=[min(q[0]for q in hits if q),max(q[0]for q in hits if q)])
for floor in [3.450024414,7.05]:
 for side,origin,di,axis,plane in [('east',(14.,8.55,0),(-1,0,0),0,13.104),('west',(-1.,8.55,0),(1,0,0),0,-.104),('rear',(2.,11.,0),(0,-1,0),1,9.904),('rear_stair',(6.,11.,0),(0,-1,0),1,9.904),('rear_slab_end',(7.85,11.,0),(0,-1,0),1,9.904)]:
  hits=[wallhits((origin[0],origin[1],float(z)),di)for z in np.linspace(floor-.36,floor+.35,31)];ck('Floor strip removed with continuous facade '+str((floor,side)),all(q is not None for q in hits)and max(abs(q[axis]-plane)for q in hits if q is not None)<3e-5,plane_m=plane,first_surfaces=hits)
for fl,floor,ceil in [(1,-.45,3.450024414),(2,3.450024414,7.05)]:
 hits=[wallhits((6.,8.2,float(z)),(0,-1,0),1.3)for z in np.linspace(floor+.15,ceil-.001,35)];ck('Front stair wall remains one flush plane through former beam band F'+str(fl),all(q is not None for q in hits)and max(abs(q[1]-7.4)for q in hits if q)<3e-5)
for fl,floor,ceil in [(1,-.45,3.32),(2,3.450024414,6.92),(3,7.05,10.22)]:
 for label,o,di,ax,p in [('left',(4.6,8.5,0),(-1,0,0),0,4.),('rear',(6.,9.1,0),(0,1,0),1,9.7)]:
  h=[wallhits((o[0],o[1],float(z)),di,1.5)for z in np.linspace(floor+.15,ceil-.01,25)];ck('Prior smooth stair '+label+' wall retained F'+str(fl),all(q is not None for q in h)and max(abs(q[ax]-p)for q in h if q)<3e-5)
rail='V24_32_Continuous_Stair_Wood_Railing';o,v,f=geo(rail);adj=[[]for _ in v]
for t in f:
 for a,b in zip(t,np.roll(t,-1)):adj[int(a)].append(int(b));adj[int(b)].append(int(a))
seen=set();counts=[]
for j in range(len(v)):
 if j in seen:continue
 todo=[j];seen.add(j);count=0
 while todo:
  j=todo.pop();count+=1
  for k in adj[j]:
   if k not in seen:seen.add(k);todo.append(k)
 counts.append(count)
ck('All flight rails balusters newels and F3 rear return form the two intended connected assemblies',len(counts)==2 and min(counts)>1000,component_vertices=counts)
for land in [1.499951124,5.249951363]:
 q=tree(rail).ray_cast(Vector((4.05,7.465,land+.7)),Vector((1,0,0)),1.12)[0];ck('Marked extra landing short guard removed at z '+str(land),q is None)
for y in [8.72,9.01,9.30,9.445]:
 q=tree(rail).ray_cast(Vector((8.5,y,7.75)),Vector((-1,0,0)),1.0)[0];ck('Missing F3 rear well edge has a turned baluster at station '+str(y),q is not None)
# Tile coverage is tested over all marked white-patch area, including joints.
tiletree=tree('TERRACE_SIDE_CERAMIC_PANEL_GRID_Geometry');grouttree=tree('V24_32_F3_Terrace_Panel_Recessed_Grout');gaps=[]
for y in np.linspace(7.61,9.55,33):
 for z in np.linspace(7.07,9.93,41):
  loc=Vector((3.5,float(y),float(z)));di=Vector((1,0,0));q=tiletree.ray_cast(loc,di,.31)[0]or grouttree.ray_cast(loc,di,.31)[0]
  if q is None:gaps.append([y,z])
ck('Marked F3 terrace patch has continuous matching ceramic or recessed grout',not gaps,sample_count=33*41,gaps=gaps)
ck('All simple tree proxies removed',not any(o.type=='MESH'and o.name.startswith('SITE_TREE_')for o in bpy.data.objects))
oldprobe=json.loads((D/'Perimeter_Exterior_Probe.json').read_text('utf8'));newprobe=[];perinames=['SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry','V24_28_Continuous_White_Courtyard_Wall_Face','SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_1_Geometry']
for row in oldprobe:
 if row['hit'][4]not in ['M_V24_11_Plain_White_Limewash','M_Wall_Exterior']:continue
 loc=Vector(row['origin']);di=(Vector(row['hit'][3])-loc).normalized();hits=[]
 for n in perinames:
  q,no,j,dd=tree(n).ray_cast(loc,di,1.8)
  if q is not None:
   ob=bpy.data.objects[n];ob.data.calc_loop_triangles();p=ob.data.polygons[ob.data.loop_triangles[j].polygon_index];hits.append((dd,n,ob.data.materials[p.material_index].name))
 hit=min(hits)if hits else None;newprobe.append(hit)
ck('Every detected outward white patch now uses the same original blue-brick material',len(newprobe)==4 and all(q and q[2]=='M_V24_20_Continuous_AsBuilt_Perimeter'for q in newprobe),hits=newprobe)
for txt,fn in [('V24_25_测量工具.py','measure_tools.py'),('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py')]:ck('Roam and measurement runtime retained / '+fn,bpy.data.texts[txt].as_string()==(O/'Roam'/fn).read_text('utf8')==(SOURCE:=Path('E:/jz/JIA/Rebuild_V24_31/Roam')/fn).read_text('utf8'))
ck('All textures and new reference photos packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
source=json.loads((D/'Source.json').read_text('utf8'));ck('Previous V24.31 model remains untouched',sha(source['model'])==source['sha256'])
failed=[c for c in checks if not c['pass']];(R/'V24_32_Native_QA.json').write_text(json.dumps({'status':'PASS_NATIVE_FACADE_RAILING_DOOR_REPAIRS'if not failed else'FAIL','model_sha256':sha(P),'checks':checks,'failures':failed,'corrected_door_poses':doorposes},ensure_ascii=False,indent=2),encoding='utf8');print('V32_NATIVE_QA',len(checks),'FAIL',len(failed),flush=True)
