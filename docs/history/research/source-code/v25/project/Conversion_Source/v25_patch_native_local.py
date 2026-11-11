from v25_rhino_common import *
import json,time,hashlib
O=Path('E:/jz/JIA/Rebuild_V25');D=W/'v25';idx=json.loads((D/'Export_Index.json').read_text('utf8'));repair=json.loads((D/'Coplanar_Cleanup.json').read_text('utf8'));core=start()
try:
 b=bridge();p=O/'Rhino/Architecture_Complete_V25.3dm';f=Rhino.FileIO.File3dm.Read(str(p));changes=0
 for ob in list(f.Objects):
  a=ob.Attributes;i=int(a.GetUserString('V25_PartIndex'));x=idx[i]
  if x['source_object']==repair['source_object'] and x['material']==repair['material_key']:
   assert call(b,'Hash',ob.Geometry)==repair['final_pass_original_geometry_sha256'];at=a.Duplicate();oid=at.ObjectId;m=call(b,'Read',x['file']);assert m.IsValid and call(b,'Hash',m)==x['sha256'];at.SetUserString('V25_BinaryGeometrySHA256',x['sha256']);at.SetUserString('V25_GeometryMethod',x['geometry_method']);assert f.Objects.Delete(oid);assert f.Objects.AddMesh(m,at)==oid;m.Dispose();at.Dispose();changes+=1
 assert changes==1;temp=p.with_name('_Building_LOCAL.3dm');print('WRITE_FINAL_LOCAL_FOOT_REPAIR',flush=True);assert f.Write(str(temp),8);temp.replace(p);print('FINAL_LOCAL_FOOT_REPAIR_SAVED',p.stat().st_size,flush=True)
finally:core.Dispose()
