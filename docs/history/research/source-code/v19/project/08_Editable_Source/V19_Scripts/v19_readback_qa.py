"""Fresh saved-native geometry, facade support and drainage checks."""
import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,manifold3d as mf
O=Path(r'E:/jz/JIA/Rebuild_V19');P=O/'04_Rhino/Architecture_Complete_V19_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));AQ=json.loads((O/'06_Report/V19_Assembly_QA.json').read_text(encoding='utf8'));I=json.loads((O/'02_Data/Native_Readback_Index_V19.json').read_text(encoding='utf8'));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);obs={str(o.Attributes.Id):o for o in F.Objects};groups={};checks=[];indexproof=[];retained_ids={r['id'] for r in AQ['retained']}
for ob in F.Objects:
 parts=ob.Attributes.Name.split('__')
 for k in range(1,len(parts)+1):groups.setdefault('__'.join(parts[:k]),[]).append(ob)
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
 if isinstance(mm,rh.Brep):
  vv=[];ff=[];check('Retained Brep is solid',mm.IsSolid)
  for face in mm.Faces:
   dup=face.DuplicateFace(False);q=(np.array([[p.Location.X,p.Location.Y,p.Location.Z] for p in dup.Vertices])-origin)@R;check('Native roof face has simple planar boundary',len(q) in [3,4] and face.IsPlanar(1e-5));ud,vd=face.Domain(0),face.Domain(1);no=face.NormalAt((ud.T0+ud.T1)/2,(vd.T0+vd.T1)/2);nn=np.array([no.X,no.Y,no.Z])@R
   if face.OrientationIsReversed:nn=-nn
   cc=q.mean(0);u=q[0]-cc;u/=np.linalg.norm(u);w=np.cross(nn,u);angles=np.arctan2((q-cc)@w,(q-cc)@u);q=q[np.argsort(angles)];off=len(vv);vv.extend(q.tolist())
   for k in range(1,len(q)-1):ff.append([off,off+k,off+k+1])
  return np.array(vv),np.array(ff,np.int32)
 v=(np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R;f=[]
 for ff in mm.Faces:
  f.append(ff[:3])
  if ff[3]!=ff[2]:f.append([ff[0],ff[2],ff[3]])
 return v,np.array(f,np.int32)
def man_mesh(mm,label):
 v,f=arrays(mm);vv,inv=np.unique(np.round(v,10),axis=0,return_inverse=True);a=mf.Manifold(mf.Mesh64(vv.astype(np.float64),inv[f].astype(np.uint64)));check('Native solid accepted '+label,a.status()==mf.Error.NoError);return a
def node(n):return groups.get(n,[])
def man_node(n):return mf.Manifold.batch_boolean([man_mesh(ob.Geometry,ob.Attributes.Name) for ob in node(n)],mf.OpType.Add)
for r in AQ['retained']:check('Retained geometry '+r['name'],r['id'] in obs and gh(obs[r['id']].Geometry)==r['geometry_hash'])
for r in AQ['deleted']:check('Obsolete object removed '+r['name'],r['id'] not in obs)
for r in AQ['created']:
 ob=obs[r['id']];mm=ob.Geometry;check('Saved changed geometry '+r['name'],gh(mm)==r['geometry_hash']);check('Valid closed mesh '+r['name'],mm.IsValid and mm.IsClosed);v,f=arrays(mm);nn=np.array([[p.X,p.Y,p.Z] for p in mm.Normals]);check('Full UV and unit normals '+r['name'],len(mm.TextureCoordinates)==len(v) and len(nn)==len(v) and np.isfinite(v).all() and np.max(abs(np.linalg.norm(nn,axis=1)-1))<5e-5);t=v[f];vol=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6);check('Outward volume '+r['name'],vol>1e-10,volume_m3=vol)
print('V19 NATIVE HASH AND TOPOLOGY PASS',len(AQ['retained']),len(AQ['created']),flush=True)
for j,r in enumerate(I):
 n=r['name'];oo=node(n);vv=[];ff=[];uv=[];mi=[];mats=[]
 if any(not isinstance(ob.Geometry,rh.Mesh) for ob in oo):
  prior=Path(AQ['base_model']).parents[1]/'02_Data'/r['file'];cur=O/'02_Data'/r['file'];check('Inherited native cache unchanged '+n,sha(prior)==sha(cur) and all(str(ob.Attributes.Id) in retained_ids for ob in oo));indexproof.append({'node':n,'mode':'Inherited mesh cache hash plus retained native object/definition geometry hashes','native_objects':len(oo),'triangles':r['triangles']});continue
 for ob in oo:
  v,f=arrays(ob.Geometry);off=len(vv);vv.extend(v.tolist());ff.extend((f+off).tolist());uv.extend([[p.X,p.Y] for p in ob.Geometry.TextureCoordinates]);m=F.Materials[ob.Attributes.MaterialIndex].Name
  if m not in mats:mats.append(m)
  mi.extend([mats.index(m)]*len(f))
 d=np.load(O/'02_Data'/r['file']);dif=float(np.max(abs(np.array(vv)-d['vertices']))) if np.array(vv).shape==d['vertices'].shape else float('inf');check('Native readback parity '+n,len(oo)==r['native_objects'] and np.array_equal(np.array(ff),d['faces']) and dif<1e-8 and np.max(abs(np.array(uv)-d['uv']))<1e-8 and mats==r['materials'] and np.array_equal(mi,d['material_ids']),max_coordinate_error_m=dif);indexproof.append({'node':n,'native_objects':len(oo),'triangles':len(ff),'max_coordinate_error_m':dif})
 if j%100==0:print('INDEX PARITY',j,len(I),flush=True)
