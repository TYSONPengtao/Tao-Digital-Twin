import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'))
import rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');C=json.loads((O/'02_Data/Coordinate.json').read_text());a=math.radians(C['rotation_deg']);c=math.cos(a);s=math.sin(a)
def enu(p):return [p[0]*c-p[1]*s+C['origin'][0],p[0]*s+p[1]*c+C['origin'][1],p[2]+C['origin'][2]]
p=O/'04_Rhino/Reality_Hybrid_V8.3dm';F=rh.File3dm.Read(str(p))
cams=[('V8_Chinese_Flying_Eaves',[1,-24,7.2],[7,-13,3.7]),('V8_Kitchen_Gate_Joint',[3.1,-14.8,8.1],[8.7,-11.7,4.2]),('V8_Roman_Arch_Contact',[6.5,-8.8,2.8],[6.5,0,2.85]),('V8_Right_Wall_Stair',[8.6,9.2,1.55],[5.8,9.2,2.15]),('V8_West_Terrain_Only',[-8,-5,68],[-8,-2,-.3])]
for name,pos,tar in cams:
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pos=enu(pos);tar=enu(tar);vp.SetCameraLocation(rh.Point3d(*pos));vp.SetCameraDirection(rh.Vector3d(*[b-a for a,b in zip(pos,tar)]));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetFrustum(-.1,.1,-.065,.065,.1,10000);vp.SetScreenPort((0,1600,1040,0,0,1));F.NamedViews.Add(vi)
assert F.Write(str(p),8)
print('Named review views added',len(F.NamedViews),flush=True)
print('Embedded file API',dir(F.EmbeddedFiles[0]),flush=True)
print('File embedded helpers',[k for k in dir(F) if 'Embed' in k],flush=True)
