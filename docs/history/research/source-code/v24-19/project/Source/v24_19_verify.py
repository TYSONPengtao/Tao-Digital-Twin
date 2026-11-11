"""Fresh native readback: preservation, geometry, grade and material witnesses."""
import bpy,json,sys,hashlib,numpy as np,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_19';R=Path('E:/jz/JIA/Rebuild_V24_19/Reports');P=R.parent/'Blender/Architecture_Complete_V24_19.blend'
before=json.loads((D/'Before_Snapshot.json').read_text());changes=json.loads((R/'V24_19_Changes.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text())};checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
def coords(o):return np.array([o.matrix_world@p.co for p in o.data.vertices],dtype=np.float64)
def tree(o):
 me=o.data;me.calc_loop_triangles();return BVHTree.FromPolygons([Vector(v)for v in coords(o)],[t.vertices[:]for t in me.loop_triangles],all_triangles=True)
def source_tree(n):
 a=np.load(D/idx[n]['file']);return BVHTree.FromPolygons([Vector(v)for v in a['v']],a['f'].tolist(),all_triangles=True)
def ray_z(t,x,y):
 h=t.ray_cast(Vector((x,y,.2)),Vector((0,0,-1)),8);return float(h[0].z)if h[0]is not None else None
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);after=json.loads(json.dumps(snapshot(bpy)));allow=set(changes['changed']);new=set(changes['added']);removed=set(changes['removed'])
ck('Only rejected brick plinth removed',set(before['objects'])-set(after['objects'])==removed=={'V24_18_House_Continuous_Grade_Plinth'})
ck('Only declared new objects',set(after['objects'])-set(before['objects'])==new)
for n,a in before['objects'].items():
 if n in removed:continue
 b=after['objects'][n]
 for k in ['type','parent','matrix','animation','hide_render']:ck('Preserved '+k+' / '+n,a[k]==b[k])
 if n not in allow:ck('Original mesh UV and material slots / '+n,a['mesh_hash']==b['mesh_hash'])
for kind in ['materials','images','actions']:
 for n,a in before[kind].items():ck('Retained original '+kind+' / '+n,after[kind].get(n)==a)
ck('Original 26 doors and all key poses unchanged',len(after['doors'])==26 and before['doors']==after['doors']and before['door_poses']==after['door_poses'])
roots=sorted(o.name for o in bpy.data.objects if o.get('UE_Interaction')=='HINGED_OUTWARD');ck('Twelve outward window hinges retained',len(roots)==12)
poses=[]
for f in [1,20,40]:
 sc.frame_set(f);bpy.context.view_layer.update()
 for n in roots:
  o=bpy.data.objects[n];a=math.degrees(o.rotation_euler.z);exp=float(o['OpenAngleDegrees'])*({1:0,20:.5,40:1}[f]);ck('Window angle '+n+' frame '+str(f),abs(a-exp)<1e-4);poses.append({'root':n,'frame':f,'angle_degrees':a})
sc.frame_set(40);bpy.context.view_layer.update();exports=[]
for n in sorted(allow|new|{'HOUSE_V20_ONE_SOLID_ENTRY_STEP_AND_PORCH_SUPPORT_Geometry'}|{n for n in idx if n.startswith('V24_XIESHAN_')}):
 o=bpy.data.objects.get(n)
 if not o or o.type!='MESH':continue
 me=o.data;me.calc_loop_triangles();v=coords(o);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);fn=f'SAVED_{len(exports):03d}.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi);exports.append({'name':n,'file':fn,'materials':[m.name for m in me.materials]})
slab=bpy.data.objects['SLAB_JOINED_F1_Geometry'];old=np.load(D/idx[slab.name]['file']);ck('First-floor slab exact vertex geometry retained',np.max(abs(coords(slab)-old['v']))<1e-8)
ck('No visible masonry material on ground-floor slab edge',all(slab.data.materials[f.material_index].name=='M_Wall_Exterior'for f in slab.data.polygons if abs(f.normal.z)<.6))
ground_names=[r['name']for r in prep['raw_objects']];trees={n:tree(bpy.data.objects[n])for n in ground_names};oldtrees={n:source_tree(n)for n in ground_names}
stations=[(-.26,y)for y in [3,5,7.3,9.7]]+[(13.26,y)for y in [3,5,7.3,9.7]]+[(x,10.06)for x in [1,4.5,8.5,11.8]]+[(x,1.02)for x in [1.,2.,2.9,10.1,11.1,12.1]]
outline=np.array(prep['proof']['house_grade']['house_footprint']);signed=sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(outline[:-1],outline[1:]));sign=1 if signed>0 else-1
for a,b in zip(outline[:-1],outline[1:]):
 d=b-a;L=np.linalg.norm(d)
 if L<.02:continue
 u=d/L;out=sign*np.array([u[1],-u[0]])
 for s in np.linspace(.10,.90,max(1,math.ceil(L/.40))):
  p=a+d*s+out*.05;x,y=map(float,p)
  if 3.74<=x<=9.26 and-.31<=y<=2.11:continue
  stations.append((x,y))
