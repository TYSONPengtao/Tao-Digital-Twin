from v25_rhino_common import *
import json
core=start()
try:
 p='E:/jz/JIA/Rebuild_V25/Rhino/Architecture_Complete_V25.3dm';f=Rhino.FileIO.File3dm.Read(p);rows=[]
 for n in f.NamedViews:
  v=n.Viewport
  if not v.IsValid:
   rows.append({'name':n.Name,'camera':v.IsValidCamera,'frustum':v.IsValidFrustum,'log':str(v.IsValidWithLog()),'screen':str(v.ScreenPort),'perspective':v.IsPerspectiveProjection,'near':v.FrustumNear,'far':v.FrustumFar})
 print(json.dumps(rows[:12],ensure_ascii=True,indent=2),flush=True);print('TOTAL_INVALID',len(rows),flush=True)
 main=list(f.Views)[0].Viewport;print('MAIN',main.IsValid,main.IsValidCamera,main.IsValidFrustum,main.CameraLocation,flush=True)
 for enu in [False,True]:
  if enu:f.Dispose();f=Rhino.FileIO.File3dm.Read(p.replace('.3dm','_ALIGNED_ENU.3dm'))
  ob=list(f.Objects)[0];print('COORD',enu,ob.Geometry.GetBoundingBox(True),list(f.Views)[0].Viewport.CameraLocation,flush=True)
finally:core.Dispose()
