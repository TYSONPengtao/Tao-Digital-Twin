"""Reopen the saved deliverable and audit edits, contacts and retained animation."""
import bpy,json,sys,hashlib,numpy as np,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_20';R=Path('E:/jz/JIA/Rebuild_V24_20/Reports');P=R.parent/'Blender/Architecture_Complete_V24_20.blend';before=json.loads((D/'Before_Snapshot.json').read_text(encoding='utf8'));changes=json.loads((R/'V24_20_Changes.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text())};checks=[]
def ck(n,good,**kw):checks.append({'check':n,'pass':bool(good),**kw})
def coords(o):return np.array([o.matrix_world@p.co for p in o.data.vertices],dtype=np.float64)
def tree(o):
 me=o.data;me.calc_loop_triangles();return BVHTree.FromPolygons([Vector(p)for p in coords(o)],[t.vertices[:]for t in me.loop_triangles],all_triangles=True)
def ray(tr,origin,direction,dist=20):
 h=tr.ray_cast(Vector(origin),Vector(direction),dist);return list(h[0])if h[0]is not None else None
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;sc.frame_set(40);after=json.loads(json.dumps(snapshot(bpy)));changed=set(changes['changed']);added=set(changes['added']);removed=set(changes['removed']);door_names={n for n in before['objects']if n.startswith('DOOR_BATH_F1_R__')}
ck('Only declared objects removed',set(before['objects'])-set(after['objects'])==removed)
ck('Only declared objects added',set(after['objects'])-set(before['objects'])==added)
for n,a in before['objects'].items():
 if n in removed:continue
 b=after['objects'][n]
 for k in ['type','animation','hide_render']:ck('Preserved '+k+' / '+n,a[k]==b[k])
 if n not in door_names:
  for k in ['parent','matrix']:ck('Preserved '+k+' / '+n,a[k]==b[k])
 if n not in changed:ck('Preserved mesh and UV / '+n,a['mesh_hash']==b['mesh_hash'])
for kind in ['materials','images','actions']:
 for n,a in before[kind].items():ck('Original library '+kind+' / '+n,after[kind].get(n)==a)
ck('All original 26 doors retained including stair-facing WC door',set(before['doors'])==set(after['doors'])and len(after['doors'])==26)
for frame in ['1','20','40']:
 for n,a in before['door_poses'][frame].items():
  expected=np.array(a)
  if n=='DOOR_BATH_F1_R__LEAF':expected[0,3]-=1.2
  ck('Door animation pose '+n+' / '+frame,np.max(abs(expected-np.array(after['door_poses'][frame][n])))<3e-5)
roots=sorted(o.name for o in bpy.data.objects if o.get('UE_Interaction')=='HINGED_OUTWARD');ck('Twelve outward window roots retained',len(roots)==12)
for frame in [1,20,40]:
 sc.frame_set(frame);bpy.context.view_layer.update()
 for n in roots:
  o=bpy.data.objects[n];angle=math.degrees(o.rotation_euler.z);expected=float(o['OpenAngleDegrees'])*{1:0,20:.5,40:1}[frame];ck('Window angle '+n+' / '+str(frame),abs(angle-expected)<1e-4)
sc.frame_set(40);bpy.context.view_layer.update()
for n in ['SLAB_JOINED_F1_Geometry','STAIR_F1_FLIGHT_1_Geometry','STAIR_F1_FLIGHT_2_Geometry']:
 if n in idx:ck('Untranslated original datum / '+n,before['objects'][n]['matrix']==after['objects'][n]['matrix']and before['objects'][n]['mesh_hash']==after['objects'][n]['mesh_hash'])

post=tree(bpy.data.objects['SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry']);floor=tree(bpy.data.objects['SITE_KITCHEN_STONE_FLOOR_Geometry']);contacts=[]
outer_wall=tree(bpy.data.objects['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'])
for x,y in prep['proof']['kitchen_posts']['axes_xy']:
 foot=ray(post,[x,y,-1],[0,0,1]);ff=ray(floor,[x,y,.1],[0,0,-1]);contacts.append({'xy':[x,y],'post_bottom':foot,'floor':ff});ck('Original post base meets kitchen floor / '+str(y),foot is not None and ff is not None and abs(foot[2]-ff[2])<.003)
 wallhit=ray(outer_wall,[x,y,1],[1,0,0],.5);ck('Post follows the outer wall inner side / '+str(y),wallhit is not None and .065<wallhit[0]-x<.19,axis_xy=[x,y],wall_hit=wallhit)
