import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_17';O=Path('E:/jz/JIA/Rebuild_V24_17');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_17.blend';checks=[]
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;before=json.loads((R/'V24_17_Before_Snapshot.json').read_text());after=json.loads(json.dumps(snapshot(bpy)));ch=json.loads((R/'V24_17_Changes.json').read_text());allow=set(ch['changed']);gone=set(ch['removed']);added=set(ch['added']);sc.frame_set(40);bpy.context.view_layer.update()
ck('Only recorded redundant/detail objects removed',set(before['objects'])-set(after['objects'])==gone);ck('Only recorded objects added',set(after['objects'])-set(before['objects'])==added)
for n,a in before['objects'].items():
 if n in gone:continue
 b=after['objects'][n]
 for k in ['type','parent','hide_render','animation','matrix']:ck('Preserved '+k+' / '+n,a[k]==b[k])
 if n not in allow:ck('Unchanged mesh UV and surface slots / '+n,a['mesh_hash']==b['mesh_hash'])
for n,a in before['materials'].items():ck('Original shader preserved / '+n,after['materials'].get(n)==a)
for n,a in before['images'].items():ck('Original packed texture preserved / '+n,after['images'].get(n)==a)
ck('All 26 door actions and three sampled poses unchanged',before['actions']==after['actions']and before['doors']==after['doors']and before['door_poses']==after['door_poses']and len(after['doors'])==26)
ck('All file textures embedded',all(im.packed_file for im in bpy.data.images if im.source=='FILE'))
for n in ['SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry','V24_11_Storage_Veranda_Column_1','V24_11_Storage_Veranda_Column_2','V24_11_Storage_Veranda_Column_Base_1','V24_11_Storage_Veranda_Column_Base_2','V24_16_Storage_Entrance_White_Wall_Return','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry','SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry']:
 ck('Accepted foundation entry or wall retained / '+n,before['objects'][n]==after['objects'][n])
ck('Crossed-out projecting plinth removed',not bpy.data.objects.get('V24_11_Screenwall_Continuous_Stepped_Stone_Plinth'));ck('Crossed-out diagonal roof adapter removed',not bpy.data.objects.get('SITE_V14_KITCHEN_STORAGE_DIAGONAL_VALLEY_Geometry'))
ck('Entrance tin canopy remains removed',not any(n in bpy.data.objects for n in ['V24_10_Entry_Metal_Canopy_Sheet','V24_10_Entry_Canopy_Attached_Frame']))
def coords(o):
 a=np.empty(len(o.data.vertices)*3,np.float32);o.data.vertices.foreach_get('co',a);a=a.reshape(-1,3).astype(np.float64);T=np.asarray(o.matrix_world);return a@T[:3,:3].T+T[:3,3]
for side,outer in [('West',13.205),('East',18.685)]:
 o=bpy.data.objects['V24_14_Storage_'+side+'_Sealed_Gable'];v=coords(o);ck('Enlarged integral storage ear / '+side,v[:,2].max()>5.15 and v[:,2].max()<5.50,peak_z=float(v[:,2].max()));ck('Exterior gable has blue brick material / '+side,any('Blue_Brick'in m.name for m in o.data.materials));ck('Inner gable white finish / '+side,'V24_17_Storage_'+side+'_Inner_Gable_Limewash'in bpy.data.objects)
# The local retirement preserves every triangle outside the old secondary cap.
n='SITE_PERIMETER_JOINED_RETAINING_WALL_0_TILE_COPING_Geometry';o=bpy.data.objects[n];me=o.data;v=coords(o);vi=np.empty(len(me.loops),np.int32);me.loops.foreach_get('vertex_index',vi);f=vi.reshape(-1,3);q=v[f].mean(1);bad=(q[:,0]>10.79)&(q[:,0]<13.18)&(q[:,1]>-17.20)&(q[:,1]<-16.18)&(q[:,2]>2.47)&(q[:,2]<2.85);ret=json.loads((R/'V24_17_Retired_Coping.json').read_text());raw=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',raw);T=np.asarray(o.matrix_world);vh=raw.reshape(-1,3)@T[:3,:3].T+T[:3,3];h=hashlib.sha256(np.round(vh[f],6).tobytes()).hexdigest();ck('No old secondary coping left to overlap the new roof',not bad.any(),retired_faces=ret['retired_secondary_faces']);ck('All other original perimeter coping triangles preserved',h==ret['outside_triangle_signature_sha256'],hash_coordinate_dtype=str(vh.dtype))
exports=[];obs={r['name']for r in json.loads((W/'v24_11/QA_Obstacle_Index.json').read_text())};names=(allow|added|obs|{'V24_16_Storage_Entrance_White_Wall_Return','V24_11_Storage_Curved_Rear_Interior_White_Finish','SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry','V24_15_Storage_Seven_Round_Purlin_Rows','SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES_Geometry'})-gone-{n}
for name in sorted(names):
 o=bpy.data.objects.get(name)
 if not o or o.type!='MESH':continue
 o.data.calc_loop_triangles();v=coords(o);f=np.array([t.vertices[:]for t in o.data.loop_triangles]);fn=f'SAVED_{len(exports):03d}.npz';np.savez_compressed(D/fn,v=v,f=f);exports.append({'name':name,'file':fn,'changed':name in allow or name in added,'obstacle':name in obs or name in added})
mh=sha(P);(D/'Solid_Export_Index.json').write_text(json.dumps({'model_sha256':mh,'objects':exports},indent=2));build=json.loads((R/'V24_17_Build.json').read_text());ck('Final model hash matches saved build',mh==build['sha256']);ck('Source V24.16 preserved',sha(build['source'])==build['source_sha256']);fail=[r for r in checks if not r['pass']];out={'status':'PASS_FRESH_NATIVE_QA'if not fail else'FAIL_FRESH_NATIVE_QA','model_sha256':mh,'checks':checks,'failures':fail};(R/'V24_17_Fresh_Blend_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(out['status'],len(checks),len(fail),flush=True)
for r in fail:print('FAIL',r,flush=True)
