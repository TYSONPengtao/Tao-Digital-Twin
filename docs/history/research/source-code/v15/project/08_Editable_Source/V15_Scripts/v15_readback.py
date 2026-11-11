import sys,json,math,hashlib,shutil,collections
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh,mapbox_earcut
from scipy.spatial import cKDTree
O=Path(r'E:\jz\JIA\Rebuild_V15');B=Path(r'E:\jz\JIA\Rebuild_V14');D=O/'02_Data/Native_Readback';D.mkdir(exist_ok=True)
print('READBACK START',flush=True)
P=O/'04_Rhino/Architecture_Complete_V15_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));BF=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V14_ALIGNED_ENU.3dm'));obs={str(ob.Attributes.Id):ob for ob in F.Objects};bobs={str(ob.Attributes.Id):ob for ob in BF.Objects};Q=json.loads((O/'06_Report/V15_Assembly_QA.json').read_text(encoding='utf8'));I=json.loads((O/'02_Data/Modeled_Index_V15.json').read_text(encoding='utf8'));S=json.loads((O/'08_Editable_Source/Architecture_Scene_V15.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']};C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
print('MODELS LOADED',len(F.Objects),len(BF.Objects),flush=True)
def gh(g):return hashlib.sha256(json.dumps(g.Encode(),sort_keys=True).encode()).hexdigest()
bad=[q['name'] for q in Q['retained_native'] if q['id'] not in obs or gh(obs[q['id']].Geometry)!=q['geometry_hash']];assert not bad,bad[:5]
newbad=[q['name'] for q in Q['native_created'] if gh(obs[q['id']].Geometry)!=q['geometry_hash']];assert not newbad,newbad[:5]
print('GEOMETRY HASHES PASS',flush=True)
def base(n):return n.rsplit('__',1)[0] if '__' in n and n.rsplit('__',1)[1].isdigit() else n
groups={}
for ob in F.Objects:
 if not ob.Attributes.IsInstanceDefinitionObject:groups.setdefault(base(ob.Attributes.Name),[]).append(ob)
invalid=[ob.Attributes.Name for ob in F.Objects if not ob.Geometry.IsValid];assert not invalid,invalid[:10]
print('VALIDITY PASS',flush=True)
render_mats={}
for m in F.Materials:
 tx=m.GetBitmapTexture();bu=m.GetBumpTexture();pb=m.PhysicallyBased
 supported=pb.Supported
 render_mats[m.Name]={'color':[round(c*255) for c in list(pb.BaseColor)[:3]] if supported else list(m.DiffuseColor)[:3],'roughness':pb.Roughness if supported else .85,'metallic':pb.Metallic if supported else 0,'alpha':1-m.Transparency,'native_bitmap':tx.FileName if tx else None,'native_bump':bu.FileName if bu else None,'native_diffuse':list(m.DiffuseColor),'physically_based_supported':supported}