for y in np.arange(-8.1,-3.0,.4):
 x=13.245+(y+8.276)*(.714/4.994)-.012;h=ray(floor,[x,y,0],[0,0,-1]);ck('Curved wall foot has continuous floor / '+str(round(y,2)),h is not None and abs(h[2]+.400024)<.002,xy=[float(x),float(y)],hit=h)
wall=bpy.data.objects['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'];count=0;bad=0
for face in wall.data.polygons:
 c=wall.matrix_world@face.center;normal=wall.matrix_world.to_3x3()@face.normal
 if -11.6<c.y<-3.2 and c.x>12.7 and normal.x<-.5 and c.z>.05:
  count+=1;bad+=wall.data.materials[face.material_index].name!='M_V24_11_Plain_White_Limewash'
ck('Kitchen inside wall is white',count>5 and bad==0,faces=count,wrong_finish=bad)

tr=tree(bpy.data.objects['PARTITIONS_JOINED_F1_Geometry']);infill=tree(bpy.data.objects['HOUSE_V20_F1_PHOTO_MISSING_INFILL_WALLS_Geometry'])
for y in [7.65,8.5,9.1,9.70]:
 h=ray(tr,[9.3,y,1],[1,0,0],3.3);ck('Blue-line partition divides both zones / '+str(y),h is not None and abs(h[0]-10.6)<.003,hit=h)
for y in [7.65,8.05,8.45,9.52]:
 h=ray(tr,[8.5,y,1],[1,0,0],1.0);ck('Stair-facing WC boundary closed / '+str(y),h is not None and abs(h[0]-9.0)<.003)
for y in [8.72,9.0,9.28]:
 ck('Stair-facing original WC doorway retained / '+str(y),ray(tr,[8.5,y,1],[1,0,0],1.0)is None)
ck('Old bathroom doorway sealed',ray(tr,[12.3,7.,1],[0,1,0],.6)is not None)
for x in [10.82,11.1,11.38]:
 ck('New bathroom opening cut through both wall meshes / '+str(x),ray(tr,[x,7.,1],[0,1,0],.6)is None and ray(infill,[x,7.,1],[0,1,0],.6)is None)
ck('Stair entrance passage remains clear',ray(tr,[8.45,7.5,1],[0,1,0],1.7)is None)
frame=bpy.data.objects['DOOR_BATH_F1_R__FRAME_Geometry'];v=coords(frame);ck('Bathroom red frame shifted 1.2m left',abs(v[:,0].min()-10.7)<3e-5 and abs(v[:,0].max()-11.5)<3e-5)
for n in prep['proof']['drainage']['removed']:
 ck('Obsolete drainage object removed / '+n,n not in bpy.data.objects)
for n in ['V24_08_Kitchen_Corrugated_Exhaust_Elbow','V24_08_Kitchen_Open_Round_Flue']:
 ck('Functional exhaust retained / '+n,n in bpy.data.objects and before['objects'][n]['mesh_hash']==after['objects'][n]['mesh_hash'])