grade=[]
for x,y in stations:
 hit=[ray_z(t,x,y)for t in trees.values()];oldhit=[ray_z(t,x,y)for t in oldtrees.values()];zz=[z for z in hit if z is not None];oz=[z for z in oldhit if z is not None];z=max(zz)if zz else None
 row={'xy':[x,y],'before_grade_z':max(oz)if oz else None,'new_grade_z':z,'slab_underside_z':float(coords(slab)[:,2].min())};grade.append(row)
 ck('Ground meets original slab without added skirt / '+str((x,y)),z is not None and -.10<=z<=-.04,**row)
far=[]
for x,y in [(-6,3),(-8,-8),(6,-5),(12,-7),(14.6,-5),(6,-.5),(4.1,-.5),(8.9,-.5)]:
 a=[ray_z(t,x,y)for t in trees.values()];b=[ray_z(t,x,y)for t in oldtrees.values()];a=[z for z in a if z is not None];b=[z for z in b if z is not None]
 if not a or not b:continue
 delta=max(a)-max(b);far.append({'xy':[x,y],'change_m':delta});ck('Remote native grade retained / '+str((x,y)),abs(delta)<1e-5,change_m=delta)
for row in prep['objects']:
 n=row['name'];o=bpy.data.objects[n];v=coords(o)
 distance=None
 if len(v)==len(row['v']):good=np.max(abs(v-np.array(row['v'])))<3e-5
 else:
  tr=BVHTree.FromPolygons([Vector(p)for p in row['v']],row['f'],all_triangles=True);distance=max(tr.find_nearest(Vector(p))[3]for p in v);p=np.array(row['v']);bounds=max(abs(v.min(0)-p.min(0)).max(),abs(v.max(0)-p.max(0)).max());good=distance<.001 and bounds<3e-5
 ck('Prepared geometry survives save / '+n,good,nearest_surface_witness_error_m=distance)
for row in prep['raw_objects']:
 n=row['name'];v=coords(bpy.data.objects[n]);ck('Native terrain plan remains original / '+n,np.max(abs(v[:,:2]-np.array(row['v'])[:,:2]))<3e-5)
for tag,n,axis,w,edge in [('Storage East','SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry',0,18.685,18.855),('Storage West','SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry',0,13.205,13.035),('Kitchen South','V24_19_Kitchen_True_Tiled_Verge_Courses',1,-11.94,-12.13),('Kitchen North','V24_19_Kitchen_True_Tiled_Verge_Courses',1,-2.575,-2.385)]:
 v=coords(bpy.data.objects[n]);outer=float(v[:,axis].max())if edge>w else float(v[:,axis].min());proj=abs(outer-w);ck('Actual clay tiles project beyond brick / '+tag,.14<proj<.22,projection_m=proj,brick_outer_face=w,clay_edge=outer)
ck('All image textures embedded',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
uv_report=json.loads((R/'V24_19_Gable_UV.json').read_text());uv_checks=[]
for r in uv_report['surfaces']:
 o=bpy.data.objects[r['object']];v=coords(o);uv=o.data.uv_layers.active;maxerr=0.;ratios=[];bands=True
 for f in o.data.polygons:
  t=v[list(f.vertices)];area=np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]));q=np.array([uv.data[li].uv[:]for li in f.loop_indices]);z=t[:,2].mean();bands&=f.material_index==(0 if z<-1.05-1e-7 else 1 if z<-.38-1e-7 else 2)
  if area<2e-8 or abs(f.normal.z)>.85:continue
  maxerr=max(maxerr,float(abs(q[:,1]-t[:,2]).max()))
  for a,b in [(0,1),(1,2),(2,0)]:
   L=np.linalg.norm(t[b,:2]-t[a,:2])
   if L>.05 and abs(t[b,2]-t[a,2])<2e-5:ratios.append(abs(q[b,0]-q[a,0])/L)
 ck('Continuous world-Z material bands / '+o.name,bands);ck('Metre UV without vertical stretch / '+o.name,maxerr<3e-5)
 ck('Metre UV without horizontal stretch / '+o.name,not ratios or max(abs(a-1)for a in ratios)<.01);ck('UV split leaves gable surface unchanged / '+o.name,r['absolute_area_change_m2']<1e-5)
 uv_checks.append({'object':o.name,'maximum_vertical_error_m':maxerr,'horizontal_scale_min':min(ratios)if ratios else None,'horizontal_scale_max':max(ratios)if ratios else None})
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Solid_Export_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2));fail=[r for r in checks if not r['pass']]
(R/'V24_19_Fresh_Native_QA.json').write_text(json.dumps({'status':'PASS_FRESH_NATIVE_QA'if not fail else'FAIL_FRESH_NATIVE_QA','model_sha256':h,'checks':checks,'failures':fail,'grade_stations':grade,'unchanged_remote_grade':far,'window_poses':poses,'uv_checks':uv_checks},ensure_ascii=False,indent=2),encoding='utf8');print('V19_FRESH_QA',len(checks),'FAIL',len(fail),flush=True)
for f in fail:print('FAIL',f,flush=True)
