import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');F=rh.File3dm.Read(str(O/'01_Source/Pure_Site_UNMODIFIED.3dm'))
for i,ob in enumerate(list(F.Objects)):
    d=np.load(O/'02_Data'/('Base_'+str(i)+'.npz'));m=rh.Mesh();m.Vertices.UseDoublePrecisionVertices=True
    for p in d['vertices']:m.Vertices.AddPoint3d(*map(float,p))
    for f in d['faces']:m.Faces.AddFace(*map(int,f))
    mapping=rh.TextureMapping.CreatePlaneMapping(rh.Plane.WorldXY(),rh.Interval(0,1),rh.Interval(0,1),rh.Interval(0,1));m.SetTextureCoordinates(mapping,rh.Transform.Identity(),False)
    for j,u in enumerate(d['uv']):m.TextureCoordinates[j]=rh.Point2f(*map(float,u))
    # Plane mapping initializes computed normals. Replace those before
    # restoring the original survey normals and new clipped-edge normals.
    m.Normals.Clear()
    for n in d['normals']:m.Normals.Add(*map(float,n))
    for j,n in enumerate(d['normals']):m.Normals[j]=rh.Vector3f(*map(float,n))
    assert len(m.Normals)==len(m.Vertices)
    for c in ob.Geometry.VertexColors:m.VertexColors.Add(c)
    assert m.IsValid
    at=ob.Attributes;oid=at.Id;F.Objects.Delete(oid);assert F.Objects.AddMesh(m,at)==oid
assert F.Write(str(O/'01_Source/Pure_Site_WORKING_V8.3dm'),8)
G=rh.File3dm.Read(str(O/'01_Source/Pure_Site_WORKING_V8.3dm'))
for i,ob in enumerate(G.Objects):
    d=np.load(O/'02_Data'/('Base_'+str(i)+'.npz'))
    n=np.array([[p.X,p.Y,p.Z] for p in ob.Geometry.Normals])
    assert np.array_equal(n,d['normals'].astype(np.float32).astype(float))
print('Working source readback normals restored from exact survey arrays',flush=True)