for n in prep['proof']['perimeter_finish']['walls']:
 o=bpy.data.objects[n];ck('Both perimeter walls use the preferred shared photo / '+n,[m.name for m in o.data.materials]==['M_V24_20_Continuous_AsBuilt_Perimeter']);ck('Finish division is a continuous vertex field / '+n,o.data.attributes.get('V24_20_Height_Above_Finish_Division')is not None);uv=o.data.uv_layers.active;v=coords(o);maxerr=0.;ratios=[]
 for f in o.data.polygons:
  t=v[list(f.vertices)];q=np.array([uv.data[li].uv[:]for li in f.loop_indices])
  nn=np.cross(t[1]-t[0],t[2]-t[0]);ll=np.linalg.norm(nn)
  if ll<1e-10 or abs(nn[2])/ll>.85:continue
  maxerr=max(maxerr,float(abs(q[:,1]-t[:,2]).max()))
  for a,b in [(0,1),(1,2),(2,0)]:
   L=np.linalg.norm(t[b,:2]-t[a,:2])
   if L>.1 and abs(t[b,2]-t[a,2])<2e-5:ratios.append(abs(q[b,0]-q[a,0])/L)
 ck('Photo UV vertical metre scale / '+n,maxerr<3e-5,error_m=maxerr)
 ck('Photo UV horizontal metre scale / '+n,len(ratios)>10 and max(abs(r-1)for r in ratios)<.015,minimum=min(ratios),maximum=max(ratios))
 old=np.load(D/idx[n]['file']);bt=BVHTree.FromPolygons([Vector(p)for p in old['v']],old['f'].tolist(),all_triangles=True);err=max(bt.find_nearest(Vector(p))[3]for p in v);ck('Restored closed wall exterior remains within 1mm of original surfaces / '+n,err<.001,maximum_surface_distance_m=err)
for tag in ['main','kitchen']:
 for n in prep['proof']['roof_tiles'][tag]['objects']:
  o=bpy.data.objects[n];ck('Unified roof clay material / '+n,[m.name for m in o.data.materials]==['M_V24_20_Unified_Weathered_Gray_Clay'])
o=bpy.data.objects['SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry'];ck('Storage tiles share the new clay material',o.data.materials[0].name=='M_V24_20_Unified_Weathered_Gray_Clay')
joint=prep['proof']['two_room_roof_junction'];bedtree=tree(bpy.data.objects[joint['bed_object']]);kp=np.array(joint['kitchen_plane']);sp=np.array(joint['storage_plane']);df=kp-sp;normal=df[:2]/np.linalg.norm(df[:2])
for y in [-11.4,-11.0,-10.6,-9.7,-9.2,-8.85]:
 x=-(df[1]*y+df[2])/df[0];p=np.array([x,y]);centre=ray(bedtree,[x,y,6],[0,0,-1]);expect=float(kp@np.array([x,y,1.]));ck('Continuous roof bed at diagonal valley / '+str(y),centre is not None and abs(centre[2]-expect)<.003,hit=centre,expected_z=expect)
 if centre is not None:
  hs=[ray(bedtree,[*(p+normal*t),6],[0,0,-1])for t in [-.12,.12]];ck('Both roof slopes rise from the concave seam / '+str(y),all(h is not None and h[2]>centre[2]+.02 for h in hs),hits=hs)
ck('All image textures embedded',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))

exports=[]
names={r['name']for r in prep['objects']}|set(prep['proof']['perimeter_finish']['walls'])|{'V24_Kitchen_Gable_Upper_Brick_Infill','V24_03_Kitchen_Rear_Gable_Wall','SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry'}
for n in sorted(names):
 o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();fn=f'SAVED_{len(exports):03d}.npz';v=coords(o);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);np.savez_compressed(D/fn,v=v,f=f,mi=mi);exports.append({'name':n,'file':fn,'materials':[m.name for m in me.materials]})
for row in prep['objects']:
 v=coords(bpy.data.objects[row['name']]);expected=np.array(row['v']);ck('Prepared mesh bounds retained / '+row['name'],np.max(abs(v.min(0)-expected.min(0)))<3e-5 and np.max(abs(v.max(0)-expected.max(0)))<3e-5)
 ck('All prepared vertex positions survive native save / '+row['name'],len(v)==len(expected)and np.max(np.linalg.norm(v-expected,axis=1))<3e-5,maximum_vertex_error_m=float(np.max(np.linalg.norm(v-expected,axis=1)))if len(v)==len(expected)else None)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Solid_Export_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2));fail=[r for r in checks if not r['pass']];(R/'V24_20_Fresh_Native_QA.json').write_text(json.dumps({'status':'PASS_FRESH_NATIVE_QA'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail,'post_floor_contacts':contacts},ensure_ascii=False,indent=2),encoding='utf8');print('V20_NATIVE_QA',len(checks),'FAIL',len(fail),flush=True)
for r in fail:print('FAIL',r,flush=True)
