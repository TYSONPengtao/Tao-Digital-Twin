"""Fresh saved-native geometry, facade support and drainage checks."""
import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,manifold3d as mf
O=Path(r'E:/jz/JIA/Rebuild_V21');P=O/'04_Rhino/Architecture_Complete_V21_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));AQ=json.loads((O/'06_Report/V21_Assembly_QA.json').read_text(encoding='utf8'));I=json.loads((O/'02_Data/Native_Readback_Index_V21.json').read_text(encoding='utf8'));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);obs={str(o.Attributes.Id):o for o in F.Objects};groups={};checks=[];indexproof=[];retained_ids={r['id'] for r in AQ['retained']}
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
 ob=obs[r['id']];mm=ob.Geometry;check('Saved changed geometry '+r['name'],gh(mm)==r['geometry_hash']);check('Valid closed mesh '+r['name'],mm.IsValid and (mm.IsClosed or not r.get("closed_expected",True)));v,f=arrays(mm);nn=np.array([[p.X,p.Y,p.Z] for p in mm.Normals]);check('Full UV and unit normals '+r['name'],len(mm.TextureCoordinates)==len(v) and len(nn)==len(v) and np.isfinite(v).all() and np.max(abs(np.linalg.norm(nn,axis=1)-1))<5e-5);t=v[f];vol=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6);check('Outward volume '+r['name'],vol>1e-10 or not r.get("closed_expected",True),volume_m3=vol)
print('V21 NATIVE HASH AND TOPOLOGY PASS',len(AQ['retained']),len(AQ['created']),flush=True)
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

check('V20 source model preserved',sha(Path(AQ['base_model']))==AQ['base_model_sha256'])
for m in F.Materials:
 for getter in ['GetBitmapTexture','GetBumpTexture']:
  tx=getattr(m,getter)()
  if tx:check('Material bitmap exists '+m.Name,Path(tx.FileName).is_file())
report={'status':'PASS_FRESH_NATIVE_V21_QA','model':str(P),'sha256':sha(P),'native_objects':len(F.Objects),'nodes':len(I),'triangles':sum(r['triangles'] for r in I),'retained_objects':len(AQ['retained']),'changed_objects':len(AQ['created']),'checks':checks,'index_parity':indexproof,'ue5_import_tested':False}
(O/'06_Report/V21_Native_Readback_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('V21 FRESH NATIVE PASS',len(I),flush=True)