BF=rh.File3dm.Read(AQ['base_model']);bg={}
for ob in BF.Objects:
 parts=ob.Attributes.Name.split('__')
 for k in range(1,len(parts)+1):bg.setdefault('__'.join(parts[:k]),[]).append(ob)
def old(n):return mf.Manifold.batch_boolean([man_mesh(ob.Geometry,'V18 '+ob.Attributes.Name) for ob in bg[n]],mf.OpType.Add)
def major(a):return [p for p in a.decompose() if p.volume()>1e-8]
walls={};caps={};wallproof=[]
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
 walls[n]=man_node(n);before=old(n);lost=(before-walls[n]).volume();check('Registered retaining envelope kept '+n,lost<1e-5,lost_volume_m3=lost)
 added=walls[n]-before
 if n.endswith('_1'):check('West wall body unchanged',(added.volume()+lost)<1e-5,symmetric_volume_m3=added.volume()+lost)
 else:
  screenbox=mf.Manifold.cube([7.56,.82,2.5]).translate([3.245,-17.4,2.13]);outside=(added-screenbox).volume();check('Additional core limited to fitted upper screen',outside<1e-5,outside_volume_m3=outside)
 cap=man_node(n+'_TILE_COPING');caps[n]=cap;contacts=[]
 for j,p in enumerate(major(cap)):
  vol=(p^walls[n]).volume();check('Coping section backed '+n+str(j),vol>1e-9,section_volume_m3=p.volume(),bearing_overlap_m3=vol);contacts.append({'section':j,'volume_m3':p.volume(),'wall_bearing_overlap_m3':vol})
 check('Ordinary floral crown removed '+n,not node(n+'_PROVISIONAL_FLOWER_CROWN'));wallproof.append({'wall':n,'supported_coping_sections':contacts,'lost_registered_volume_m3':lost})
cn='SITE_V19_JOINED_PERIMETER_NORTHWEST_MASONRY_MITER';corner=man_node(cn)
for n,w in walls.items():check('Northwest miter bonded to '+n,(corner^w).volume()>1e-6,positive_contact_m3=(corner^w).volume())
for ob in node(cn):
 p=man_mesh(ob.Geometry,ob.Attributes.Name)
 for n,w in walls.items():check('Corner course supported '+ob.Attributes.Name+n,(p^w).volume()>1e-8,overlap_m3=(p^w).volume())
combined=walls['SITE_PERIMETER_JOINED_RETAINING_WALL_0']+walls['SITE_PERIMETER_JOINED_RETAINING_WALL_1']+corner;inside=man_node('SITE_V15_PERIMETER_WHITE_INSIDE_FINISH');decorobs=node('SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES');decps=[man_mesh(ob.Geometry,ob.Attributes.Name) for ob in decorobs];nb=next(r['element']['v19_backing_piece_count'] for r in I if r['name']=='SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES');backing=mf.Manifold.batch_boolean(decps[:nb],mf.OpType.Add);wall_support=combined+inside;frame_support=wall_support+backing;deccontacts=[]
# Every finish piece must touch a backed finish or the masonry, not merely share a group.
for j,ob in enumerate(decorobs):
 p=decps[j];vol=(p^(wall_support if j<nb else frame_support)).volume()
 check('Facade finish backed '+str(j),vol>1e-10,positive_contact_m3=vol);deccontacts.append({'object':ob.Attributes.Name,'backing_overlap_m3':vol})
