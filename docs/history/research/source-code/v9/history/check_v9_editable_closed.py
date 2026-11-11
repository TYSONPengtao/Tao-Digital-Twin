import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'));import rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid');changed=set(json.loads((O/'02_Data/V9_Changed_Nodes.json').read_text())['changed']);F=rh.File3dm.Read(str(O/'04_Rhino/Architecture_Edit_V9_ALIGNED_ENU.3dm'));bad=[];parts=[]
for ob in F.Objects:
 if not any(ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__') for n in changed):continue
 if isinstance(ob.Geometry,(rh.Brep,rh.Extrusion)):
  parts.append(ob.Attributes.Name)
  if not ob.Geometry.IsSolid or not ob.Geometry.IsValid:bad.append({'name':ob.Attributes.Name,'valid':ob.Geometry.IsValid,'solid':ob.Geometry.IsSolid})
r={'status':'PASS' if not bad and parts else 'FAIL','changed_solid_parts':len(parts),'bad':bad,'all_changed_native_parts_valid_and_solid':not bad,'conversion':'Double precision; actual 3D plane for polygon caps'}
(O/'06_Report/Editable_Changed_Solids_QA.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r),flush=True);assert r['status']=='PASS'
