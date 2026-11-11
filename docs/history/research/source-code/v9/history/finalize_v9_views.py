import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'))
import rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid');C=json.loads((O/'02_Data/Coordinate.json').read_text());a=math.radians(C['rotation_deg']);c=math.cos(a);s=math.sin(a)
def enu(p):return [p[0]*c-p[1]*s+C['origin'][0],p[0]*s+p[1]*c+C['origin'][1],p[2]+C['origin'][2]]
p=O/'04_Rhino/Reality_Hybrid_V9.3dm';F=rh.File3dm.Read(str(p))
cams=[('V9_Gate_Kitchen_Joint',[3.1,-14.8,8.1],[8.7,-11.5,3.8]),('V9_Gate_Front',[2,-24,5.6],[7,-11.4,3.9]),('V9_Joint_Underside',[8.7,-13.8,2.05],[8.1,-11.3,3.3])]
for name,pos,tar in cams:
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pos=enu(pos);tar=enu(tar);vp.SetCameraLocation(rh.Point3d(*pos));vp.SetCameraDirection(rh.Vector3d(*[b-a for a,b in zip(pos,tar)]));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetFrustum(-.1,.1,-.065,.065,.1,10000);vp.SetScreenPort((0,1600,1040,0,0,1));F.NamedViews.Add(vi)
for vi in F.Views:
 if vi.Name=='V9_Whole_Site':
  pos=enu([3.1,-14.8,8.1]);tar=enu([8.7,-11.5,3.8]);vi.Viewport.SetCameraLocation(rh.Point3d(*pos));vi.Viewport.SetCameraDirection(rh.Vector3d(*[b-a for a,b in zip(pos,tar)]));vi.Name='V9_Gate_Kitchen_Joint_Review'
assert F.Write(str(p),8)
print('Named review views added',len(F.NamedViews),flush=True)
print('Embedded file API',dir(F.EmbeddedFiles[0]),flush=True)
print('File embedded helpers',[k for k in dir(F) if 'Embed' in k],flush=True)
