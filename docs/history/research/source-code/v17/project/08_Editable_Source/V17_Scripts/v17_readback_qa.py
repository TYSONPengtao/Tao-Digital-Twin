import sys,json,math,hashlib,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,manifold3d as mf
from shapely.geometry import Polygon,Point,shape
from shapely.ops import unary_union
O=Path(r'E:/jz/JIA/Rebuild_V17');P=O/'04_Rhino/Architecture_Complete_V17_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));AQ=json.loads((O/'06_Report/V17_Assembly_QA.json').read_text(encoding='utf8'));I=json.loads((O/'02_Data/Native_Readback_Index_V17.json').read_text(encoding='utf8'));ii={r['name']:r for r in I};C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);obs={str(o.Attributes.Id):o for o in F.Objects};names={o.Attributes.Name:o for o in F.Objects};checks=[]
def check(n,ok,**data):
 checks.append({'check':n,'passed':bool(ok),**data})
 if not ok:raise AssertionError((n,data))
def gh(g):return hashlib.sha256(json.dumps(g.Encode(),sort_keys=True).encode()).hexdigest()
def sh(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def arrays(mm):
 v=(np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R;f=[]
 for ff in mm.Faces:
  f.append(ff[:3])
  if ff[3]!=ff[2]:f.append([ff[0],ff[2],ff[3]])
 return v,np.array(f,np.int32)
def data(n):return np.load(O/'02_Data'/ii[n]['file'])
def top(n):
 d=data(n);t=d['vertices'][d['faces']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);return t[no[:,2]>1e-9]
def footprint(n):return unary_union([Polygon(q[:,:2]) for q in top(n)]).buffer(0)
def z_at(n,x,y):
 ts=top(n);p=np.array([x,y]);q=ts[(ts[:,:,:2].min(1)<=p+1e-6).all(1)&(ts[:,:,:2].max(1)>=p-1e-6).all(1)];zs=[]
 for t in q:
  A=np.column_stack([t[1,:2]-t[0,:2],t[2,:2]-t[0,:2]]);ab=np.linalg.solve(A,p-t[0,:2])
  if (ab>=-1e-5).all() and ab.sum()<=1+1e-5:zs.append(float(t[0,2]+ab@(t[1:,2]-t[0,2])))
 return max(zs) if zs else None
for r in AQ['retained']:check('Retained geometry '+r['name'],r['id'] in obs and gh(obs[r['id']].Geometry)==r['geometry_hash'])
for r in AQ['deleted']:check('Deleted obsolete object '+r['name'],r['id'] not in obs)
meshrows=[]
for r in AQ['created']:
 ob=obs[r['id']];mm=ob.Geometry;check('Changed geometry '+r['name'],gh(mm)==r['geometry_hash']);check('Valid mesh '+r['name'],mm.IsValid);check('Closed mesh '+r['name'],mm.IsClosed or not r.get('closed_expected',True));v,f=arrays(mm);uv=np.array([[p.X,p.Y] for p in mm.TextureCoordinates]);nn=np.array([[p.X,p.Y,p.Z] for p in mm.Normals]);t=v[f];vol=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)
 check('UV coverage '+r['name'],len(uv)==len(v));check('Unit normals '+r['name'],len(nn)==len(v) and np.max(abs(np.linalg.norm(nn,axis=1)-1))<5e-5)
 if r.get('closed_expected',True):check('Outward closed solid '+r['name'],vol>1e-10,signed_volume_m3=vol)
 meshrows.append({'name':r['name'],'triangles':len(f),'closed':mm.IsClosed,'signed_volume_m3':vol})
print('FRESH NATIVE HASH/TOPOLOGY PASS',len(AQ['retained']),len(AQ['created']),flush=True)
# Native arrays used for previews/export must match the saved-file geometry, in order.
indexproof=[]
for n in AQ['changed_nodes']:
 oo=[o for o in F.Objects if o.Attributes.Name==n or o.Attributes.Name.startswith(n+'__')];v=[];f=[];uv=[];nn=[]
 for ob in oo:
  vv,ff=arrays(ob.Geometry);off=len(v);v.extend(vv.tolist());f.extend((ff+off).tolist());uv.extend([[p.X,p.Y] for p in ob.Geometry.TextureCoordinates]);nn.extend((np.array([[p.X,p.Y,p.Z] for p in ob.Geometry.Normals])@R).tolist())
 d=data(n);v=np.array(v);f=np.array(f,np.int32);diff=float(np.max(abs(v-d['vertices'])))
 check('Saved mesh readback parity '+n,len(oo)==ii[n]['native_objects'] and np.array_equal(f,d['faces']) and diff<1e-8 and np.max(abs(np.array(uv)-d['uv']))<1e-8,coordinate_error_m=diff);indexproof.append({'node':n,'native_objects':len(oo),'triangles':len(f),'coordinate_error_m':diff})
outside=shape(json.loads((W/'v17/raised_soil_cut.geojson').read_text(encoding='utf8')));oldbox=shape(json.loads((W/'v17/obsolete_branch.geojson').read_text(encoding='utf8')))
check('No raised soil in exterior pocket',footprint('SITE_V16_GRADED_INTERIOR_SOIL').intersection(outside).area<1e-6)
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_0_TILE_COPING','SITE_PERIMETER_JOINED_RETAINING_WALL_0_PROVISIONAL_FLOWER_CROWN','SITE_PERIMETER_JOINED_RETAINING_WALL_0_PLASTER_STEPPED_RELIEF','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH']:
 ar=footprint(n).intersection(oldbox.buffer(-1e-5)).area;check('No obsolete wall branch '+n,ar<1e-6,remaining_area_m2=ar)
garden='SITE_V17_LOWER_EXTERIOR_GARDEN_TERRAIN';garden_probes=[]
for x,y in [[14,-8.9],[14,-8],[16,-8],[17,-8.4],[17,-5],[18,-4]]:
 z=z_at(garden,x,y);check('Lower garden level',z is not None and -4.5<z<-2.8,xy=[x,y],z=z);garden_probes.append([x,y,z])
facade=np.array(ii['SITE_V17_KITCHEN_STORAGE_CONTINUOUS_STONE_BASE']['element']['v17_facade_outer_line']);foundation_probes=[]
for a,b in zip(facade[:-1],facade[1:]):
 d=b-a;d/=np.linalg.norm(d);right=np.array([d[1],-d[0]])
 for s in [.1,.5,.9]:
  p=a+(b-a)*s+right*.10;z=z_at('SITE_V17_KITCHEN_STORAGE_CONTINUOUS_STONE_BASE',*p);check('Continuous L facade base',z is not None and abs(z+.38)<.002,xy=p.tolist(),z=z);foundation_probes.append([*p,z])
check('Storage under-slab support',abs(z_at('SITE_V17_KITCHEN_STORAGE_CONTINUOUS_STONE_BASE',17,-13)+.51)<.002)
# Original scan crop ground vertices are on the very same height field as the new garden.
DQ=json.loads((O/'06_Report/V17_Design_Control.json').read_text(encoding='utf8'));coef=np.array(DQ['garden']['fit_coefficients']);segs=json.loads((W/'v16/Drain_Segments.json').read_text(encoding='utf8'));segs=[r for r in segs if r['ci']==max(q['ci'] for q in segs)];patch=shape(json.loads((W/'v17/low_garden_patch.geojson').read_text(encoding='utf8')))
def garden_height(p):
 z=float(np.dot([*p,1],coef));best=None
 for r in segs:
  a=np.array(r['outer_a']);d=np.array(r['outer_b'])-a;s=np.clip((p-a)@d/(d@d),0,1);di=np.linalg.norm(p-a-s*d);zz=r['za']+s*(r['zb']-r['za'])
  if best is None or di<best[0]:best=(di,zz)
 di,zz=best
 if di<2:
  s=di/2;w=1-3*s*s+2*s*s*s;z=z*(1-w)+zz*w
 return z
d=data('SITE_V14_ORIGINAL_EXTERIOR_3');v=d['vertices'];errors=[]
for p in v[(v[:,0]>13.25)&(v[:,0]<20.8)&(v[:,1]>-10.1)&(v[:,1]<-2.4)&(v[:,2]<-1.7)]:
 if Point(p[:2]).distance(patch.boundary)<2e-7:errors.append(abs(p[2]-garden_height(p[:2])))
check('Garden/scan cut edge shared elevation',len(errors)>50 and max(errors)<.002,boundary_vertex_occurrences=len(errors),max_error_m=max(errors) if errors else None)

# Native closed-solid contacts verify timber posts are seated on stones and connected to beams.
def man_mesh(mm):
 v,f=arrays(mm);vv,inv=np.unique(np.round(v,8),axis=0,return_inverse=True);a=mf.Manifold(mf.Mesh64(vv.astype(np.float64),inv[f].astype(np.uint64)));assert a.status()==mf.Error.NoError,a.status();return a
rooftimber=man_mesh(names['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY__1'].Geometry);check('All storage timber connected',len(rooftimber.decompose())==1);stones=[o for o in F.Objects if o.Attributes.Name.startswith('SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES__')];contacts=[]
for base in stones:
 bv=(rooftimber^man_mesh(base.Geometry)).volume();check('Timber seated on stone base '+base.Attributes.Name,bv>1e-6,base_overlap_m3=bv);contacts.append({'stone_base':base.Attributes.Name,'wood_overlap_m3':bv})
guard=man_mesh(names['SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD__1'].Geometry);join=guard.volume();check('All stone guard components connected',len(guard.decompose())==1,volume_m3=join)
gf=z_at('SITE_V17_STORAGE_EAVE_GALLERY_FLOOR',16.4,-15.5);check('Gallery continuous floor',abs(gf+.394)<.002)
check('Roof surfaces preserved',all(any(r['name'].startswith(n) for r in AQ['retained']) for n in ['SITE_V14_INNER_STORAGE_GABLE_ROOF','SITE_V14_KITCHEN_STORAGE_DIAGONAL_VALLEY','SITE_KITCHEN_CHINESE_TILE_ROOF']))
core=man_mesh(names['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY__1'].Geometry)
for pp,sz in [([13.105,-11.48,-.39],[.74,1.21,2.11]),([18.62,-13.43,-.39],[.50,1.25,2.16])]:
 boxman=mf.Manifold.cube(sz).translate(pp);vol=(core^boxman).volume();check('Linked room portal remains clear',vol<1e-7,blocked_volume_m3=vol)
for m in F.Materials:
 for getter in ['GetBitmapTexture','GetBumpTexture']:
  tx=getattr(m,getter)()
  if tx:check('Texture available '+m.Name,Path(tx.FileName).exists())
views=[v.Name for v in F.NamedViews];check('Review views present',all(v in views for v in ['V17_Kitchen_Storage_Concave_Corner','V17_Storage_Timber_Interior','V17_Storage_Eave_Gallery','V17_Storage_Stone_Guard_Exterior']))
result={'status':'PASS_FRESH_NATIVE_GEOMETRY_AND_JUNCTION_QA','sha256':sh(P),'native_objects':len(F.Objects),'nodes':len(I),'triangles':sum(r['triangles'] for r in I),'retained_native_objects_verified':len(AQ['retained']),'changed_or_new_native_meshes_verified':len(AQ['created']),'deleted_obsolete_objects_verified':len(AQ['deleted']),'saved_readback_index_proof':indexproof,'garden_ground_probes':garden_probes,'L_base_probes':foundation_probes,'garden_scan_boundary_vertex_occurrences':len(errors),'garden_scan_max_height_error_m':max(errors),'timber_column_contacts':contacts,'stone_guard_connected_volume_m3':join,'checks':[r for r in checks if not r['check'].startswith(('Retained geometry','Changed geometry','Deleted obsolete object'))]}
(O/'06_Report/V17_Native_Readback_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print('PASS V17 FRESH NATIVE QA',json.dumps({k:result[k] for k in ['native_objects','nodes','retained_native_objects_verified','changed_or_new_native_meshes_verified','sha256']},ensure_ascii=False),flush=True)
