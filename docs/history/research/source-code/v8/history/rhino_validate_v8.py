import sys,json,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'netlibs'))
import rhinoinside
rhinoinside.__parse_rhino_id(r'D:\AJAVIS01\RHINO8\RUNING\System').load(rhinoinside.__parse_framework_id('net48'))
import clr
clr.AddReference('RhinoCommon')
import Rhino,System
core=Rhino.Runtime.InProcess.RhinoCore(System.Array[System.String](['/nosplash','/notemplate']),Rhino.Runtime.InProcess.WindowStyle.NoWindow)
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');path=O/'08_Editable_Source/06_Rhino/Production_1QK_ARCH.3dm'
try:
 f=Rhino.FileIO.File3dm.Read(str(path));repair=0
 for ob in list(f.Objects):
  if isinstance(ob.Geometry,Rhino.Geometry.Brep):
   b=ob.Geometry
   if not b.IsValid:
    b.SetTolerancesBoxesAndFlags();repair+=1
    if not b.IsValid:b.Repair(.001)
   b.SetTolerancesBoxesAndFlags();at=ob.Attributes.Duplicate();id=at.ObjectId
   f.Objects.Delete(id);newid=f.Objects.Add(b,at);assert newid==id
 temp=path.with_name(path.stem+'_validated.3dm');assert f.Write(str(temp),8)
 check=Rhino.FileIO.File3dm.Read(str(temp));bad=[];openb=[]
 for ob in check.Objects:
  if not ob.Geometry.IsValid:bad.append(ob.Attributes.Name)
  if isinstance(ob.Geometry,(Rhino.Geometry.Brep,Rhino.Geometry.Extrusion)) and not ob.Geometry.IsSolid and check.Layers[ob.Attributes.LayerIndex].Name not in ['60_SITE','90_UNCERTAIN']:openb.append(ob.Attributes.Name)
 report={'object_count':check.Objects.Count,'invalid':bad,'unexpected_open_solids':openb,'tolerances_initialized':repair,'native_kernel':'RhinoCommon 8 headless'}
 print(json.dumps(report),flush=True);assert not bad and not openb
 shutil.copy2(temp,path);temp.unlink()
 (O/'06_Report/Editable_Rhino_Kernel_QA.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
finally:core.Dispose()
