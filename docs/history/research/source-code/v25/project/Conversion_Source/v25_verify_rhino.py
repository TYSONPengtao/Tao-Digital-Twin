# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
from v25_rhino_common import *
import json,hashlib,time,math
T=time.monotonic();O=Path('E:/jz/JIA/Rebuild_V25');D=W/'v25';idx=json.loads((D/'Export_Index.json').read_text('utf8'));build=json.loads((O/'Reports/V25_Rhino_Build_QA.json').read_text('utf8'));textures=json.loads((D/'Texture_Index.json').read_text('utf8'));mats={x['key']:x for x in json.loads((D/'Material_Index.json').read_text('utf8'))};expectedtex={str(Path(t['file'])):t for t in textures};expectedgroups={g for x in idx for g in x['group_path']};checks=[]
def check(name,passed,detail=None):
 checks.append({'name':name,'passed':bool(passed),'detail':detail});assert passed,(name,detail)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
core=start()
try:
 b=bridge()
 for enu in [False,True]:
  path=O/'Rhino'/('Architecture_Complete_V25_ALIGNED_ENU.3dm' if enu else 'Architecture_Complete_V25.3dm');f=Rhino.FileIO.File3dm.Read(str(path));tag='ENU' if enu else 'LOCAL';print('READ',tag,flush=True)
  check(tag+'_units_metres',f.Settings.ModelUnitSystem==Rhino.UnitSystem.Meters);check(tag+'_part_count',f.Objects.Count==len(idx),f.Objects.Count);check(tag+'_materials',f.Materials.Count==build['materials']);check(tag+'_groups',set(g.Name for g in f.AllGroups)==expectedgroups);check(tag+'_layers',len(list(f.Layers))==len(build['layers']))
  allvalid=True;geometryhash=0;faces=0;vertices=0;areas=0;maxerror=[0.,0.,0.,0.];seen=set();bounds=[]
  tr=Rhino.Geometry.Transform.Identity;ang=math.radians(19.65);tr.M00=math.cos(ang);tr.M01=-math.sin(ang);tr.M10=math.sin(ang);tr.M11=math.cos(ang);tr.M03=-3.45191261;tr.M13=-3.90043098;tr.M23=TAO_PRIVATE_SITE_002
  for ob in f.Objects:
   a=ob.Attributes;i=int(a.GetUserString('V25_PartIndex'));x=idx[i];seen.add(i);m=ob.Geometry;allvalid=allvalid and m.IsValid;faces+=m.Faces.Count;vertices+=m.Vertices.Count;areas+=call(b,'Area',m)
   assert m.Faces.Count==x['triangles'] and m.Vertices.Count==x['vertices'];assert a.MaterialSource==Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject
   assert f.Materials[a.MaterialIndex].Name==x['material'];assert f.Layers[a.LayerIndex].FullPath=='::'.join(x['layer_path'])
   assert set(f.AllGroups.FindIndex(g).Name for g in a.GetGroupList())==set(x['group_path'])
   if enu:
    err=list(call(b,'CompareTransformed',m,x['file'],tr));maxerror=[max(c,d) for c,d in zip(maxerror,err)]
   else:
    assert call(b,'Hash',m)==x['sha256'],('LOCAL hash',i);geometryhash+=1
   if i%400==0:print('VERIFY',tag,i,round(time.monotonic()-T,1),flush=True)
  check(tag+'_all_native_meshes_valid',allvalid);check(tag+'_all_parts_represented',seen==set(range(len(idx))));check(tag+'_triangle_count',faces==build['triangles'],faces)
  if enu:check(tag+'_all_vertices_normals_uv_faces_preserved',maxerror[0]<1e-8 and maxerror[1]<2e-6 and maxerror[2]==0 and maxerror[3]==0,maxerror)
  else:check(tag+'_exact_mesh_uv_normal_hashes',geometryhash==len(idx),geometryhash)
  expectarea=sum(x['area_m2'] for x in idx);check(tag+'_area_preserved',abs(areas-expectarea)<1e-5,{'source':expectarea,'native':areas,'difference':areas-expectarea})
  embedded={};dest=D/'Extracted';dest.mkdir(exist_ok=True)
  for e in f.EmbeddedFiles:
   key=str(Path(e.Filename));record=expectedtex[key];p=dest/Path(key).name;assert e.SaveToFile(str(p));h=sha(p);assert h==record['sha256'];embedded[key]=h
  check(tag+'_embedded_texture_bytes',len(embedded)==build['embedded_textures'],len(embedded))
  for material in f.Materials:
   s=mats[material.Name]
   for slot,tt in [('base_texture',Rhino.DocObjects.TextureType.Bitmap),('bump_texture',Rhino.DocObjects.TextureType.Bump)]:
    if s.get(slot):
     tx=material.GetTexture(tt);assert tx and str(Path(tx.FileName)) in embedded and tx.Enabled,(tag,material.Name,slot)
  check(tag+'_all_referenced_textures_embedded',True);check(tag+'_named_views',len(list(f.NamedViews))==build['named_views'] and all(v.Viewport.IsValid for v in f.NamedViews),len(list(f.NamedViews)))
  c=next(c for c in json.loads((D/'Camera_Index.json').read_text('utf8')) if c['name']=='V24_37_02_House_And_PTJIA6');p=Rhino.Geometry.Point3d(*c['location'])
  if enu:p.Transform(tr)
  actual=list(f.Views)[0].Viewport.CameraLocation;check(tag+'_default_view_coordinates',p.DistanceTo(actual)<1e-8,[list(c['location']),[actual.X,actual.Y,actual.Z]])
  f.Dispose();System.GC.Collect();System.GC.WaitForPendingFinalizers()
 check('V24_37_source_unchanged',sha(json.loads((D/'Export_Report.json').read_text())['source'])==build['source_sha256'])
 report={'status':'PASS_NATIVE_RHINO_READBACK','checks':checks,'total_checks':len(checks),'failures':[],'files':build['files'],'native_kernel':str(Rhino.RhinoApp.Version),'seconds':time.monotonic()-T};(O/'Reports/V25_Rhino_Readback_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('V25_NATIVE_READBACK_OK',len(checks),report['seconds'],flush=True)
finally:core.Dispose()
