from v25_rhino_common import *
import json,hashlib
core=start()
try:
 b=bridge();idx=json.loads((W/'v25/Export_Index.json').read_text('utf8'));mats=json.loads((W/'v25/Material_Index.json').read_text('utf8'));tex=json.loads((W/'v25/Texture_Index.json').read_text('utf8'))
 print('MATERIAL_SAMPLE',json.dumps(mats[0],ensure_ascii=False),flush=True);print('TEXTURE_SAMPLE',json.dumps(tex[0],ensure_ascii=False),flush=True)
 f=Rhino.FileIO.File3dm();m=Rhino.DocObjects.Material();m.Name='Test';m.ToPhysicallyBased();f.Materials.Add(m);l=Rhino.DocObjects.Layer();l.Name='Test';f.Layers.Add(l)
 print('INDEX',m.Index,f.Materials.Count,l.Index,f.Layers.Count,flush=True)
 gi=f.AllGroups.AddGroup();g=f.AllGroups.FindIndex(gi);g.Name='TestGroup';print('GROUP',gi,g.Index,f.AllGroups.Count,flush=True)
 mesh=call(b,'Read',idx[0]['file']);print('MESH',mesh.IsValid,call(b,'Hash',mesh)==idx[0]['sha256'],flush=True)
 a=Rhino.DocObjects.ObjectAttributes();a.Name='Test';a.LayerIndex=f.Layers.Count-1;a.MaterialIndex=f.Materials.Count-1;a.MaterialSource=Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject;a.AddToGroup(gi);f.Objects.AddMesh(mesh,a)
 vi=Rhino.DocObjects.ViewInfo();vi.Name='Perspective';vp=vi.Viewport;vp.SetCameraLocation(Rhino.Geometry.Point3d(10,-20,15));vp.SetCameraDirection(Rhino.Geometry.Vector3d(-10,20,-15));vp.SetCameraUp(Rhino.Geometry.Vector3d(0,0,1));vp.SetFrustum(-.018,.018,-.012,.012,.05,2000);vp.IsPerspectiveProjection=True;vp.SetScreenPort(0,1600,0,1000,0,1000);vp.TargetPoint=Rhino.Geometry.Point3d(0,0,0);print('VIEW',vp.IsValid,vp.IsValidCamera,vp.IsValidFrustum,flush=True);f.Views.Add(vi);f.NamedViews.Add(vi)
 print('EMBED',dir(f.EmbeddedFiles),flush=True)
 p=tex[0].get('file',tex[0].get('path'));print('TEXTUREPATH',p,flush=True);f.EmbeddedFiles.Add(p)
 f.Strings.SetString('Rebuild_V25','Smoke','true');out=str(W/'v25/Smoke.3dm');print('WRITE',f.Write(out,8),flush=True);f.Dispose();f=Rhino.FileIO.File3dm.Read(out)
 for e in f.EmbeddedFiles:
  print('EMBEDDED',e.Filename,flush=True);dest=str(W/'v25/smoke_texture.bin');print('EXTRACT',e.SaveToFile(dest),hashlib.sha256(Path(dest).read_bytes()).hexdigest(),flush=True)
 print('READBACK',len(list(f.Objects)),len(list(f.Materials)),f.Settings.ModelUnitSystem,call(b,'Hash',list(f.Objects)[0].Geometry)==idx[0]['sha256'],flush=True)
finally:core.Dispose()
