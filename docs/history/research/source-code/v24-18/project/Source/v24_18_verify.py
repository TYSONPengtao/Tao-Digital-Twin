import bpy,json,sys,hashlib,numpy as np,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_18';O=Path('E:/jz/JIA/Rebuild_V24_18');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_18.blend';before=json.loads((D/'Before_Snapshot.json').read_text());changes=json.loads((R/'V24_18_Changes.json').read_text());prep=json.loads((D/'Prepared_Geometry.json').read_text());checks=[];allow=set(changes['changed']);new=set(changes['added'])
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
def coords(o):return np.array([o.matrix_world@p.co for p in o.data.vertices],dtype=np.float64)
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;after=json.loads(json.dumps(snapshot(bpy)));ck('No original object removed',set(before['objects'])<=set(after['objects']));ck('Only declared new objects',set(after['objects'])-set(before['objects'])==new)
for n,a in before['objects'].items():
 b=after['objects'][n]
 for k in ['type','parent','matrix','animation','hide_render']:ck('Preserved '+k+' / '+n,a[k]==b[k])
 if n not in allow:ck('Original geometry UV and slots / '+n,a['mesh_hash']==b['mesh_hash'])
for n,a in before['materials'].items():ck('Original material retained / '+n,after['materials'].get(n)==a)
for n,a in before['images'].items():ck('Original embedded photo retained / '+n,after['images'].get(n)==a)
for n,a in before['actions'].items():ck('Original action retained / '+n,after['actions'].get(n)==a)
ck('All 26 doors and 1/20/40 poses unchanged',len(after['doors'])==26 and before['doors']==after['doors']and before['door_poses']==after['door_poses']);ck('All file textures embedded',all(i.packed_file for i in bpy.data.images if i.source=='FILE'));ck('12 separate outward sash hinges',len(changes['outward_window_roots'])==12)
windows=[]
for w in prep['windows']:
 for s in w['sashes']:
  name='V24_18_'+s['name']+'_Outward_Hinge';root=bpy.data.objects[name];poses={}
  for f,fac in [(1,0),(20,.5),(40,1)]:
   sc.frame_set(f);bpy.context.view_layer.update();v=coords(bpy.data.objects[name+'_Frame']);poses[str(f)]={'angle_degrees':math.degrees(root.rotation_euler.z),'bounds':[v.min(0).tolist(),v.max(0).tolist()]};ck('Outward hinge angle '+name+' frame '+str(f),abs(math.degrees(root.rotation_euler.z)-s['angle_degrees']*fac)<1e-4)
   if f==1:ck('Closed sash exactly in original opening '+name,np.max(np.abs(v-np.array(s['frame']['v'])))<2e-5)
  ck('Open sash travels outward '+name,poses['40']['bounds'][0][1]<poses['1']['bounds'][0][1]-.20 and poses['40']['bounds'][1][1]<=poses['1']['bounds'][1][1]+.001)
  windows.append({'root':name,'poses':poses})
sc.frame_set(40);bpy.context.view_layer.update();exports=[];idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text())};extra=json.loads((D/'Extra_Index.json').read_text());names=allow|new|{r['name']for r in extra}|{'SLAB_JOINED_F1_Geometry','HOUSE_V20_ONE_SOLID_ENTRY_STEP_AND_PORCH_SUPPORT_Geometry','SITE_V16_GRADED_INTERIOR_SOIL_Geometry'}
for n in sorted(names):
 o=bpy.data.objects.get(n)
 if not o or o.type!='MESH':continue
 me=o.data;me.calc_loop_triangles();v=coords(o);f=np.array([t.vertices[:]for t in me.loop_triangles]);mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);fn=f'SAVED_{len(exports):03d}.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi);exports.append({'name':n,'file':fn,'materials':[m.name for m in me.materials]})
for n in ['SLAB_JOINED_F1_Geometry','SLAB_JOINED_F2_Geometry','SLAB_JOINED_F3_Geometry','ROMAN_COLUMN_X3.9_Z0_Geometry','ROMAN_COLUMN_X9.1_Z0_Geometry','V24_16_Storage_Entrance_White_Wall_Return','V24_11_Storage_Veranda_Column_1','V24_11_Storage_Veranda_Column_2']:
 ck('Original building datum and accepted entry fixed / '+n,before['objects'][n]==after['objects'][n])
for side in ['West','East']:
 v=coords(bpy.data.objects[f'V24_14_Storage_{side}_Sealed_Gable']);ck('Reduced narrow storage ear '+side,abs(v[:,2].max()-4.91)<.002,peak_z=float(v[:,2].max()))
uv=json.loads((R/'V24_18_Exterior_UV.json').read_text());uchecks=[]
for row in uv['surfaces']:
 n=row['object'];o=bpy.data.objects[n];me=o.data;v=coords(o);layer=me.uv_layers.active;maxz=0;bands=True;scales=[]
 for face in me.polygons:
  ids=list(face.vertices);t=v[ids];norm=np.cross(t[1]-t[0],t[2]-t[0]);norm/=max(np.linalg.norm(norm),1e-15);z=t[:,2].mean();expected=0 if z<-1.05-1e-7 else 1 if z<-.38-1e-7 else 2;bands&=face.material_index==expected
  if abs(norm[2])>.85 or np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))<2e-8:continue
  coordsuv=np.array([layer.data[k].uv[:]for k in face.loop_indices]);maxz=max(maxz,float(np.abs(coordsuv[:,1]-t[:,2]).max()))
  for a,b in [(0,1),(1,2),(2,0)]:
   L=np.linalg.norm(t[b,:2]-t[a,:2])
   if abs(t[b,2]-t[a,2])<2e-5 and L>.05:scales.append(abs(coordsuv[b,0]-coordsuv[a,0])/L)
 ck('Shared world-Z material bands / '+n,bands);ck('Unstretched vertical metre coordinates / '+n,maxz<3e-5,maximum_vertical_uv_error_m=maxz);ck('UV subdivision retains surface area / '+n,row['absolute_area_change_m2']<1e-5,absolute_area_change_m2=row['absolute_area_change_m2']);ck('Unstretched horizontal metre coordinates / '+n,not scales or max(abs(s-1)for s in scales)<.01,horizontal_metric_scale_min=min(scales)if scales else None,horizontal_metric_scale_max=max(scales)if scales else None);uchecks.append({'object':n,'horizontal_metric_scale_min':min(scales)if scales else None,'horizontal_metric_scale_max':max(scales)if scales else None,'vertical_max_error_m':maxz})
 if n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry']:
  oldfile=json.loads((D/'Detail_Probe.json').read_text())[n]['file'];a=np.load(D/oldfile);tree=BVHTree.FromPolygons([Vector(p)for p in a['v']],a['f'].tolist(),all_triangles=True);dist=max(tree.find_nearest(Vector(p))[3]for p in v);ck('Finish does not move original wall plan or face / '+n,dist<3e-5,maximum_surface_displacement_m=dist)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
(D/'Solid_Export_Index.json').write_text(json.dumps({'model_sha256':h,'objects':exports},indent=2));fail=[x for x in checks if not x['pass']];(R/'V24_18_Fresh_Blend_QA.json').write_text(json.dumps({'status':'PASS_FRESH_NATIVE_QA'if not fail else'FAIL_FRESH_NATIVE_QA','model_sha256':h,'checks':checks,'failures':fail,'windows':windows,'uv_checks':uchecks},ensure_ascii=False,indent=2),encoding='utf8');print('FRESH_QA',len(checks),'FAIL',len(fail),flush=True)
for r in fail:print('FAIL',r,flush=True)
