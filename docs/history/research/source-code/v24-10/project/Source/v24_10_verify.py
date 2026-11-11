import bpy,sys,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
from v24_03_junction_blender import _closed_stats,_bounds
O=Path('E:/jz/JIA/Rebuild_V24_10');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_10.blend';B=Path('E:/jz/JIA/Rebuild_V24_09/Blender/Architecture_Complete_V24_09.blend');D=W/'v24_10'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
checks=[]
def ck(n,p,**data):checks.append({'check':n,'pass':bool(p),**data})
bpy.ops.wm.open_mainfile(filepath=str(B));before=snapshot(bpy)
bpy.ops.wm.open_mainfile(filepath=str(P));after=snapshot(bpy);sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
change=json.loads((R/'V24_10_Changes.json').read_text());proof=json.loads((R/'V24_10_AsBuilt_Storage_and_Entry.json').read_text());build=json.loads((R/'V24_10_Build.json').read_text())
allowed={r['name']for r in change['changed']}|{r['root']for r in proof['moving_storage_doors']};gone=set(change['removed']);new=set(change['added'])
ck('No unrelated objects removed',set(before['objects'])-set(after['objects'])==gone)
ck('No unrecorded new objects',set(after['objects'])-set(before['objects'])==new)
for n,a in before['objects'].items():
 if n in gone:continue
 b=after['objects'][n]
 for key in['type','parent','hide_render','animation']:ck('Preserved '+key+' / '+n,a[key]==b[key])
 if n not in allowed:
  for key in['mesh_hash','matrix']:ck('Unchanged '+key+' / '+n,a[key]==b[key])
for n,v in before['materials'].items():ck('Original shader / '+n,after['materials'].get(n)==v)
for n,v in before['images'].items():ck('Original image / '+n,after['images'].get(n)==v)
ck('All original door actions identical',after['actions']==before['actions']);ck('26 moving doors remain',after['doors']==before['doors']and len(after['doors'])==26)
store={r['root']for r in proof['moving_storage_doors']}
for f,poses in before['door_poses'].items():
 for n,m in poses.items():
  if n not in store:ck('Other door pose '+f+' / '+n,after['door_poses'][f][n]==m)
ck('Two fitted storage hinge roots retained',len(store)==2)
stats={};solid_exports=[];solid_report_path=R/'V24_10_Independent_Solid_QA.json';solid_report=json.loads(solid_report_path.read_text())if solid_report_path.is_file()else{};solid_rows={r['name']:r for r in solid_report.get('solids',[])}if solid_report.get('model_sha256')==sha(P)else{}
for n in(sorted(allowed|new)):
 o=bpy.data.objects.get(n)
 if not o or o.type!='MESH'or n.startswith('SITE_V14_ORIGINAL_EXTERIOR_'):continue
 s=_closed_stats(o);stats[n]=s
 o.data.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in o.data.vertices]);f=np.array([list(t.vertices)for t in o.data.loop_triangles]);mi=np.array([o.data.polygons[t.polygon_index].material_index for t in o.data.loop_triangles]);uv=o.data.uv_layers.active;lu=np.array([[tuple(uv.data[i].uv)for i in t.loops]for t in o.data.loop_triangles])if uv else np.zeros((len(f),3,2));fn='SOLID_'+str(len(solid_exports)).zfill(2)+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=lu);solid_exports.append({'name':n,'file':fn,'materials':[m.name for m in o.data.materials]})
 indep=solid_rows.get(n,{});raw=s['boundary_edges']==0 and s['nonmanifold_edges']==0 and s['volume_m3']>1e-9
 ck('Closed solid / '+n,raw or indep.get('pass',False),native_topology=s,independent_solid_status=indep.get('status'),normalization_precision_m=indep.get('coordinate_precision_m'))
