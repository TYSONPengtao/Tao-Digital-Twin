import bpy,sys,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W0=Path(__file__).parent;sys.path.insert(0,str(W0));from v24_06_common import snapshot
from v24_13_geometry import ridge,front,rear,roof_z,RIDGE_Z,EAVE_Z,W,E
D=W0/'v24_13';O=Path('E:/jz/JIA/Rebuild_V24_13');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_13.blend';B=Path('E:/jz/JIA/Rebuild_V24_12/Blender/Architecture_Complete_V24_12.blend')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def tree(n):
 o=bpy.data.objects[n];return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices)for f in o.data.polygons])
checks=[]
def ck(n,p,**extra):checks.append({'check':n,'pass':bool(p),**extra})
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;after=json.loads(json.dumps(snapshot(bpy)));before=json.loads((R/'V24_13_Before_Snapshot.json').read_text());sc.frame_set(40);bpy.context.view_layer.update();ch=json.loads((R/'V24_13_Changes.json').read_text());allow={r['name']for r in ch['changed']}
ck('No existing objects removed',set(before['objects'])<=set(after['objects']));ck('Only recorded objects added',set(after['objects'])-set(before['objects'])==set(ch['added']))
for n,a in before['objects'].items():
 b=after['objects'][n]
 for k in['type','parent','hide_render','animation','matrix']:ck('Preserved '+k+' / '+n,a[k]==b[k])
 if n not in allow:ck('Unchanged mesh / '+n,a['mesh_hash']==b['mesh_hash'])
for n,v in before['materials'].items():ck('Original shader / '+n,after['materials'].get(n)==v)
for n,v in before['images'].items():ck('Original image / '+n,after['images'].get(n)==v)
ck('All 26 door actions and their frame 1/20/40 poses preserved',after['actions']==before['actions']and after['doors']==before['doors']and after['door_poses']==before['door_poses']and len(after['doors'])==26)
ck('All photographic image assets packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'))
rt=tree('SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry');rows=[];ridgelevels=[];eavelevels=[]
for x in np.linspace(13.40,18.60,17):
 for y,kind in[(ridge(x),'ridge'),(front(x)+.006,'front'),(front(x)+(ridge(x)-front(x))*.45,'south'),(ridge(x)+(.30 if x<13.725 else .8),'north')]:
  p=rt.ray_cast(Vector((x,y,7)),Vector((0,0,-1)),10)[0];err=abs(p.z-roof_z(x,y))if p else 99;rows.append({'x':float(x),'y':float(y),'kind':kind,'z':p.z if p else None,'plane_error_m':err})
  if p and kind=='ridge':ridgelevels.append(p.z)
  if p and kind=='front':eavelevels.append(p.z)
ck('Both main slopes are planes',max(r['plane_error_m']for r in rows)<2e-5,maximum_plane_error_m=max(r['plane_error_m']for r in rows),samples=rows)
ck('Main ridge is level',len(ridgelevels)==17 and np.ptp(ridgelevels)<2e-5,z_range_m=float(np.ptp(ridgelevels)))
ck('Front eave baseline is level',len(eavelevels)==17 and np.ptp(eavelevels)<2e-5,z_range_m=float(np.ptp(eavelevels)))
inside=[];outside=[]
for x in np.linspace(W+.03,E-.03,13):
 inside.append(rt.ray_cast(Vector((x,front(x)+.03,6)),Vector((0,0,-1)),7)[0]is not None)
 outside.append(rt.ray_cast(Vector((x,front(x)-.05,6)),Vector((0,0,-1)),7)[0]is None)
ck('Squared front outline has continuous straight eave and no forward wedge',all(inside)and all(outside),inside_samples=len(inside),outside_samples=len(outside))
side=[]
for x in[W-.05,E+.05]:
 for y in[-16.2,-15.2,-14.2,-13.2]:side.append(rt.ray_cast(Vector((x,y,6)),Vector((0,0,-1)),7)[0]is None)
ck('Front slope sides are parallel straight boundaries with west extension removed',all(side),outside_side_samples=len(side))
tt=tree('SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry');deck=[]
for x in np.linspace(14.05,18.60,9):
 for lo,hi in[(front(x)+.15,ridge(x)-.15),(ridge(x)+.15,rear(x)-.15)]:
  for y in np.linspace(lo,hi,7):
   p=tt.ray_cast(Vector((x,y,7)),Vector((0,0,-1)),9)[0]
   if p:deck.append(p.z-roof_z(x,y))
