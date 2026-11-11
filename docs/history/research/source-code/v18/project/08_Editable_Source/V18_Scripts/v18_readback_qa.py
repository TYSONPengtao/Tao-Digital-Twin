import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,manifold3d as mf,mapbox_earcut
O=Path(r'E:/jz/JIA/Rebuild_V18');P=O/'04_Rhino/Architecture_Complete_V18_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));AQ=json.loads((O/'06_Report/V18_Assembly_QA.json').read_text(encoding='utf8'));I=json.loads((O/'02_Data/Native_Readback_Index_V18.json').read_text(encoding='utf8'));ii={r['name']:r for r in I};C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);obs={str(o.Attributes.Id):o for o in F.Objects};names={o.Attributes.Name:o for o in F.Objects};checks=[];indexproof=[]
def check(n,ok,**data):
 checks.append({'check':n,'passed':bool(ok),**data})
 if not ok:raise AssertionError((n,data))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def gh(g):return hashlib.sha256(json.dumps(g.Encode(),sort_keys=True).encode()).hexdigest()
def arrays(mm):
 v=(np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R;f=[]
 for ff in mm.Faces:
  f.append(ff[:3])
  if ff[3]!=ff[2]:f.append([ff[0],ff[2],ff[3]])
 return v,np.array(f,np.int32)
def man_ob(ob):
 g=ob.Geometry
 if isinstance(g,rh.Mesh):v,f=arrays(g)
 elif isinstance(g,rh.Extrusion):
  r0=[];r1=[]
  for i in range(g.ProfileCount):
   cc=[]
   for tt in [0,1]:
    p=g.Profile3d(i,tt).TryGetPolyline();assert p is not None;cc.append((np.array([[p[j].X,p[j].Y,p[j].Z] for j in range(len(p)-1)])-origin)@R)
   r0.append(cc[0]);r1.append(cc[1])
  q=np.concatenate(r0);b=np.concatenate(r1);N=len(q);v=np.vstack([q,b]);axis=int(np.argmax(abs(b[0]-q[0])));axes=[j for j in range(3) if j!=axis];ends=np.cumsum([len(p) for p in r0]).astype(np.uint32);tr=mapbox_earcut.triangulate_float64(q[:,axes].copy(),ends).reshape(-1,3);f=tr[:,::-1].tolist()+(tr+N).tolist();off=0
  for pp in r0:
   for j in range(len(pp)):
    k=(j+1)%len(pp);f.extend([[off+j,off+k,off+k+N],[off+j,off+k+N,off+j+N]])
   off+=len(pp)
  f=np.array(f,np.int32);t=v[f]
  if np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()<0:f=f[:,::-1]
 else:raise TypeError(type(g).__name__)
 vv,inv=np.unique(np.round(v,8),axis=0,return_inverse=True);a=mf.Manifold(mf.Mesh64(vv.astype(np.float64),inv[f].astype(np.uint64)));check('Native solid accepted '+ob.Attributes.Name,a.status()==mf.Error.NoError);return a
def node(n):return [ob for ob in F.Objects if ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__')]
def man_node(n):return mf.Manifold.batch_boolean([man_ob(ob) for ob in node(n)],mf.OpType.Add)
for r in AQ['retained']:check('Retained geometry '+r['name'],r['id'] in obs and gh(obs[r['id']].Geometry)==r['geometry_hash'])
for r in AQ['deleted']:check('Obsolete object removed '+r['name'],r['id'] not in obs)
for r in AQ['created']:
 ob=obs[r['id']];mm=ob.Geometry;check('Saved changed geometry '+r['name'],gh(mm)==r['geometry_hash']);check('Valid closed mesh '+r['name'],mm.IsValid and mm.IsClosed);v,f=arrays(mm);nn=np.array([[p.X,p.Y,p.Z] for p in mm.Normals]);check('Full UV and unit normals '+r['name'],len(mm.TextureCoordinates)==len(v) and len(nn)==len(v) and np.max(abs(np.linalg.norm(nn,axis=1)-1))<5e-5);t=v[f];vol=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6);check('Outward volume '+r['name'],vol>1e-10,volume_m3=vol)
print('NATIVE HASH AND TOPOLOGY PASS',len(AQ['retained']),len(AQ['created']),flush=True)
for j,r in enumerate(I):
 n=r['name'];oo=node(n);vv=[];ff=[];uv=[];mi=[];mats=[]
 if any(not isinstance(ob.Geometry,rh.Mesh) for ob in oo):
  prior=Path(AQ['base_model']).parents[1]/'02_Data'/r['file'];cur=O/'02_Data'/r['file'];check('Inherited native cache unchanged '+n,sha(prior)==sha(cur) and all(str(ob.Attributes.Id) in {q['id'] for q in AQ['retained']} for ob in oo));indexproof.append({'node':n,'mode':'Inherited mesh cache hash plus retained native object/definition geometry hashes','native_objects':len(oo),'triangles':r['triangles']});continue
 for ob in oo:
  v,f=arrays(ob.Geometry);off=len(vv);vv.extend(v.tolist());ff.extend((f+off).tolist());uv.extend([[p.X,p.Y] for p in ob.Geometry.TextureCoordinates]);m=F.Materials[ob.Attributes.MaterialIndex].Name
  if m not in mats:mats.append(m)
  mi.extend([mats.index(m)]*len(f))
 d=np.load(O/'02_Data'/r['file']);dif=float(np.max(abs(np.array(vv)-d['vertices']))) if np.array(vv).shape==d['vertices'].shape else float('inf')
 check('Native readback parity '+n,len(oo)==r['native_objects'] and np.array_equal(np.array(ff),d['faces']) and dif<1e-8 and np.max(abs(np.array(uv)-d['uv']))<1e-8 and mats==r['materials'] and np.array_equal(mi,d['material_ids']),max_coordinate_error_m=dif)
 indexproof.append({'node':n,'native_objects':len(oo),'triangles':len(ff),'max_coordinate_error_m':dif})
 if j%100==0:print('INDEX PARITY',j,len(I),flush=True)
base=man_node('SITE_V18_CONTINUOUS_STORAGE_STONE_BASE');guard=man_node('SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD');metal=man_node('SITE_V18_OUTER_STORAGE_THIN_METAL_CANOPY');wood=man_node('SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY');check('Continuous base connected',len(base.decompose())==1);check('Stone guard connected',len(guard.decompose())==1);check('Metal roof frame posts connected',len(metal.decompose())==1);check('Timber assembly connected',len(wood.decompose())==1);check('Stone guard seated on continuous base',(base^guard).volume()>1e-5,positive_contact_m3=(base^guard).volume())
contacts=[]
for ob in node('SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES'):
 vol=(wood^man_ob(ob)).volume();check('Timber seated on '+ob.Attributes.Name,vol>1e-6,overlap_m3=vol);contacts.append({'base':ob.Attributes.Name,'overlap_m3':vol})
floor=man_node('SITE_V14_OUTER_STORAGE_FLOOR');check('Metal canopy posts seated on floor',(metal^floor).volume()>1e-5,overlap_m3=(metal^floor).volume())
toe=man_node('SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE');drain=man_node('SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE');check('Base-to-toe positive overlap',(base^toe).volume()>1e-3,overlap_m3=(base^toe).volume());check('Toe-to-channel positive overlap',(toe^drain).volume()>1e-3,overlap_m3=(toe^drain).volume())
# Per-station sections check the exact defect area, rather than relying on whole-site overlap.
segs=[s for s in json.loads((W/'v16/Drain_Segments.json').read_text(encoding='utf8')) if s['ci']==3];probes=[]
for s in segs:
 a,b=np.array(s['a']),np.array(s['b']);d=b-a;d/=np.linalg.norm(d);n=(np.array(s['outer_a'])-a)/1.05
 for tt in [.08,.5,.92]:
  p=a+(b-a)*tt;off=(np.array(s['outer_a'])-a)*(1-tt)/1.05+(np.array(s['outer_b'])-b)*tt/1.05;rz=s['za']*(1-tt)+s['zb']*tt
  # This point was in the exposed old step at the outer plinth/soil interface.
  cube=mf.Manifold.cube([.012,.012,.012]).translate([p[0]+off[0]*.09-.006,p[1]+off[1]*.09-.006,-1.55]);check('No exposed recess behind plinth',abs((base^cube).volume()-cube.volume())<1e-7,xy=p.tolist())
  cap=mf.Manifold.cube([.012,.012,.012]).translate([p[0]+off[0]*.168-.006,p[1]+off[1]*.168-.006,rz-.14]);check('Old mid-wall toe ledge absent',(toe^cap).volume()<1e-7,xy=p.tolist(),road_z=rz)
  seal=mf.Manifold.cube([.050,.050,.18]).translate([p[0]+off[0]*.16-.025,p[1]+off[1]*.16-.025,rz-.36]);check('Local toe-channel connection',(toe^drain^seal).volume()>1e-7,xy=p.tolist());probes.append({'xy':p.tolist(),'road_z':rz})
# Roof plane/valley and linked portals are inherited unchanged.
for n in ['SITE_V14_INNER_STORAGE_GABLE_ROOF','SITE_V14_KITCHEN_STORAGE_DIAGONAL_VALLEY','SITE_KITCHEN_CHINESE_TILE_ROOF']:
 check('Registered tiled roof retained '+n,any(r['name'].startswith(n) for r in AQ['retained']))
core=man_node('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY')
for pp,sz in [([13.105,-11.48,-.39],[.74,1.21,2.11]),([18.62,-13.43,-.39],[.50,1.25,2.16])]:
 boxman=mf.Manifold.cube(sz).translate(pp);check('Linked room portal remains clear',(core^boxman).volume()<1e-7)
for m in F.Materials:
 for getter in ['GetBitmapTexture','GetBumpTexture']:
  tx=getattr(m,getter)()
  if tx:check('Texture file available '+m.Name,Path(tx.FileName).exists())
check('Native review views present',all(v in [vi.Name for vi in F.NamedViews] for v in ['V18_Storage_Photo_Exterior','V18_Storage_Exterior_Oblique','V18_Storage_Base_Drain']))
check('No missing indexed native node',all(node(r['name']) for r in I));check('Current baseline file preserved',sha(Path(AQ['base_model']))==AQ['base_model_sha256'])
result={'status':'PASS_FRESH_NATIVE_STORAGE_EXTERIOR_QA','sha256':sha(P),'native_objects':len(F.Objects),'enumerated_objects':len(obs),'nodes':len(I),'triangles':sum(r['triangles'] for r in I),'retained_native_objects_verified':len(AQ['retained']),'changed_or_new_native_meshes_verified':len(AQ['created']),'removed_obsolete_objects_verified':len(AQ['deleted']),'all_index_nodes_checked':indexproof,'local_wall_drain_probes':probes,'timber_column_contacts':contacts,'checks':[r for r in checks if not r['check'].startswith(('Retained geometry','Obsolete object removed'))]}
(O/'06_Report/V18_Native_Readback_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print('V18 FRESH QA PASS',json.dumps({k:result[k] for k in ['native_objects','nodes','triangles','sha256']},ensure_ascii=False),flush=True)
