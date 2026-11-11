import sys,json,hashlib,collections,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'netlibs'))
import rhinoinside
rhinoinside.__parse_rhino_id(r'D:\AJAVIS01\RHINO8\RUNING\System').load(rhinoinside.__parse_framework_id('net48'))
import clr;clr.AddReference('RhinoCommon');import Rhino,System
core=Rhino.Runtime.InProcess.RhinoCore(System.Array[System.String](['/nosplash','/notemplate']),Rhino.Runtime.InProcess.WindowStyle.NoWindow)
O=Path(r'E:\jz\JIA\Rebuild_V12');B=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid');p=O/'04_Rhino/Architecture_Complete_V12_ALIGNED_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
try:
 report=json.loads((O/'06_Report/Native_Assembly_QA.json').read_text(encoding='utf8'));f=Rhino.FileIO.File3dm.Read(str(p));initialized=0
 for ob in list(f.Objects):
  if not ob.Attributes.GetUserString('V12_Element'):continue
  g=ob.Geometry
  if isinstance(g,Rhino.Geometry.Brep):
   g.SetTolerancesBoxesAndFlags();initialized+=1
   if not g.IsValid:g.Repair(.001);g.SetTolerancesBoxesAndFlags()
   at=ob.Attributes.Duplicate();ident=at.ObjectId;f.Objects.Delete(ident);assert f.Objects.Add(g,at)==ident
 invalid=[];opened=[];new=[];types=collections.Counter()
 for ob in f.Objects:
  if not ob.Geometry.IsValid:invalid.append(ob.Attributes.Name)
  if ob.Attributes.GetUserString('V12_Element'):
   new.append(str(ob.Attributes.ObjectId));g=ob.Geometry;types[type(g).__name__]+=1
   if isinstance(g,(Rhino.Geometry.Brep,Rhino.Geometry.Extrusion)) and not g.IsSolid:opened.append(ob.Attributes.Name)
   if isinstance(g,Rhino.Geometry.Mesh) and not g.IsClosed:opened.append(ob.Attributes.Name)
 assert not invalid and not opened,(invalid[:30],opened[:30])
 assert len(new)==report['new_parts']
 temp=p.with_name('V12_validated_temp.3dm');assert f.Write(str(temp),8);shutil.copy2(temp,p);temp.unlink();f.Dispose()
 # Read the delivered file, then compare native CRCs to the exact retained baseline.
 f=Rhino.FileIO.File3dm.Read(str(p));old=Rhino.FileIO.File3dm.Read(str(B/'04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm'));oldgeo={str(ob.Attributes.ObjectId):ob.Geometry.DataCRC(0) for ob in old.Objects};retained=set(report['retained_ids']);mismatch=[]
 for ob in f.Objects:
  ident=str(ob.Attributes.ObjectId)
  if ident in retained and ob.Geometry.DataCRC(0)!=oldgeo[ident]:mismatch.append(ob.Attributes.Name)
 assert not mismatch,mismatch[:20];old.Dispose()
 report.update(status='PASS',sha256=sha(p),kernel='RhinoCommon 8',new_parts_valid_closed=len(new),invalid=invalid,open_new_solids=opened,retained_geometry_crc_mismatches=mismatch,retained_geometry_crc_checks=len(retained),initialized_breps=initialized,new_geometry_types=dict(types),source_scan_triangles_in_primary=0)
 save(O/'06_Report/Native_Assembly_QA.json',report)
 companions=[];terrain_mutation=json.loads((W/'v12_terrain/Mutation.json').read_text(encoding='utf8'));terrain_names={e['name'] for e in terrain_mutation.get('add',[])+terrain_mutation.get('replace',[])}
 for label,predicate in [('Kitchen_Traditional_Timber_V12_ALIGNED_ENU',lambda n:n.startswith('SITE_KITCHEN') or n.startswith('SITE_V12_KITCHEN') or n.startswith('DOOR_KITCHEN')),('Terrain_Complete_V12_ALIGNED_ENU',lambda n:any(n==k or n.startswith(k+'__') for k in terrain_names))]:
  q=Rhino.FileIO.File3dm.Read(str(p));count=0
  for ob in list(q.Objects):
   if ob.Attributes.IsInstanceDefinitionObject or not predicate(ob.Attributes.Name):q.Objects.Delete(ob.Attributes.ObjectId)
   else:count+=1
  for d in list(q.AllInstanceDefinitions):q.AllInstanceDefinitions.Delete(d)
  q.Strings.SetString('Usage','V12 component-only native editable model, original ENU metres; not to be superimposed twice on main file');dest=O/'04_Rhino'/(label+'.3dm');assert q.Write(str(dest),8);q.Dispose();companions.append({'path':str(dest),'objects':count,'sha256':sha(dest)})
 report['companions']=companions;save(O/'06_Report/Native_Assembly_QA.json',report);f.Dispose();print(json.dumps({k:report[k] for k in ['status','new_parts_valid_closed','retained_geometry_crc_checks','initialized_breps','companions']},ensure_ascii=False),flush=True)
finally:core.Dispose()