ck('No old timber deck protrudes through new roof planes',len(deck)>10 and max(deck)<-.060,maximum_timber_height_relative_to_roof_plane_m=max(deck)if deck else None,hit_samples=len(deck))
fy=lambda x:-17.00174904+(x-10.8)*(-16.773484324+17.00174904)/(13.13-10.8)
wt=tree('SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry');ct=tree('V24_13_Secondary_Screenwall_End_Return_Coping');wall=[];clear=[]
for x in np.linspace(10.84,13.10,24):
 y=fy(x)+.14;p=wt.ray_cast(Vector((x,y,3.2)),Vector((0,0,-1)),2)[0];wall.append(p.z if p else 99)
ck('Secondary wall crown is flat and horizontal',max(abs(z-2.610)for z in wall)<2e-5,crown_samples=wall)
for x in[13.35,13.40]:
 for y in[-16.30,-16.23]:
  c=ct.ray_cast(Vector((x,y,4)),Vector((0,0,-1)),5)[0]
  r=rt.ray_cast(Vector((x,y,2.8)),Vector((0,0,1)),3)[0]
  clear.append({'x':x,'y':y,'coping_top_z':c.z if c else None,'roof_soffit_z':r.z if r else None,'gap_m':r.z-c.z if r and c else None})
ck('Secondary coping remains below storage eave soffit',all(r['gap_m']is not None and r['gap_m']>.03 for r in clear),samples=clear)
o=bpy.data.objects['V24_10_Secondary_Screenwall_Closed_Panel_Band'];v=np.array([o.matrix_world@p.co for p in o.data.vertices]);zz=np.unique(np.round(v[:,2],5));ck('Secondary outer panel band has two constant horizontal edges',len(zz)==2 and abs(zz[0]-2.18)<2e-5 and abs(zz[1]-2.50)<2e-5,edge_levels_m=zz.tolist())
cols=[o for o in bpy.data.objects if o.name.startswith('V24_11_Storage_Veranda_Column_')and'_Base_'not in o.name];ck('Only two veranda posts remain',len(cols)==2)
for o in cols:
 v=np.array([o.matrix_world@p.co for p in o.data.vertices]);lo=v[v[:,2]<v[:,2].min()+.001,:2].mean(0);hi=v[v[:,2]>v[:,2].max()-.001,:2].mean(0);ck('Post axis remains vertical / '+o.name,np.linalg.norm(hi-lo)<2e-5,axis_drift_m=float(np.linalg.norm(hi-lo)))
for n in ['SITE_V14_INNER_STORAGE_FLOOR_Geometry','SITE_V17_STORAGE_EAVE_GALLERY_FLOOR_Geometry','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry','SITE_V18_OUTER_STORAGE_THIN_METAL_CANOPY_Geometry','SITE_SOUTH_SCREENWALL_V12_STEPPED_MASONRY_UNDEREAVE_Geometry','V24_11_Screenwall_Continuous_Stepped_Stone_Plinth']:
 ck('Prior accepted feature preserved / '+n,before['objects'][n]==after['objects'][n])
# Export actual saved meshes for independent topology/volume readback.
exports=[]
for n in sorted(allow|set(ch['added'])):
 o=bpy.data.objects[n]
 if o.type!='MESH':continue
 me=o.data;me.calc_loop_triangles();v=np.empty(len(me.vertices)*3);me.vertices.foreach_get('co',v);v=v.reshape(-1,3);T=np.array(o.matrix_world);v=v@T[:3,:3].T+T[:3,3];f=np.array([t.vertices[:]for t in me.loop_triangles]);fn=f'SAVED_{len(exports):02d}.npz';np.savez_compressed(D/fn,v=v,f=f);exports.append({'name':n,'file':fn})
h=sha(P);(D/'Solid_Export_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2),encoding='utf8');build=json.loads((R/'V24_13_Build.json').read_text());ck('Readback matches final saved SHA256',h==build['sha256']);ck('Previous V24.12 file retained unchanged',sha(B)==build['source_sha256']);fail=[r for r in checks if not r['pass']];out={'status':'PASS_FRESH_NATIVE_QA'if not fail else'FAIL_FRESH_NATIVE_QA','model_sha256':h,'checks':checks,'failures':fail};(R/'V24_13_Fresh_Blend_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out['status'],len(checks),len(fail),flush=True)
for r in fail:print('FAIL',json.dumps(r,ensure_ascii=False),flush=True)