(D/'Solid_Export_Index.json').write_text(json.dumps({'model_sha256':sha(P),'objects':solid_exports},indent=2),encoding='utf8')
ck('Old low south eave extension completely removed',all(n not in bpy.data.objects for n in['SITE_V20_STORAGE_SOUTH_EAVE_CONTINUATION_Geometry','SITE_V20_STORAGE_SOUTH_EAVE_TILE_COURSES_Geometry','SITE_V20_STORAGE_SOUTH_EAVE_TIMBER_CONTINUATION_Geometry','SITE_V20_STORAGE_ALIGNED_STONE_BASE_EXTENSION_Geometry']))
base=bpy.data.objects['SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry'];tree=BVHTree.FromPolygons([base.matrix_world@v.co for v in base.data.vertices],[list(p.vertices)for p in base.data.polygons]);points=[]
for r in proof['drain']:
 for t in[.12,.37,.62,.87]:
  p=Vector((r['a'][0]*(1-t)+r['b'][0]*t,r['a'][1]*(1-t)+r['b'][1]*t,-.8));hit=tree.find_nearest(p);points.append(hit[3]if hit[0]else 99)
ck('New plinth face follows source 3dm section',max(points)<.004,maximum_face_distance_m=max(points))
ck('New plot is reduced from the former model',proof['plot']['area_m2']<proof['plot']['old_local_storage_plinth_approx_area_m2']-8,new_area_m2=proof['plot']['area_m2'],former_approx_area_m2=proof['plot']['old_local_storage_plinth_approx_area_m2'])
ck('One continuous fitted retaining base',proof['base']['connected_bodies']==1)
ck('Seven guard bays and fourteen real openings',len(proof['guard_bays'])==7 and sum(x['openings']for x in proof['guard_bays'])==14)
# Physical guard apertures have empty ray paths through the band.
o=bpy.data.objects['SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry'];tr=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons]);empty=[]
for r in proof['guard_bays']:
 for t in[.27,.73]:
  a=Vector((*r['a'],.35));b=Vector((*r['b'],.35));p=a*(1-t)+b*t;no=Vector((*r['normal'],0));hit=tr.ray_cast(p-no*.18,no,.36)[0];empty.append(hit is None)
ck('All 14 stone guard openings are clear',all(empty),clear_openings=sum(empty))
# Export real saved solids for independent manifold collision measurement.
names=['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry','SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry','SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES_Geometry','SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry','DOOR_STORAGE_V20_L__LEAF_Geometry','DOOR_STORAGE_V20_R__LEAF_Geometry','V24_10_Entry_Metal_Canopy_Sheet','V24_10_Entry_Canopy_Attached_Frame']
rows=[]
for i,n in enumerate(names):
 o=bpy.data.objects[n];o.data.calc_loop_triangles();v=np.array([o.matrix_world@p.co for p in o.data.vertices]);f=np.array([list(p.vertices)for p in o.data.loop_triangles]);fn=f'QA_Obstacle_{i:02d}.npz';np.savez_compressed(D/fn,v=v,f=f);rows.append({'name':n,'file':fn})
(D/'QA_Obstacle_Index.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
ck('Source model SHA retained',sha(B)==build['source_sha256']);ck('Saved model SHA matches build',sha(P)==build['sha256']);ck('Original as-built 3dm unchanged',sha('E:/jz/实景三维场景模型.3dm')==proof['source_3dm'])
ck('All saved photographic images packed',all(im.packed_file for im in bpy.data.images if im.source=='FILE'))
fail=[x for x in checks if not x['pass']];out={'status':'PASS_V24_10_FRESH_BLEND_QA'if not fail else'FAIL_V24_10_FRESH_BLEND_QA','checks':checks,'failures':fail,'model_sha256':sha(P),'geometry_stats':stats,'original_materials':len(before['materials']),'original_images':len(before['images'])};(R/'V24_10_Fresh_Blend_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out['status'],len(checks),len(fail),flush=True)
for x in fail:print('FAIL',json.dumps(x,ensure_ascii=False),flush=True)
