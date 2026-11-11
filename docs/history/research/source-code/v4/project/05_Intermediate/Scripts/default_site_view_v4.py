import sys,json,ctypes as C,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import export_v4 as ex
su=ex.su;rh=ex.rh;O=ex.OUT;cam=next(x for x in ex.SCENE['cameras'] if x['name']=='CAM_06_Whole_Site')
su.SUInitialize();ex.extra_su_bind()
for mode in ['ARCH','VIS']:
 p=O/'07_SketchUp'/f'Production_1QK_{mode}.skp';model=su.new('SUModelCreateFromFile',str(p).encode());cr=su.new('SUCameraCreate');pp=su.Point(*[v/.0254 for v in cam['position']]);tt=su.Point(*[v/.0254 for v in cam['target']]);up=su.Point(0,0,1);su.ck(su.SUCameraSetOrientation(cr,C.byref(pp),C.byref(tt),C.byref(up)));su.ck(su.SUCameraSetPerspectiveFrustumFOV(cr,cam['fov']));su.ck(su.SUCameraSetAspectRatio(cr,1.6));su.ck(su.SUModelSetCamera(model,C.byref(cr)));su.ck(su.SUModelSaveToFile(model,str(p).encode()));su.SUModelRelease(C.byref(model))
 p=O/'06_Rhino'/f'Production_1QK_{mode}.3dm';model=rh.File3dm.Read(str(p));vi=next(v for v in model.NamedViews if v.Name=='CAM_06_Whole_Site');model.Views.Add(vi);assert model.Write(str(p),8)
 check=rh.File3dm.Read(str(p));assert all(ob.Geometry.IsValid for ob in check.Objects)
su.SUTerminate()
for ext,d in [('skp','07_SketchUp'),('3dm','06_Rhino')]:shutil.copy2(O/d/f'Production_1QK_ARCH.{ext}',O/d/f'Production_1QK_Rebuild.{ext}')
print('Default views now show the whole building and site; native object validity unchanged')
