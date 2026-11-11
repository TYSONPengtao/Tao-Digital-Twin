"""Remove unused definitions after filtering the standalone site companion."""
import sys,json,hashlib,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'netlibs'))
import rhinoinside
rhinoinside.__parse_rhino_id(r'D:\AJAVIS01\RHINO8\RUNING\System').load(rhinoinside.__parse_framework_id('net48'))
import clr;clr.AddReference('RhinoCommon');import Rhino,System
core=Rhino.Runtime.InProcess.RhinoCore(System.Array[System.String](['/nosplash','/notemplate']),Rhino.Runtime.InProcess.WindowStyle.NoWindow)
O=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid');path=O/'04_Rhino/Courtyard_Pavilion_Gate_V11_ALIGNED_ENU.3dm'
try:
 F=Rhino.FileIO.File3dm.Read(str(path));assert not any(isinstance(ob.Geometry,Rhino.Geometry.InstanceReferenceGeometry) for ob in F.Objects)
 before={str(ob.Attributes.ObjectId):ob.Geometry.DataCRC(0) for ob in F.Objects};count=F.AllInstanceDefinitions.Count
 for d in list(F.AllInstanceDefinitions):assert F.AllInstanceDefinitions.Delete(d)
 assert F.AllInstanceDefinitions.Count==0 and F.Objects.Count==len(before)
 tmp=path.with_name(path.stem+'_clean.3dm');assert F.Write(str(tmp),8);G=Rhino.FileIO.File3dm.Read(str(tmp));assert G.AllInstanceDefinitions.Count==0
 after={str(ob.Attributes.ObjectId):ob.Geometry.DataCRC(0) for ob in G.Objects};assert after==before;assert all(ob.Geometry.IsValid for ob in G.Objects)
 shutil.copy2(tmp,path);tmp.unlink();qa={'status':'PASS','removed_unused_definitions':count,'actual_instances':0,'geometry_count':len(before),'all_geometry_data_crc_and_uuid_exact':True,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 (O/'06_Report/Standalone_Companion_Cleanup_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf8');p=O/'06_Report/Editable_Rhino_Alignment_QA.json';r=json.loads(p.read_text(encoding='utf8'));r['site_only_sha256']=qa['sha256'];r['companion_unused_definitions_removed']=count;p.write_text(json.dumps(r,indent=2),encoding='utf8');print(qa,flush=True)
finally:core.Dispose()
