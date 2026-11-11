import bpy,sys,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_06_common import snapshot
D=W/'v24_33';O=Path('E:/jz/JIA/Rebuild_V24_33');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_33.blend';checks=[]
before=json.loads((D/'Before_Snapshot.json').read_text('utf8'));changes=json.loads((R/'V24_33_Changes.json').read_text('utf8'));prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));baseI={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))}
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('CHECK',n,bool(p),kw,flush=True)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(P));sc=bpy.context.scene;after=json.loads(json.dumps(snapshot(bpy)));allowed=set(changes['changed'])|set(changes['removed']);diff=[n for n,r in before['objects'].items() if n not in allowed and after['objects'].get(n)!=r];ck('All unrelated native objects geometry UV transforms and animation preserved',not diff,checked=len(set(before['objects'])-allowed),unexpected=diff)
for key in ['materials','actions','images']:
 diff=[n for n,r in before[key].items() if after[key].get(n)!=r];ck('Original '+key+' unchanged',not diff,checked=len(before[key]),unexpected=diff)
ck('All removals declared',set(before['objects'])-set(after['objects'])==set(changes['removed']),removed=changes['removed']);ck('All additions declared',set(after['objects'])-set(before['objects'])==set(changes['added']))
ck('All 26 animated doors keep their correct closed middle and open poses',len(before['doors'])==26 and before['door_poses']==after['door_poses']);ck('Marked F3 room door hinge stays on the corrected opposite jamb',abs(bpy.data.objects['DOOR_STUDY_F3__LEAF'].matrix_world.translation.x-8.853)<3e-5)
sc.frame_set(40);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();geos={};trees={};export=[]
def geo(n):
 if n not in geos:
  o=bpy.data.objects[n];me=o.data;me.calc_loop_triangles();geos[n]=(o,np.array([o.matrix_world@p.co for p in me.vertices],dtype=np.float64),np.array([t.vertices[:] for t in me.loop_triangles]))
 return geos[n]
def tree(n):
 if n not in trees:
  o,v,f=geo(n);trees[n]=BVHTree.FromPolygons([Vector(p) for p in v],f.tolist(),all_triangles=True,epsilon=1e-8)
 return trees[n]
def scenehit(origin,di,dist=30.):
 h,p,no,j,o,ma=sc.ray_cast(dg,Vector(origin),Vector(di),distance=dist)
 return {'point':list(p),'normal':list(no),'object':o.name,'material':o.data.materials[o.data.polygons[j].material_index].name} if h else None
for row in prep['raw_objects']:
 n=row['name'];o,v,f=geo(n);a=np.load(D/row['file']);me=o.data;mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:] for i in t.loops] for t in me.loop_triangles]);ck('Saved repaired mesh matches prepared geometry / '+n,len(v)==len(a['v']) and np.array_equal(f,a['f']) and float(abs(v-a['v']).max())<4e-5);ck('Saved repaired materials UV match source transfer / '+n,np.array_equal(mi,a['mi']) and np.isfinite(uv).all() and float(abs(uv-a['uv']).max())<4e-5)
 edges={}
 for face in f:
  for i,j in zip(face,np.roll(face,-1)):k=(int(min(i,j)),int(max(i,j)));edges[k]=edges.get(k,0)+1
 ck('Every repaired solid has closed two-face edges / '+n,all(c==2 for c in edges.values()),bad_edges=sum(c!=2 for c in edges.values()))
 ck('Repaired solid signed volume matches prepared volume / '+n,abs(float(np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()/6)-row['volume_m3'])<3e-5)
# Direct material-aware rays at the marked landing threshold and guard edge.
for fl,z in [(2,3.450024366378784),(3,7.050000190734863)]:
 hits=[]
 for x in ([8.05,8.45,8.75] if fl==2 else [4.3,5.5,6.5,7.5,8.5]):
  for y in [7.22,7.29,7.37]:hits.append(scenehit((x,y,z+.15),(0,0,-1)))
 ck('Marked landing floor band is continuous gray concrete F'+str(fl),all(h and h['object']==f'SLAB_JOINED_F{fl}_Geometry' and h['material']=='M_Concrete' and abs(h['point'][2]-z)<3e-5 and h['normal'][2]>.99 for h in hits),samples=hits)
hits=[]
for x in [.35,1.2,2.0,3.2,3.65]:
 for y in [1.3,1.9,3.5,5.,6.85]:hits.append(scenehit((x,y,7.40),(0,0,-1)))
ck('Terrace has original level concrete floor with no raised finish plate or roof fragments',all(h and h['object']=='SLAB_JOINED_F3_Geometry' and h['material']=='M_Concrete' and abs(h['point'][2]-7.05)<3e-5 for h in hits),samples=hits)
ck('Old terrace overlay retired',not bpy.data.objects.get('CONSTRUCTION_TERRACE_SLOPED_FINISH_Geometry'))
for row in prep['proof']['terrace_roof_intrusion']:
 n=row['object'];o,v,f=geo(n);tri=v[f];inside=(tri.mean(1)[:,0]<3.79999)&(tri.mean(1)[:,1]>1.20001)&(tri.mean(1)[:,2]>7.05001);ck('No porch roof surface inside usable F3 terrace / '+n,not inside.any(),intruding_triangles=int(inside.sum()))
wood=json.loads((D/'Wood_Probes_Before.json').read_text('utf8'));hits=[]
for r in wood:
 if not r['object'] or not any(t in r['object'] for t in ['BEFORE_WOOD_29','UPPER_FACADE_COLUMN','Carved_Bracket']):continue
 origin=Vector((7.8,-1.8,1.25));di=(Vector(r['point'])-origin).normalized();hits.append(scenehit(origin,di))