roof=man_node('SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL');check('Raised screen core bears retained tile roof',(roof^walls['SITE_PERIMETER_JOINED_RETAINING_WALL_0']).volume()>1e-5,overlap_m3=(roof^walls['SITE_PERIMETER_JOINED_RETAINING_WALL_0']).volume());check('Old blank white screen plates removed',not node('SITE_SOUTH_SCREENWALL_RAISED_BODY') and not node('SITE_SOUTH_SCREENWALL_UNDER_ROOF_BASE'))
dn='SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE';check('Drain geometry and survey tie retained exactly',[gh(ob.Geometry) for ob in node(dn)]==[gh(ob.Geometry) for ob in bg[dn]],mode='Identical encoded native mesh geometry, UV and normals; material assignment differs');drain=man_node(dn);tn='SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE'
def shape_triangles(oo):
 out=[]
 for ob in oo:
  v,f=arrays(ob.Geometry);tt=np.round(v[f],8)
  for t in tt:out.append(sorted(map(tuple,t)))
 return sorted(out)
check('Wall toe geometry retained',shape_triangles(node(tn))==shape_triangles(bg[tn]),mode='Canonical saved native triangle coordinates at 10 nm; UV finish changes allowed');toe=man_node(tn)
segs=json.loads((W/'v16/Drain_Segments.json').read_text(encoding='utf8'));probes=[];excluded=[];fd=json.loads((O/'02_Data/Perimeter_Facade_Segments_V19.json').read_text(encoding='utf8'));ar=np.array([r['a'] for r in fd['brick']]);br=np.array([r['b'] for r in fd['brick']]);dr=br-ar;ll=np.sum(dr*dr,axis=1);masonry_support=combined+toe
for ci in [0,1,2]:
 ss=[s for s in segs if s['ci']==ci]
 for s in ss[::max(1,len(ss)//12)]:
  aa,bb=np.array(s['a']),np.array(s['b']);p=(aa+bb)/2;off=((np.array(s['outer_a'])-aa)+(np.array(s['outer_b'])-bb))/2/1.05;rz=(s['za']+s['zb'])/2;front=p+off*.16;tt=np.clip(np.sum((front-ar)*dr,axis=1)/ll,0,1);distance=float(np.linalg.norm(front-ar-tt[:,None]*dr,axis=1).min())
  if distance>.10:
   excluded.append({'chain':ci,'station':s['j'],'xy':p.tolist(),'distance_to_current_registered_wall_m':distance,'reason':'Legacy drain station inside the corrected kitchen/storage footprint, away from the currently retained perimeter wall'});continue
  seal=mf.Manifold.cube([.050,.050,.18]).translate([front[0]-.025,front[1]-.025,rz-.36]);vol=(masonry_support^drain^seal).volume();check('Local perimeter masonry-channel join '+str((ci,s['j'])),vol>1e-7,xy=p.tolist(),positive_overlap_m3=vol);probes.append({'chain':ci,'station':s['j'],'xy':p.tolist(),'road_z':rz,'overlap_m3':vol,'support':'Main registered retaining masonry or its buried toe; the toe can lie below the drain at high road stations'})
for n in ['SITE_V18_CONTINUOUS_STORAGE_STONE_BASE','SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD','SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY','SITE_V18_OUTER_STORAGE_THIN_METAL_CANOPY','SITE_V14_INNER_STORAGE_GABLE_ROOF','SITE_V14_KITCHEN_STORAGE_DIAGONAL_VALLEY','SITE_KITCHEN_CHINESE_TILE_ROOF']:
 check('Previously corrected storage and roof retained '+n,all(str(ob.Attributes.Id) in retained_ids for ob in node(n)) and bool(node(n)))
for m in F.Materials:
 for getter in ['GetBitmapTexture','GetBumpTexture']:
  tx=getattr(m,getter)()
  if tx:check('Texture file available '+m.Name,Path(tx.FileName).exists())
check('Native perimeter review views present',all(v[0] in [vi.Name for vi in F.NamedViews] for v in AQ['cameras']));check('No missing indexed native node',all(node(r['name']) for r in I));check('Current V18 baseline preserved',sha(Path(AQ['base_model']))==AQ['base_model_sha256'])
result={'status':'PASS_FRESH_NATIVE_PERIMETER_QA','sha256':sha(P),'native_objects':len(F.Objects),'nodes':len(I),'triangles':sum(r['triangles'] for r in I),'retained_native_objects_verified':len(AQ['retained']),'changed_or_new_native_meshes_verified':len(AQ['created']),'removed_obsolete_objects_verified':len(AQ['deleted']),'all_index_nodes_checked':indexproof,'coping_supports':wallproof,'finish_supports':deccontacts,'local_wall_drain_probes':probes,'legacy_station_exclusions':excluded,'checks':[r for r in checks if not r['check'].startswith(('Retained geometry','Obsolete object removed'))]}
(O/'06_Report/V19_Native_Readback_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print('V19 FRESH QA PASS',json.dumps({k:result[k] for k in ['native_objects','nodes','triangles','sha256']},ensure_ascii=False),flush=True)
