import sys,json,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'netlibs'))
import rhinoinside
rhinoinside.__parse_rhino_id('D:/AJAVIS01/RHINO8/RUNING/System').load(rhinoinside.__parse_framework_id('net48'))
import clr;clr.AddReference('RhinoCommon');import Rhino,System
core=Rhino.Runtime.InProcess.RhinoCore(System.Array[System.String](['/nosplash','/notemplate']),Rhino.Runtime.InProcess.WindowStyle.NoWindow)
O=Path(__file__).parent;p=O/'V11_Pavilion_LOCAL_Review.3dm'
try:
    F=Rhino.FileIO.File3dm.Read(str(p));bad=[];opened=[];init=0;repairs=0
    for ob in list(F.Objects):
        g=ob.Geometry
        if isinstance(g,Rhino.Geometry.Brep):
            g.SetTolerancesBoxesAndFlags();init+=1
            if not g.IsValid:g.Repair(.001);g.SetTolerancesBoxesAndFlags();repairs+=1
            a=ob.Attributes.Duplicate();uid=a.ObjectId;F.Objects.Delete(uid);assert F.Objects.Add(g,a)==uid
        if not g.IsValid:bad.append(ob.Attributes.Name)
        if isinstance(g,(Rhino.Geometry.Brep,Rhino.Geometry.Extrusion)) and not g.IsSolid:opened.append(ob.Attributes.Name)
        if isinstance(g,Rhino.Geometry.Mesh) and not g.IsClosed:opened.append(ob.Attributes.Name)
    report=dict(status='PASS' if not bad and not opened else 'FAIL',parts=F.Objects.Count,invalid=bad,open_solids=opened,brep_flags_initialized=init,kernel_repairs=repairs,
                coordinate='LOCAL metres; isolated review file, integration transforms to ENU separately',kernel='RhinoCommon 8 headless')
    print(json.dumps(report),flush=True);assert not bad and not opened
    assert F.Write(str(p),8);report['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    (O/'Native_Geometry_QA.json').write_text(json.dumps(report,indent=2),encoding='utf8')
finally:core.Dispose()