ck('Every identified dangling north timber sample now reveals intact blue brick',len(hits)>8 and all(h and h['object']=='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry' and h['material']=='M_V24_18_Continuous_Blue_Brick' for h in hits),samples=hits)
hits=[scenehit((x,-15.5,z),(0,-1,0)) for x in [10.8,11.2,11.8,12.2,12.7,12.9] for z in [.0,.7,1.4,1.9]]
ck('Southern marked wall body is continuously the original blue brick',all(h and h['object']=='SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry' and h['material']=='M_V24_20_Continuous_AsBuilt_Perimeter' for h in hits),samples=hits)
ck('Underlying as-built perimeter masonry and decorated upper bands unchanged',all(after['objects'][n]==before['objects'][n] for n in before['objects'] if n.startswith('SITE_PERIMETER_JOINED_RETAINING_WALL_') or n.startswith('SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS')))
hits=[scenehit((x,y,-.10),(0,0,-1)) for x,y in [(12.,-15.),(12.5,-15.),(12.8,-15.5),(13.1,-15.5),(13.2,-16.2),(13.5,-16.),(13.6,-15.),(14.,-15.5)]]
ck('Storage approach and gallery have one continuous gray floor owner',all(h and h['object']=='V24_31_Continuous_Gray_Road_And_Storage_Approach' and h['material']=='M_V12_Road_Concrete' for h in hits),samples=hits)
ck('Storage gallery joins the original -0.40m floor flush',all(abs(h['point'][2]+.4)<3e-5 for h in hits[-5:] if h));ck('Old storage threshold and raised gallery sheet retired',not any(bpy.data.objects.get(n) for n in ['V24_10_Entry_Continuous_Threshold','SITE_V17_STORAGE_EAVE_GALLERY_FLOOR_Geometry']))
post=prep['proof']['extra_stone_post']['column_center_xy_m'];q=tree('SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry').ray_cast(Vector((post[0],post[1]+.3,.60)),Vector((0,-1,0)),.6)[0];ck('Marked surplus terminal stone column removed',q is None)
ck('Previously completed stair rail remains unchanged',after['objects']['V24_32_Continuous_Stair_Wood_Railing']==before['objects']['V24_32_Continuous_Stair_Wood_Railing'])
# Read-only export actual saved exposed faces for a second, planar audit.
prefixes=('FACADE_CONTINUOUS','PARTITIONS_JOINED','HOUSE_V21_','HOUSE_V22_','SLAB_JOINED','BEAM_','KZ_','V24_31_F','CONSTRUCTION_SILL_');partners=[o.name for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith(prefixes) or o.name in [r['name'] for r in prep['raw_objects']] or o.name in ['SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','SITE_V14_INNER_STORAGE_FLOOR_Geometry','SITE_V14_OUTER_STORAGE_FLOOR_Geometry'])];vv=[];ff=[]
for n in partners:
 o,v,f=geo(n);k=len(vv);vv.extend(Vector(q) for q in v);ff.extend(tuple(int(i)+k for i in q) for q in f)
whole=BVHTree.FromPolygons(vv,ff,all_triangles=True,epsilon=1e-8)
for n in partners:
 o,v,f=geo(n);me=o.data;mi=np.array([me.polygons[t.polygon_index].material_index for t in me.loop_triangles]);uv=np.array([[me.uv_layers.active.data[i].uv[:] for i in t.loops] for t in me.loop_triangles]) if me.uv_layers.active else np.zeros((len(f),3,2));t=v[f];ns=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ns/=np.maximum(np.linalg.norm(ns,axis=1)[:,None],1e-20);cc=t.mean(1);visible=np.zeros(len(f),bool)
 for j in np.where(np.max(abs(ns),axis=1)>.999999)[0]:visible[j]=whole.ray_cast(Vector(cc[j]+ns[j]*.00015),Vector(ns[j]),.18)[0] is None
 fn='FINAL_'+str(len(export))+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv,visible=visible);export.append({'name':n,'file':fn,'materials':[m.name for m in me.materials]})
(D/'Final_Geometry_Index.json').write_text(json.dumps(export,ensure_ascii=False),encoding='utf8')
for txt,fn in [('V24_25_测量工具.py','measure_tools.py'),('V24_21_启动漫游.py','start_roam.py'),('V24_21_漫游控制器.py','roam_controller.py'),('V24_21_碰撞控制.py','roam_physics.py')]:ck('Roam and measure runtime preserved / '+fn,bpy.data.texts[txt].as_string()==(O/'Roam'/fn).read_text('utf8')==(Path('E:/jz/JIA/Rebuild_V24_32/Roam')/fn).read_text('utf8'))
ck('All textures and reference photos packed',all(i.packed_file for i in bpy.data.images if i.source=='FILE'));source=json.loads((D/'Source.json').read_text('utf8'));ck('Previous V24.32 native model remains untouched',sha(source['model'])==source['sha256']);failed=[c for c in checks if not c['pass']];(R/'V24_33_Native_QA.json').write_text(json.dumps({'status':'PASS_NATIVE_ANNOTATED_RESIDUAL_REPAIRS' if not failed else 'FAIL','model_sha256':sha(P),'checks':checks,'failures':failed},ensure_ascii=False,indent=2),encoding='utf8');print('V33_NATIVE_QA',len(checks),'FAIL',len(failed),flush=True)
