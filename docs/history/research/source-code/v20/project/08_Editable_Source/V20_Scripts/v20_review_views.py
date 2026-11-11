import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
O=Path('E:/jz/JIA/Rebuild_V20');P=O/'04_Rhino/Architecture_Complete_V20_ALIGNED_ENU.3dm';AQ=json.loads((O/'06_Report/V20_Assembly_QA.json').read_text(encoding='utf8'));QA=json.loads((O/'06_Report/V20_Native_Readback_QA.json').read_text(encoding='utf8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
assert sha(P)==QA['sha256'];F=rh.File3dm.Read(str(P));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);orig=np.array(C['origin']);expected={r['id']:r['geometry_hash'] for r in AQ['retained']+AQ['created']}
views=[('V20_Entry_Review',[8.5,-2.2,1.1],[6.5,.25,-.05],74),('V20_Storage_Gallery_Review',[14.15,-15.45,1.1],[18.82,-15.45,1.0],88)]
for name,pos,tar,fov in views:
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pp=np.array(pos)@R.T+orig;tt=np.array(tar)@R.T+orig;vp.SetCameraLocation(rh.Point3d(*pp));vp.SetCameraDirection(rh.Vector3d(*(tt-pp)));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetScreenPort((0,1600,1100,0,0,1));span=.05*math.tan(math.radians(fov/2));vp.SetFrustum(-span,span,-span*1100/1600,span*1100/1600,.05,5000);F.NamedViews.Add(vi)
assert F.Write(str(P),8);F=rh.File3dm.Read(str(P));assert len(F.Objects)==len(expected)
for ob in F.Objects:assert hashlib.sha256(json.dumps(ob.Geometry.Encode(),sort_keys=True).encode()).hexdigest()==expected[str(ob.Attributes.Id)],ob.Attributes.Name
oldsha=QA['sha256'];QA['sha256']=sha(P);QA['named_view_revision']={'old_model_sha256':oldsha,'new_review_views':views,'geometry_hashes_unchanged':len(expected)};(O/'06_Report/V20_Native_Readback_QA.json').write_text(json.dumps(QA,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/Review_Named_Views.json').write_text(json.dumps({'views':views,'all_native_geometry_hashes_preserved':len(expected)},indent=2),encoding='utf8');print('REVIEW VIEWS SAVED, ALL GEOMETRY UNCHANGED',len(expected),flush=True)
