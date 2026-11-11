# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
from v25_rhino_common import *
core=start()
try:
 v=Rhino.DocObjects.ViewportInfo();v.SetCameraLocation(Rhino.Geometry.Point3d(10,-20,15));v.SetCameraDirection(Rhino.Geometry.Vector3d(-10,20,-15));v.SetCameraUp(Rhino.Geometry.Vector3d(0,0,1));v.SetFrustum(-.018,.018,-.012,.012,.05,2000);v.IsPerspectiveProjection=True;v.SetScreenPort(0,1600,0,1000,0,1000);v.TargetPoint=Rhino.Geometry.Point3d(0,0,0)
 rv=Rhino.Display.RhinoViewport();assert rv.SetViewProjection(v,True);vi=Rhino.DocObjects.ViewInfo(rv);vi.Name='Test';print('VIEW',vi.Viewport.IsValid,vi.Viewport.CameraLocation,flush=True)
 f=Rhino.FileIO.File3dm.Read(str(W/'v25/Smoke.3dm'));f.Views.Clear();f.NamedViews.Clear();f.Views.Add(vi);f.NamedViews.Add(vi)
 ob=list(f.Objects)[0];m=ob.Geometry.DuplicateMesh();a=ob.Attributes.Duplicate();oid=a.ObjectId;assert m.Transform(Rhino.Geometry.Transform.Translation(0,0,TAO_PRIVATE_SITE_002));assert f.Objects.Delete(oid);assert f.Objects.AddMesh(m,a)==oid
 p=str(W/'v25/PersistenceSmoke.3dm');assert f.Write(p,8);f.Dispose();f=Rhino.FileIO.File3dm.Read(p);vv=list(f.Views)[0].Viewport;print('READ_VIEW',vv.IsValid,vv.CameraLocation,flush=True);assert vv.IsValid and vv.CameraLocation.DistanceTo(v.CameraLocation)<1e-8;bb=list(f.Objects)[0].Geometry.GetBoundingBox(True);print('READ_TRANSFORM',bb,flush=True);assert bb.Min.Z>1300;print('PERSISTENCE_SMOKE_PASS',flush=True)
finally:core.Dispose()
