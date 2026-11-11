import sys,json,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'netlibs'))
import rhinoinside
rhinoinside.__parse_rhino_id(r'D:\AJAVIS01\RHINO8\RUNING\System').load(rhinoinside.__parse_framework_id('net48'))
import clr
clr.AddReference('RhinoCommon')
import Rhino,System
core=Rhino.Runtime.InProcess.RhinoCore(System.Array[System.String](['/nosplash','/notemplate']),Rhino.Runtime.InProcess.WindowStyle.NoWindow)
OUT=Path(r'E:\jz\JIA\Rebuild_V5');results={}
try:
 for mode in ['ARCH','VIS']:
  path=OUT/'06_Rhino'/f'Production_1QK_{mode}.3dm';f=Rhino.FileIO.File3dm.Read(str(path));repair=0
  for ob in list(f.Objects):
   if isinstance(ob.Geometry,Rhino.Geometry.Brep):
    b=ob.Geometry
    if not b.IsValid:
     b.SetTolerancesBoxesAndFlags();repair+=1
     if not b.IsValid:b.Repair(.001)
    b.SetTolerancesBoxesAndFlags()
    at=ob.Attributes.Duplicate();id=at.ObjectId
    f.Objects.Delete(id)
    newid=f.Objects.Add(b,at)
    assert newid==id,'Native replacement must retain block object IDs'
  temp=path.with_name(path.stem+'_validated.3dm');assert f.Write(str(temp),8)
  check=Rhino.FileIO.File3dm.Read(str(temp));bad=[];openb=[]
  for ob in check.Objects:
   if not ob.Geometry.IsValid:bad.append(ob.Attributes.Name)
   layer=check.Layers[ob.Attributes.LayerIndex]
   if isinstance(ob.Geometry,Rhino.Geometry.Brep) and not ob.Geometry.IsSolid and layer.Name not in ['60_SITE','90_UNCERTAIN']:openb.append(ob.Attributes.Name)
  results[mode]={'object_count':check.Objects.Count,'invalid':bad,'unexpected_open_breps':openb,'tolerances_initialized':repair,'native_kernel':'RhinoCommon 8, headless Rhino.Inside'}
  print(mode,json.dumps(results[mode]),flush=True)
  assert not bad and not openb
  shutil.copy2(temp,path);temp.unlink()
 shutil.copy2(OUT/'06_Rhino/Production_1QK_ARCH.3dm',OUT/'06_Rhino/Production_1QK_Rebuild.3dm')
 (OUT/'09_Report/Rhino_Kernel_Validation.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
 qa=json.loads((OUT/'09_Report/Native_Model_QA.json').read_text(encoding='utf-8'))
 for mode in results:qa[mode]['rhino']['invalid']=results[mode]['invalid'];qa[mode]['rhino']['unexpected_open_solids']=results[mode]['unexpected_open_breps'];qa[mode]['rhino']['kernel_validation']=results[mode]
 (OUT/'09_Report/Native_Model_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
finally:core.Dispose()
