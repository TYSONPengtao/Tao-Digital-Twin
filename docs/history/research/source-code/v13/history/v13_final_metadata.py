import sys,json,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V13');path=O/'04_Rhino/Architecture_Complete_V13_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(path));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
for v in F.NamedViews:
 if v.Name.startswith('V12_'):v.Name=v.Name.replace('V12_','V13_',1)
for v in F.Views:
 if v.Name.startswith('V12_'):v.Name=v.Name.replace('V12_','V13_',1)
for name,pos,tar in [('V13_Terrace',[-11,-6,18],[1.8,5.3,9.5]),('V13_Canopy_Underside',[-2,-2,9.6],[1.8,4.3,9.8])]:
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pos=np.array(pos)@R.T+origin;tar=np.array(tar)@R.T+origin;vp.SetCameraLocation(rh.Point3d(*pos));vp.SetCameraDirection(rh.Vector3d(*(tar-pos)));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetScreenPort((0,1600,1100,0,0,1));vp.SetFrustum(-.1,.1,-.06875,.06875,.1,5000);F.NamedViews.Add(vi)
F.Strings['V13_Scene_SHA256']=hashlib.sha256((O/'08_Editable_Source/Architecture_Scene_V13.json').read_bytes()).hexdigest();F.Strings['V13_Model_Status']='Native profile coordinates repaired and canopy bearing connections completed. Actual native mesh readback and solid contacts reviewed; no member-strength calculation.'
assert F.Write(str(path),8)
print('Updated view names and current editable scene hash; geometric objects unchanged',flush=True)
