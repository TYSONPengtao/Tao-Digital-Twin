import sys,json,math,hashlib,collections,time
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'netlibs')]
import numpy as np,rhinoinside
rhinoinside.__parse_rhino_id(r'D:\AJAVIS01\RHINO8\RUNING\System').load(rhinoinside.__parse_framework_id('net48'))
import clr;clr.AddReference('RhinoCommon');import Rhino,System
core=Rhino.Runtime.InProcess.RhinoCore(System.Array[System.String](['/nosplash','/notemplate']),Rhino.Runtime.InProcess.WindowStyle.NoWindow)
O=Path(r'E:\jz\JIA\Rebuild_V13');B=Path(r'E:\jz\JIA\Rebuild_V12');D=O/'02_Data/Native_Readback';D.mkdir(exist_ok=True)
S=json.loads((O/'08_Editable_Source/Architecture_Scene_V13.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']}
C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def base(n):return n.rsplit('__',1)[0] if '__' in n and n.rsplit('__',1)[1].isdigit() else n
report=json.loads((O/'06_Report/Profile_Repair_QA.json').read_text(encoding='utf8'));canopy=json.loads((O/'06_Report/Canopy_Connection_Changes.json').read_text(encoding='utf8'));changed=set(report['changed_native_ids'])|{x['id'] for x in canopy['native_changes']};source_path=B/'04_Rhino/Architecture_Complete_V12_ALIGNED_ENU.3dm';path=O/'04_Rhino/Architecture_Complete_V13_ALIGNED_ENU.3dm'
try:
 f=Rhino.FileIO.File3dm.Read(str(path));print('loaded native',len(list(f.Objects)),flush=True)
 obs={str(ob.Attributes.ObjectId):ob for ob in f.Objects};defs={str(d.Id):d for d in f.AllInstanceDefinitions};counts=collections.Counter();invalid=[];unmapped=[];groups=collections.defaultdict(list);crcs={}
 for ob in f.Objects:
  at=ob.Attributes;g=ob.Geometry;ident=str(at.ObjectId);crcs[ident]=int(g.DataCRC(0));counts[(type(g).__name__,at.IsInstanceDefinitionObject)]+=1
  if not g.IsValid:invalid.append(at.Name)
  if not at.IsInstanceDefinitionObject:
   n=base(at.Name)
   if n not in E:unmapped.append(at.Name)
   groups[n].append(ob)
 assert not invalid and not unmapped,(invalid[:12],unmapped[:12])
 members={str(x) for d in f.AllInstanceDefinitions for x in d.GetObjectIds()};flag_mismatches=[ob.Attributes.Name for ob in f.Objects if (str(ob.Attributes.ObjectId) in members)!=ob.Attributes.IsInstanceDefinitionObject];assert not flag_mismatches
 mp=Rhino.Geometry.MeshingParameters.FastRenderMesh;mp.Tolerance=.001;mp.MinimumEdgeLength=.0001
 def mesh_geometry(g):
  if isinstance(g,Rhino.Geometry.Mesh):return [g.DuplicateMesh()]
  if isinstance(g,Rhino.Geometry.Extrusion):g=g.ToBrep()
  elif isinstance(g,Rhino.Geometry.Surface):g=g.ToBrep()
  if isinstance(g,Rhino.Geometry.Brep):
   mm=Rhino.Geometry.Mesh.CreateFromBrep(g,mp)
   if mm is None:raise ValueError('No actual native mesh')
   return list(mm)
  return []
 cache={}
 def extract(ob,transform=None,depth=0):
  assert depth<5;g=ob.Geometry;at=ob.Attributes
  if isinstance(g,Rhino.Geometry.InstanceReferenceGeometry):
   xf=g.Xform if transform is None else transform*g.Xform
   for ident in defs[str(g.ParentIdefId)].GetObjectIds():yield from extract(obs[str(ident)],xf,depth+1)
  else:
   ident=str(at.ObjectId)
   if ident not in cache:cache[ident]=mesh_geometry(g)
   mi=at.MaterialIndex;mat=f.Materials[mi].Name if mi>=0 else 'M_Wall_Exterior'
   for mesh in cache[ident]:
    m=mesh.DuplicateMesh() if transform is not None else mesh
    if transform is not None:m.Transform(transform)
    yield m,mat
 rows=[];parts=[];parity=[];full_v=[];full_f=[];full_mid=[];material_names=[];curve_only=[];last=time.monotonic()
 for ni,(n,objects) in enumerate(groups.items()):
  vv=[];ff=[];mi=[];mmnames=[];uv=[];offset=0;part_bboxes=[]
  for ob in objects:
   start_offset=offset
   for m,mat in extract(ob):
    vertices=np.array([[q.X,q.Y,q.Z] for q in m.Vertices.ToPoint3dArray()],dtype=float);faces=[]
    for q in m.Faces:
     faces.append([q.A,q.B,q.C])
     if q.IsQuad:faces.append([q.A,q.C,q.D])
    faces=np.array(faces,dtype=np.int32)
    if not len(faces):continue
    ve=vertices.copy();vertices=(vertices-origin)@R
    if mat not in mmnames:mmnames.append(mat)
    mids=np.full(len(faces),mmnames.index(mat),np.int32)
    # Use native UVs when supplied; deterministic planar mapping otherwise.
    if len(list(m.TextureCoordinates))==len(vertices):uvs=np.array([[q.X,q.Y] for q in m.TextureCoordinates],float)
    else:
     ax=np.argsort(np.ptp(vertices,axis=0))[-2:];uvs=vertices[:,ax]
    vv.append(vertices);ff.append(faces+offset);uv.append(uvs);mi.append(mids);offset+=len(vertices)
    part_bboxes.extend([ve.min(0),ve.max(0)])
   if offset>start_offset:
    parts.append({'id':str(ob.Attributes.ObjectId),'name':ob.Attributes.Name,'node':n,'native_type':type(ob.Geometry).__name__,'crc':crcs[str(ob.Attributes.ObjectId)]})
  if not vv:curve_only.append(n);continue
  v=np.concatenate(vv);faces=np.concatenate(ff);mid=np.concatenate(mi);uvs=np.concatenate(uv);fn='NATIVE_'+n+'.npz';np.savez_compressed(D/fn,vertices=v,faces=faces,uv=uvs,material_ids=mid)
  row={'name':n,'file':str(Path('Native_Readback')/fn),'materials':mmnames,'triangles':len(faces),'element':{k:v for k,v in E[n].items() if k!='parts'},'native_objects':len(objects),'actual_3dm_mesh_bbox_local':[v.min(0).tolist(),v.max(0).tolist()]};rows.append(row)
  modeled=O/'02_Data'/('MODEL_'+n+'.npz')
  if modeled.exists():
   expected=np.load(modeled)['vertices'];err=float(np.max(abs(np.array([v.min(0),v.max(0)])-np.array([expected.min(0),expected.max(0)]))));parity.append({'name':n,'max_bbox_error_m':err})
  # Retain only block meshes in cache; free meshes for already completed nodes.
  for ob in objects:
   ident=str(ob.Attributes.ObjectId)
   if ident not in members:cache.pop(ident,None)
  if ni%25==0 or time.monotonic()-last>20:
   print('meshed actual native',ni+1,'/',len(groups),n,'triangles',len(faces),flush=True);last=time.monotonic()
 save(O/'02_Data/Native_Readback_Index_V13.json',rows);save(O/'06_Report/Native_Scene_Mesh_Parity.json',sorted(parity,key=lambda r:-r['max_bbox_error_m']));save(O/'06_Report/Native_Meshed_Object_Registry.json',parts)
 # Source CRC check includes definition members, all ordinary geometry, IDs.
 old=Rhino.FileIO.File3dm.Read(str(source_path));mismatch=[];retained=0
 for ob in old.Objects:
  ident=str(ob.Attributes.ObjectId)
  if ident in changed:continue
  retained+=1
  if ident not in crcs or int(ob.Geometry.DataCRC(0))!=crcs[ident]:mismatch.append(ob.Attributes.Name)
 old.Dispose();assert not mismatch,mismatch[:20]
 volumes=[]
 for ob in f.Objects:
  if str(ob.Attributes.ObjectId) not in report['changed_native_ids']:continue
  at=ob.Attributes;g=ob.Geometry;n=at.Name;key=base(n)
  if at.IsInstanceDefinitionObject:continue
  part=E[key]['parts'][int(n.rsplit('__',1)[1])-1]['geometry'];poly=part['outer'];holes=part['holes']
  def area(r):return abs(sum(r[i][0]*r[(i+1)%len(r)][1]-r[(i+1)%len(r)][0]*r[i][1] for i in range(len(r)))/2)
  expected=(area(poly)-sum(area(h) for h in holes))*abs(part['height']);b=g.ToBrep();vp=Rhino.Geometry.VolumeMassProperties.Compute(b)
  assert vp is not None,(n,'mass properties');err=abs(vp.Volume-expected);volumes.append({'name':n,'volume_m3':vp.Volume,'expected_m3':expected,'error_m3':err,'closed':g.IsSolid,'brep_valid':b.IsValid})
  assert g.IsSolid and b.IsValid and err<max(1e-6,expected*1e-5),(n,expected,vp.Volume,err)
 worst=max(r['max_bbox_error_m'] for r in parity);badparity=[r for r in parity if r['max_bbox_error_m']>.015];assert not badparity,badparity[:20]
 qa={'status':'PASS_ACTUAL_3DM_READBACK','model':str(path),'sha256':sha(path),'source_sha256':sha(source_path),'objects_including_definitions':len(obs),'rendered_native_nodes':len(rows),'actual_native_mesh_triangles':sum(r['triangles'] for r in rows),'invalid_geometries':invalid,'unmapped_objects':unmapped,'definition_membership_mismatches':flag_mismatches,'retained_geometry_crc_checks':retained,'retained_geometry_crc_mismatches':mismatch,'repaired_extrusion_volume_checks':len(volumes),'maximum_native_scene_mesh_bbox_error_m':worst,'bbox_tolerance_m':.015,'curve_only_non_render_nodes':curve_only,'note':'Previews are regenerated from actual native 3DM geometries including resolved block instances, not from the editable scene surrogate. Curved surface meshing differs slightly from scene polygon tessellation.'}
 save(O/'06_Report/Repaired_Extrusion_Volume_QA.json',volumes);save(O/'06_Report/Native_Readback_QA.json',qa);print(json.dumps(qa,ensure_ascii=False),flush=True);f.Dispose()
finally:core.Dispose()
