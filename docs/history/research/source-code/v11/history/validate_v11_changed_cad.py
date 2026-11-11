import sys,json,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'netlibs'))
import rhinoinside
rhinoinside.__parse_rhino_id(r'D:\AJAVIS01\RHINO8\RUNING\System').load(rhinoinside.__parse_framework_id('net48'))
import clr;clr.AddReference('RhinoCommon');import Rhino,System
core=Rhino.Runtime.InProcess.RhinoCore(System.Array[System.String](['/nosplash','/notemplate']),Rhino.Runtime.InProcess.WindowStyle.NoWindow)
O=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid');path=O/'04_Rhino/V11_Changed_Wall_Solids_LOCAL.3dm'
try:
 f=Rhino.FileIO.File3dm.Read(str(path));repair=0;bad=[];openb=[]
 for ob in list(f.Objects):
  g=ob.Geometry
  if isinstance(g,Rhino.Geometry.Brep):
   g.SetTolerancesBoxesAndFlags();repair+=1
   if not g.IsValid:g.Repair(.001);g.SetTolerancesBoxesAndFlags()
   at=ob.Attributes.Duplicate();id=at.ObjectId;f.Objects.Delete(id);assert f.Objects.Add(g,at)==id
  if not g.IsValid:bad.append(ob.Attributes.Name)
  if isinstance(g,(Rhino.Geometry.Brep,Rhino.Geometry.Extrusion)) and not g.IsSolid:openb.append(ob.Attributes.Name)
  if isinstance(g,Rhino.Geometry.Mesh) and not g.IsClosed:openb.append(ob.Attributes.Name)
 report={'status':'PASS' if not bad and not openb else 'FAIL','parts':f.Objects.Count,'invalid':bad,'open_solids':openb,'brep_tolerances_initialized':repair,'native_kernel':'RhinoCommon 8 headless; all changed site parts checked'}
 print(json.dumps(report),flush=True);assert not bad and not openb
 tmp=path.with_name(path.stem+'_validated.3dm');assert f.Write(str(tmp),8);shutil.copy2(tmp,path);tmp.unlink();report['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();(O/'06_Report/Changed_CAD_Kernel_QA.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
finally:core.Dispose()
