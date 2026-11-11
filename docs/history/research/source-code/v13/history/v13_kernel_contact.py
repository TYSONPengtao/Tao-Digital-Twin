import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'netlibs')]
import rhinoinside
rhinoinside.__parse_rhino_id(r'D:\AJAVIS01\RHINO8\RUNING\System').load(rhinoinside.__parse_framework_id('net48'))
import clr;clr.AddReference('RhinoCommon');import Rhino,System
core=Rhino.Runtime.InProcess.RhinoCore(System.Array[System.String](['/nosplash','/notemplate']),Rhino.Runtime.InProcess.WindowStyle.NoWindow)
O=Path(r'E:\jz\JIA\Rebuild_V13');path=O/'04_Rhino/Architecture_Complete_V13_ALIGNED_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
try:
 F=Rhino.FileIO.File3dm.Read(str(path));obs={str(ob.Attributes.ObjectId):ob for ob in F.Objects};defs={str(d.Id):d for d in F.AllInstanceDefinitions};groups={}
 for ob in F.Objects:
  if ob.Attributes.IsInstanceDefinitionObject:continue
  n=ob.Attributes.Name;key=n.rsplit('__',1)[0] if '__' in n and n.rsplit('__',1)[1].isdigit() else n;groups.setdefault(key,[]).append(ob)
 def breps(ob,xf=None):
  g=ob.Geometry
  if isinstance(g,Rhino.Geometry.InstanceReferenceGeometry):
   t=g.Xform if xf is None else xf*g.Xform
   for ident in defs[str(g.ParentIdefId)].GetObjectIds():yield from breps(obs[str(ident)],t)
  else:
   if isinstance(g,Rhino.Geometry.Brep):b=g.DuplicateBrep()
   elif isinstance(g,Rhino.Geometry.Extrusion):b=g.ToBrep()
   elif isinstance(g,Rhino.Geometry.Mesh):b=Rhino.Geometry.Brep.CreateFromMesh(g,True)
   else:return
   if xf is not None:b.Transform(xf)
   yield b
 def pair(a,b):
  aa=[q for ob in groups[a] for q in breps(ob)];bb=[q for ob in groups[b] for q in breps(ob)];found=[]
  for i,x in enumerate(aa):
   bx=x.GetBoundingBox(True)
   for j,y in enumerate(bb):
    by=y.GetBoundingBox(True)
    if not Rhino.Geometry.BoundingBox.Intersection(bx,by).IsValid:continue
    hit,curves,points=Rhino.Geometry.Intersect.Intersection.BrepBrep(x,y,.001)
    if hit and (len(curves) or len(points)):found.append({'child_part':i,'support_part':j,'intersection_curves':len(curves),'intersection_points':len(points)})
  return {'child':a,'support':b,'passed':bool(found),'actual_native_brep_intersections':found}
 checks=[];ledger='TERRACE_CANOPY_V13_SIDE_WALL_LEDGER'
 for n in ['FACADE_CONTINUOUS_F3','PARTITIONS_JOINED_F3']:checks.append(pair(ledger,n))
 for z,slab in [(0,'SLAB_JOINED_F2'),(3.9,'SLAB_JOINED_F3')]:
  for x in [3.9,9.1]:
   col='ROMAN_COLUMN_X'+str(x)+'_Z'+str(z);checks.append(pair(col,slab));checks.append(pair('PORCH_ARCH_BEAM_Z'+str(z),col))
 # Confirm late view/string edits preserved every actual object's geometry.
 registry=json.loads((O/'06_Report/Native_Meshed_Object_Registry.json').read_text(encoding='utf8'));mismatch=[]
 for row in registry:
  if int(obs[row['id']].Geometry.DataCRC(0))!=row['crc']:mismatch.append(row['name'])
 assert not mismatch,mismatch[:10]
 qa={'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','model_sha256':sha(path),'kernel':'RhinoCommon 8','method':'Actual native Brep-Brep intersections, resolved native instance definition geometry; no source-parametric fallback','checks':checks,'meshed_object_crc_rechecks':len(registry),'geometry_mismatches_after_view_metadata_edit':mismatch,'strength_calculation':False}
 (O/'06_Report/Native_Kernel_Contact_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(qa,ensure_ascii=False),flush=True)
 nr=json.loads((O/'06_Report/Native_Readback_QA.json').read_text(encoding='utf8'));nr['mesh_source_model_sha256']=nr['sha256'];nr['sha256']=qa['model_sha256'];nr['named_views_metadata_only_crc_rechecks']=len(registry);nr['bbox_tolerance_m']=.001;assert nr['maximum_native_scene_mesh_bbox_error_m']<.001;(O/'06_Report/Native_Readback_QA.json').write_text(json.dumps(nr,ensure_ascii=False,indent=2),encoding='utf8')
 assert qa['status']=='PASS'
 F.Dispose()
finally:core.Dispose()
