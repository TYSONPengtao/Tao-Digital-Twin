import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
from v24_13_geometry import roof_z,ridge,front,rear,W as RW,E as RE
D=W/'v24_14';O=Path('E:/jz/JIA/Rebuild_V24_14');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_14.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def tree(n):
 o=bpy.data.objects[n];return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices)for f in o.data.polygons])
checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;after=json.loads(json.dumps(snapshot(bpy)));before=json.loads((R/'V24_14_Before_Snapshot.json').read_text());ch=json.loads((R/'V24_14_Changes.json').read_text());allow=set(ch['changed']);deleted=set(ch['removed']);moved={'SITE_V17_STORAGE_VERANDA_TIMBER_ENTRY_FRONT_Geometry','DOOR_STORAGE_V20_L__LEAF','DOOR_STORAGE_V20_R__LEAF','DOOR_STORAGE_V20_L__LEAF_Geometry','DOOR_STORAGE_V20_R__LEAF_Geometry'}
ck('Only the two erroneous return objects removed',set(before['objects'])-set(after['objects'])==deleted)
ck('Only recorded objects added',set(after['objects'])-set(before['objects'])==set(ch['added']))
postmoves={'V24_11_Storage_Veranda_Column_1','V24_11_Storage_Veranda_Column_Base_1'}
for n,a in before['objects'].items():
 if n in deleted:continue
 b=after['objects'][n]
 for k in ['type','parent','hide_render','animation']:ck('Preserved '+k+' / '+n,a[k]==b[k])
 if n in postmoves:
  expect=np.array(a['matrix']);expect[0,3]+=.30;ck('Entry round post freed from gable / '+n,np.max(abs(expect-np.array(b['matrix'])))<3e-6)
 elif n not in moved:ck('Unchanged transform / '+n,a['matrix']==b['matrix'])
 else:
  expect=np.array(a['matrix']);expect[1,3]+=.48;ck('Coherent facade setback / '+n,np.max(abs(expect-np.array(b['matrix'])))<3e-6)
 if n not in allow:ck('Unchanged mesh and UV / '+n,a['mesh_hash']==b['mesh_hash'])
for n,a in before['materials'].items():ck('Original shader / '+n,after['materials'].get(n)==a)
for n,a in before['images'].items():ck('Original packed image / '+n,after['images'].get(n)==a)
ck('All 26 door actions unchanged',before['actions']==after['actions']and before['doors']==after['doors']and len(after['doors'])==26)
for f,poses in before['door_poses'].items():
 for n,a in poses.items():
  expect=np.array(a)
  if n.startswith('DOOR_STORAGE_V20_'):expect[1,3]+=.48
  ck('Door pose '+n+' frame '+f,np.max(abs(expect-np.array(after['door_poses'][f][n])))<3e-6)
ck('All file textures remain embedded',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
sc.frame_set(40);bpy.context.view_layer.update();rt=tree('SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry');err=[]
for x in np.linspace(13.40,18.60,17):
 for y in [front(x)+.006,ridge(x),-14.0,ridge(x)+.30]:
  p=rt.ray_cast(Vector((x,y,7)),Vector((0,0,-1)),10)[0];err.append(abs(p.z-roof_z(x,y))if p else 99)
ck('Accepted rectangular roof and level two planes retained',max(err)<2e-5,maximum_plane_error_m=max(err))
fy=lambda x:-17.00174904+(x-10.8)*(-16.773484324+17.00174904)/(13.13-10.8)
wt=tree('SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry');levels=[]
for x in np.linspace(10.84,13.10,24):
 p=wt.ray_cast(Vector((x,fy(x)+.14,3.2)),Vector((0,0,-1)),2)[0];levels.append(p.z if p else 99)
ck('Secondary straight wall crown remains level',max(abs(z-2.610)for z in levels)<2e-5,range_m=[min(levels),max(levels)])
for n in ['V24_10_Secondary_Screenwall_Closed_Panel_Band','V24_10_Secondary_Screenwall_Panel_Mouldings','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry','SITE_V18_OUTER_STORAGE_THIN_METAL_CANOPY_Geometry','SITE_SOUTH_SCREENWALL_V12_STEPPED_MASONRY_UNDEREAVE_Geometry','V24_11_Screenwall_Continuous_Stepped_Stone_Plinth']:
 ck('Prior accepted geometry retained / '+n,before['objects'][n]==after['objects'][n])
ck('Deleted entrance canopy not reintroduced',not any(n in bpy.data.objects for n in ['V24_10_Entry_Metal_Canopy_Sheet','V24_10_Entry_Canopy_Attached_Frame']))
cols=[o for o in bpy.data.objects if o.name.startswith('V24_11_Storage_Veranda_Column_')and'_Base_'not in o.name];ck('Exactly two round veranda columns',len(cols)==2);axes=[]
for o in cols:
 v=np.array([o.matrix_world@p.co for p in o.data.vertices]);lo=v[v[:,2]<v[:,2].min()+.001,:2].mean(0);hi=v[v[:,2]>v[:,2].max()-.001,:2].mean(0);axes.append(lo);ck('Vertical round post '+o.name,np.linalg.norm(hi-lo)<2e-5)
angle=np.degrees(np.arctan2(*(axes[1]-axes[0])[::-1]));ck('Post line remains oblique to railing',abs(angle+11.82)<.15,angle_deg=float(angle))
gb=[]
for side,x in [('West',13.205),('East',18.685)]:
 t=tree('V24_14_Storage_'+side+'_Sealed_Gable');sg=1 if side=='West'else-1
 for y in [-15.9,-15,-14,-13,-12.15,-11.5]:
  for z in [2.57,roof_z(x,y)-.12]:
   hit=t.ray_cast(Vector((x-sg*.2,y,z)),Vector((sg,0,0)),.8)[0];gb.append(hit is not None)
ck('Sealed gables cover roof beam end zone',all(gb),samples=len(gb))
# Actual saved changed solids and route obstacles are exported independently.
exports=[];obsnames={r['name']for r in json.loads((W/'v24_11/QA_Obstacle_Index.json').read_text())};target=set(ch['changed'])|set(ch['added'])|obsnames|{'SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry'}
for n in sorted(target):
 o=bpy.data.objects.get(n)
 if not o or o.type!='MESH':continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);fn=f'SAVED_{len(exports):02d}.npz';np.savez_compressed(D/fn,v=v,f=f);exports.append({'name':n,'file':fn,'changed':n in allow or n in ch['added'],'obstacle':n in obsnames or n in ch['added']})
h=sha(P);(D/'Solid_Export_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2),encoding='utf8');build=json.loads((R/'V24_14_Build.json').read_text());ck('Final saved SHA256 matches build',h==build['sha256']);ck('Source V24.13 unchanged',sha(build['source'])==build['source_sha256']);fail=[r for r in checks if not r['pass']];out={'status':'PASS_FRESH_NATIVE_QA'if not fail else'FAIL_FRESH_NATIVE_QA','model_sha256':h,'checks':checks,'failures':fail};(R/'V24_14_Fresh_Blend_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out['status'],len(checks),len(fail),flush=True)
for r in fail:print('FAIL',json.dumps(r,ensure_ascii=False),flush=True)
