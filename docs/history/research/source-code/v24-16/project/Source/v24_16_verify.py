import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_16';O=Path('E:/jz/JIA/Rebuild_V24_16');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_16.blend'
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
bpy.ops.wm.open_mainfile(filepath=str(P));after=json.loads(json.dumps(snapshot(bpy)));before=json.loads((R/'V24_16_Before_Snapshot.json').read_text());ch=json.loads((R/'V24_16_Changes.json').read_text());allow=set(ch['changed']);sc=bpy.context.scene;sc.frame_set(40);bpy.context.view_layer.update()
ck('No objects deleted',set(before['objects'])<=set(after['objects']));ck('Only recorded objects added',set(after['objects'])-set(before['objects'])==set(ch['added']))
for n,a in before['objects'].items():
 b=after['objects'][n]
 for k in ['type','parent','hide_render','animation','matrix']:ck('Preserved '+k+' / '+n,a[k]==b[k])
 if n not in allow:ck('Unchanged mesh UV and materials / '+n,a['mesh_hash']==b['mesh_hash'])
for n,a in before['materials'].items():ck('Original shader / '+n,after['materials'].get(n)==a)
for n,a in before['images'].items():ck('Original packed image / '+n,after['images'].get(n)==a)
ck('All 26 door actions and three sampled poses unchanged',before['actions']==after['actions']and before['doors']==after['doors']and before['door_poses']==after['door_poses']and len(after['doors'])==26)
ck('All file textures embedded',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
def coords(n):
 o=bpy.data.objects[n];return np.array([o.matrix_world@v.co for v in o.data.vertices])
cols=[o for o in bpy.data.objects if o.name.startswith('V24_11_Storage_Veranda_Column_')and'_Base_'not in o.name];ck('Exactly two veranda round posts',len(cols)==2);axes=[]
for o in sorted(cols,key=lambda o:o.name):
 v=coords(o.name);lo=v[v[:,2]<v[:,2].min()+.001,:2].mean(0);hi=v[v[:,2]>v[:,2].max()-.001,:2].mean(0);axes.append(lo);ck('Vertical column / '+o.name,np.linalg.norm(hi-lo)<2e-5 and abs(v[:,2].max()-2.89)<2e-5)
ck('Entrance post moved outward with white side return',np.linalg.norm(axes[0]-[13.72,-15.22])<2e-5 and 'V24_16_Storage_Entrance_White_Wall_Return'in bpy.data.objects,axis=axes[0].tolist())
ck('Far post axis retained',np.linalg.norm(axes[1]-[18.26,-15.60])<2e-5)
o=bpy.data.objects['V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails'];tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices)for f in o.data.polygons]);tops=[]
for t in np.linspace(.04,.96,25):
 xy=axes[0]*(1-t)+axes[1]*t;pt=tree.ray_cast(Vector((*xy,3.1)),Vector((0,0,-1)),1)[0];tops.append(pt.z if pt else 99)
ck('Reconnected veranda beam remains level over both posts',max(abs(z-2.905)for z in tops)<2e-5,z_range=[min(tops),max(tops)])
inventory={r['name']:r for r in json.loads((D/'Inventory.json').read_text())}
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry']:
 old=np.load(D/inventory[n]['file'])['v'];v=coords(n);ck('Wall plan unchanged / '+n,np.allclose(old[:,:2],v[:,:2],atol=1e-7,rtol=0));mask=old[:,2]<=2.65;ck('Lower wall geometry unchanged / '+n,np.allclose(old[mask],v[mask],atol=1e-7,rtol=0))
ck('Entrance metal canopy remains removed',not any(n in bpy.data.objects for n in ['V24_10_Entry_Metal_Canopy_Sheet','V24_10_Entry_Canopy_Attached_Frame']))
proof=json.loads((R/'V24_16_Corrections.json').read_text());ck('Screen ridge has four branching hips and tiles in both end fans',proof['screen']['fork_arms']==4 and proof['screen']['fan_barrel_tiles']>0 and proof['screen']['fork_junction_x'][0]>3.75 and proof['screen']['fork_junction_x'][1]<10.3)
ck('Photo-fitted geometry not labelled as structural calculation',proof['scope']['bearing_checks_are_geometric_not_structural_calculations'])
# Export the actual reopened native meshes for the independent geometry test.
obs={r['name']for r in json.loads((W/'v24_11/QA_Obstacle_Index.json').read_text())};names=set(inventory)|obs|set(ch['added']);exports=[]
for n in sorted(names):
 o=bpy.data.objects.get(n)
 if not o or o.type!='MESH':continue
 me=o.data;me.calc_loop_triangles();v=coords(n);f=np.array([t.vertices[:]for t in me.loop_triangles]);fn=f'SAVED_{len(exports):03d}.npz';np.savez_compressed(D/fn,v=v,f=f);exports.append({'name':n,'file':fn,'changed':n in allow or n in ch['added'],'obstacle':n in obs or n=='V24_16_Storage_Entrance_White_Wall_Return'})
h=sha(P);(D/'Solid_Export_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2));build=json.loads((R/'V24_16_Build.json').read_text());ck('Final model hash matches',h==build['sha256']);ck('Source V24.15 preserved',sha(build['source'])==build['source_sha256']);fail=[r for r in checks if not r['pass']];out={'status':'PASS_FRESH_NATIVE_QA'if not fail else'FAIL_FRESH_NATIVE_QA','model_sha256':h,'checks':checks,'failures':fail};(R/'V24_16_Fresh_Blend_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(out['status'],len(checks),len(fail),flush=True)
for r in fail:print('FAIL',r,flush=True)
