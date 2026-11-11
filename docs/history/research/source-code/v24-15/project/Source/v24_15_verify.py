import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_15';O=Path('E:/jz/JIA/Rebuild_V24_15');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_15.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def tree(n):
 o=bpy.data.objects[n];return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices)for f in o.data.polygons])
checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;after=json.loads(json.dumps(snapshot(bpy)));before=json.loads((R/'V24_15_Before_Snapshot.json').read_text());ch=json.loads((R/'V24_15_Changes.json').read_text());allow=set(ch['changed']);deleted=set(ch['removed'])
ck('Only obsolete haunch group removed',set(before['objects'])-set(after['objects'])==deleted)
ck('Only recorded objects added',set(after['objects'])-set(before['objects'])==set(ch['added']))
for n,a in before['objects'].items():
 if n in deleted:continue
 b=after['objects'][n]
 for k in ['type','parent','hide_render','animation','matrix']:ck('Preserved '+k+' / '+n,a[k]==b[k])
 if n not in allow:ck('Unchanged mesh and UV / '+n,a['mesh_hash']==b['mesh_hash'])
for n,a in before['materials'].items():ck('Original shader / '+n,after['materials'].get(n)==a)
for n,a in before['images'].items():ck('Original packed image / '+n,after['images'].get(n)==a)
ck('All 26 door actions and poses unchanged',before['actions']==after['actions']and before['doors']==after['doors']and before['door_poses']==after['door_poses']and len(after['doors'])==26)
ck('All file textures remain embedded',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
sc.frame_set(40);bpy.context.view_layer.update()
for n in ['SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry','SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry','SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry','V24_14_Storage_West_Sealed_Gable','V24_14_Storage_East_Sealed_Gable','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry','SITE_V18_OUTER_STORAGE_THIN_METAL_CANOPY_Geometry','V24_11_Screenwall_Continuous_Stepped_Stone_Plinth','V24_14_Secondary_Screenwall_Volute_End','SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','DOOR_STORAGE_V20_L__LEAF','DOOR_STORAGE_V20_R__LEAF']:
 ck('Accepted roof/site/door feature retained / '+n,before['objects'][n]==after['objects'][n])
ck('Deleted entrance canopy not restored',not any(n in bpy.data.objects for n in ['V24_10_Entry_Metal_Canopy_Sheet','V24_10_Entry_Canopy_Attached_Frame']))
cols=[o for o in bpy.data.objects if o.name.startswith('V24_11_Storage_Veranda_Column_')and'_Base_'not in o.name];ck('Exactly two veranda round posts',len(cols)==2);axes=[]
for o in cols:
 v=np.array([o.matrix_world@p.co for p in o.data.vertices]);lo=v[v[:,2]<v[:,2].min()+.001,:2].mean(0);hi=v[v[:,2]>v[:,2].max()-.001,:2].mean(0);axes.append(lo);ck('Vertical column with seated top / '+o.name,np.linalg.norm(hi-lo)<2e-5 and abs(v[:,2].max()-2.89)<2e-5,head_z=float(v[:,2].max()))
ck('Oblique column line preserved',abs(np.degrees(np.arctan2(*(axes[1]-axes[0])[::-1]))+11.82)<.15)
gt=tree('V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails');tops=[]
for t in np.linspace(.07,.93,19):
 xy=axes[0]*(1-t)+axes[1]*t;p=gt.ray_cast(Vector((*xy,3.1)),Vector((0,0,-1)),1)[0];tops.append(p.z if p else 99)
ck('Veranda tie top is horizontal and seated over posts',max(abs(z-2.905)for z in tops)<2e-5,z_range_m=[min(tops),max(tops)])
o=bpy.data.objects['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry'];v=np.array([o.matrix_world@p.co for p in o.data.vertices]);bay=v[(v[:,0]>13.536)&(v[:,0]<18.42)];ck('No upper legacy beam fragments remain in room bay',len(bay)>0 and bay[:,2].max()<=1.82001,maximum_retained_original_bay_z=float(bay[:,2].max()))
proof=json.loads((R/'V24_15_Corrections.json').read_text());ck('Four upper transom panels follow photo',proof['front_transom']['four_octagon_panels']==4);ck('Dense round rafters built on both slopes',proof['rafters']['round_members']==62 and abs(proof['rafters']['pitch_m']-.158)<1e-8)
# Read back actual meshes, including unchanged route obstacles and roof shell.
exports=[];obs={r['name']for r in json.loads((W/'v24_11/QA_Obstacle_Index.json').read_text())};names=allow|set(ch['added'])|obs|{'SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry','V24_14_Storage_West_Sealed_Gable','V24_14_Storage_East_Sealed_Gable'}
for n in sorted(names):
 o=bpy.data.objects.get(n)
 if not o or o.type!='MESH':continue
 me=o.data;me.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in me.vertices]);f=np.array([t.vertices[:]for t in me.loop_triangles]);fn=f'SAVED_{len(exports):02d}.npz';np.savez_compressed(D/fn,v=v,f=f);exports.append({'name':n,'file':fn,'changed':n in allow or n in ch['added'],'obstacle':n in obs or n in ch['added']})
h=sha(P);(D/'Solid_Export_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2),encoding='utf8');build=json.loads((R/'V24_15_Build.json').read_text());ck('Final saved SHA256 matches build',h==build['sha256']);ck('Source V24.14 unchanged',sha(build['source'])==build['source_sha256']);fail=[r for r in checks if not r['pass']];out={'status':'PASS_FRESH_NATIVE_QA'if not fail else'FAIL_FRESH_NATIVE_QA','model_sha256':h,'checks':checks,'failures':fail};(R/'V24_15_Fresh_Blend_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out['status'],len(checks),len(fail),flush=True)
for r in fail:print('FAIL',json.dumps(r,ensure_ascii=False),flush=True)
