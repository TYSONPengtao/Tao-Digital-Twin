import sys,json
from pathlib import Path
D=Path(__file__).parent;W=D.parent;sys.path.insert(0,str(W/'netlibs'))
import rhinoinside
rhinoinside.__parse_rhino_id(r'D:/AJAVIS01/RHINO8/RUNING/System').load(rhinoinside.__parse_framework_id('net48'))
import clr;clr.AddReference('RhinoCommon');import Rhino,System
core=Rhino.Runtime.InProcess.RhinoCore(System.Array[System.String](['/nosplash','/notemplate']),Rhino.Runtime.InProcess.WindowStyle.NoWindow)
try:
 f=Rhino.FileIO.File3dm.Read(str(D/'Candidate_Ground_LOCAL.3dm'));rows=[]
 for ob in list(f.Objects):
  g=ob.Geometry.Duplicate()
  if isinstance(g,Rhino.Geometry.Brep):
   g.SetTolerancesBoxesAndFlags()
   if not g.IsValid:g.Repair(.001);g.SetTolerancesBoxesAndFlags()
  row={'name':ob.Attributes.Name,'native_type':g.GetType().Name,'valid':g.IsValid,'closed':g.IsSolid};rows.append(row);print(row,flush=True)
  at=ob.Attributes.Duplicate();oid=at.ObjectId;f.Objects.Delete(oid);assert f.Objects.Add(g,at)==oid
 qa=json.loads((D/'Geometry_QA.json').read_text(encoding='utf-8'));qa['native_kernel_checks']=rows;qa['native_kernel']='RhinoCommon 8 headless; candidate only; Brep tolerances initialized'
 qa['invalid_parts']=[r['name'] for r in rows if not r['valid']];qa['open_parts']=[r['name'] for r in rows if not r['closed']]
 qa['status']='PASS_CANDIDATE' if not qa['invalid_parts'] and not qa['open_parts'] and qa['remaining_numerical_residual_m2']<1e-5 and qa['outside_true_gap_m2']<1e-7 else 'FAIL'
 (D/'Geometry_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8');assert f.Write(str(D/'Candidate_Ground_LOCAL_VALIDATED.3dm'),8);print('FINAL',qa['status'],flush=True)
finally:core.Dispose()