missing_bitmap=[r['native_bitmap'] for r in render_mats.values() if r['native_bitmap'] and not Path(r['native_bitmap']).exists()];assert not missing_bitmap,missing_bitmap
(O/'02_Data/Native_Render_Materials.json').write_text(json.dumps(render_mats,ensure_ascii=False,indent=2),encoding='utf8')
oldi={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V14.json').read_text(encoding='utf8'))};retained={q['id'] for q in Q['retained_native']};rows=[];parity=[];types=collections.Counter();profilechecks=[]
mixed_reuse=[]
def mesh_position_hash(g):
 v=np.array([[p.X,p.Y,p.Z] for p in g.Vertices.ToPoint3dArray()]);ff=[]
 for f in g.Faces:
  ff.append(f[:3])
  if f[2]!=f[3]:ff.append([f[0],f[2],f[3]])
 t=np.round(v[np.array(ff)],7);oo=np.lexsort((t[:,:,2],t[:,:,1],t[:,:,0]),axis=1);t=np.take_along_axis(t,oo[:,:,None],axis=1).reshape(-1,9);order=np.lexsort(tuple(t[:,i] for i in range(8,-1,-1)));return hashlib.sha256(t[order].tobytes()).hexdigest()
def fresh(g):
 if isinstance(g,rh.Mesh):
  v=np.array([[q.X,q.Y,q.Z] for q in g.Vertices.ToPoint3dArray()]);f=[]
  for face in g.Faces:
   f.append(face[:3])
   if face[2]!=face[3]:f.append([face[0],face[2],face[3]])
  uv=np.array([[p.X,p.Y] for p in g.TextureCoordinates]) if len(g.TextureCoordinates)==len(v) else None
  return (v-origin)@R,np.array(f,np.int32),uv
 if isinstance(g,rh.Extrusion):
  ring0=[];ring1=[]
  for i in range(g.ProfileCount):
   cc=[]
   for t in [0,1]:
    c=g.Profile3d(i,t);p=c.TryGetPolyline();assert p is not None
    q=np.array([[p[j].X,p[j].Y,p[j].Z] for j in range(len(p)-1)]);cc.append((q-origin)@R)
   ring0.append(cc[0]);ring1.append(cc[1])
  q=np.concatenate(ring0);b=np.concatenate(ring1);N=len(q);v=np.vstack([q,b]);ends=np.cumsum([len(p) for p in ring0]).astype(np.uint32);xy=q[:,:2].copy();tris=mapbox_earcut.triangulate_float64(xy,ends).reshape(-1,3);f=tris[:,::-1].tolist()+(tris+N).tolist();off=0
  for i,p in enumerate(ring0):
   for j in range(len(p)):
    k=(j+1)%len(p);f.extend([[off+j,off+k,off+k+N],[off+j,off+k+N,off+j+N]])
   off+=len(p)
  profilechecks.append({'profiles':g.ProfileCount,'closed':g.IsSolid,'min_local':v.min(0).tolist(),'max_local':v.max(0).tolist()});assert g.IsSolid
  return v,np.array(f,np.int32),None
 raise ValueError(type(g).__name__)
for ir,row in enumerate(I):
 n=row['name'];oblist=groups[n];e=E[n]
 if all(str(ob.Attributes.Id) in retained for ob in oblist):
  rr=dict(oldi[n]);rr['element']=row['element'];shutil.copy2(B/'02_Data'/rr['file'],O/'02_Data'/rr['file']);rows.append(rr);continue
 if any(isinstance(ob.Geometry,rh.Brep) for ob in oblist):
  # A few unchanged furniture/frame groups contain both native Breps and Meshes.
  # Prove their coordinates are unchanged after UV/normal repair, then reuse their existing kernel tessellation.
  assert n not in Q['geometry_changes'] and n not in Q['added'],n
  for ob in oblist:
   ident=str(ob.Attributes.Id);og=bobs[ident].Geometry;ng=ob.Geometry
   if isinstance(ng,rh.Mesh):assert mesh_position_hash(ng)==mesh_position_hash(og),ob.Attributes.Name
   else:assert gh(ng)==gh(og),ob.Attributes.Name
  rr=dict(oldi[n]);rr['element']=row['element'];shutil.copy2(B/'02_Data'/rr['file'],O/'02_Data'/rr['file']);rows.append(rr);mixed_reuse.append({'node':n,'objects_verified':len(oblist),'method':'Native Brep hashes unchanged; native Mesh triangle-coordinate hashes unchanged. UV/normals checked in saved model; existing native-kernel mixed-group tessellation reused.'});print('MIXED UNCHANGED POSITION PROOF',n,flush=True);continue
 vv=[];ff=[];mi=[];uvv=[];materials=[];offset=0
 if e.get('definition'):
  assert len(oblist)==1;ob=oblist[0];oldob=bobs[str(ob.Attributes.Id)];d=np.load(B/'02_Data'/oldi[n]['file']);v=d['vertices'];enu=v@R.T+origin;xf=ob.Geometry.Xform;of=oldob.Geometry.Xform;mx=np.array([[getattr(xf,'M'+str(i)+str(j)) for j in range(4)] for i in range(4)])@np.linalg.inv(np.array([[getattr(of,'M'+str(i)+str(j)) for j in range(4)] for i in range(4)]));v=(np.c_[enu,np.ones(len(enu))]@mx.T)[:,:3];v=(v-origin)@R;f=d['faces'];uv=d['uv'];mid=d['material_ids'];materials=oldi[n]['materials'];types['InstanceReferenceGeometry']+=1
 else:
  for ob in oblist:
   g=ob.Geometry;types[type(g).__name__]+=1;v,f,uv=fresh(g);mat=F.Materials[ob.Attributes.MaterialIndex].Name
   if mat not in materials:materials.append(mat)
   vv.append(v);ff.append(f+offset);mi.extend([materials.index(mat)]*len(f));uvv.append(v[:,:2] if uv is None else uv);offset+=len(v)
  v=np.vstack(vv);f=np.vstack(ff);uv=np.vstack(uvv);mid=np.array(mi,np.int32)
 fn='Native_Readback/NATIVE_'+n+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=v,faces=f,uv=uv,material_ids=mid);rr={'name':n,'file':fn,'materials':materials,'triangles':len(f),'native_objects':len(oblist),'element':row['element']};rows.append(rr)
 # Compare actual geometry bounds to the source scene as a file consistency check.
 md=np.load(O/'02_Data'/row['file']);model=md['vertices'];err=float(np.max(abs(np.array([v.min(0),v.max(0)])-np.array([model.min(0),model.max(0)]))));vertexerr=max(float(cKDTree(model).query(v)[0].max()),float(cKDTree(v).query(model)[0].max()));record={'node':n,'bbox_max_error_m':err,'symmetric_vertex_distance_m':vertexerr}
 if n.startswith('SITE_V14_ORIGINAL_EXTERIOR'):
  assert uv.shape==md['uv'].shape;record['original_uv_max_error']=float(abs(uv-md['uv']).max());assert record['original_uv_max_error']<1e-6
 parity.append(record);assert err<.001 and vertexerr<.001,(n,err,vertexerr)
 print('READBACK',ir,n,len(f),flush=True)
(O/'02_Data/Native_Readback_Index_V15.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
qa={'status':'PASS_NATIVE_FILE_READBACK','model':str(P),'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'native_objects':len(obs),'nodes':len(rows),'retained_geometry_hash_checks':len(Q['retained_native']),'retained_geometry_changes':bad,'created_geometry_hash_checks':len(Q['native_created']),'created_geometry_changes':newbad,'invalid_native':invalid,'fresh_native_types':dict(types),'profile_checks':len(profilechecks),'native_scene_parity':parity,'max_new_bbox_difference_m':max(r['bbox_max_error_m'] for r in parity),'method':'Fresh V15 rhino3dm file read: corrected Mesh coordinates, explicit UV and sharp normals and actual Extrusion Profile3d rings; retained Brep/block meshes reuse verified V14 actual-native-kernel data after complete native geometry hash equality','missing_native_bitmaps':missing_bitmap,'rhino_common_core_available_this_pass':False,'force_capacity_calculated':False}
(O/'06_Report/V15_Native_Readback_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');print('PASS',qa['nodes'],qa['max_new_bbox_difference_m'],flush=True)
(O/'06_Report/V15_Mixed_Group_Readback.json').write_text(json.dumps(mixed_reuse,ensure_ascii=False,indent=2),encoding='utf8')
