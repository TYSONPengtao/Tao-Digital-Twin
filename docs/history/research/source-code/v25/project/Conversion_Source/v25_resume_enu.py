# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
from v25_rhino_common import *
import json,hashlib,math,time
O=Path('E:/jz/JIA/Rebuild_V25');D=W/'v25';T=time.monotonic();report=json.loads((O/'Reports/V25_Rhino_Build_QA.json').read_text('utf8'));idx=json.loads((D/'Export_Index.json').read_text('utf8'));report['triangles']=sum(x['triangles'] for x in idx);report['coplanar_internal_backfaces_removed']=json.loads((D/'Coplanar_Cleanup.json').read_text('utf8'))['faces_removed']
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
core=start()
try:
 b=bridge();p=O/'Rhino/Architecture_Complete_V25.3dm';f=Rhino.FileIO.File3dm.Read(str(p));assert f.Objects.Count==len(idx)
 for ob in f.Objects:
  i=int(ob.Attributes.GetUserString('V25_PartIndex'));assert call(b,'Hash',ob.Geometry)==idx[i]['sha256'];assert ob.Geometry.IsValid
 report['files']=[{'file':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}];print('FINAL_LOCAL_EXACT_HASHES_PASS',len(idx),flush=True)
 tr=Rhino.Geometry.Transform.Identity;ang=math.radians(19.65);tr.M00=math.cos(ang);tr.M01=-math.sin(ang);tr.M10=math.sin(ang);tr.M11=math.cos(ang);tr.M03=-3.45191261;tr.M13=-3.90043098;tr.M23=TAO_PRIVATE_SITE_002
 for ob in list(f.Objects):
  m=ob.Geometry.DuplicateMesh();a=ob.Attributes.Duplicate();oid=a.ObjectId;assert m.Transform(tr);a.SetUserString('V25_Coordinates','Original ENU project alignment, metres. Vertical offset +1303.75 m. Not independent survey control.');assert f.Objects.Delete(oid);assert f.Objects.AddMesh(m,a)==oid;m.Dispose();a.Dispose()
 def transformed_view(vi):
  v=vi.Viewport;assert v.TransformCamera(tr);rv=Rhino.Display.RhinoViewport();assert rv.SetViewProjection(v,True);n=Rhino.DocObjects.ViewInfo(rv);n.Name=vi.Name;return n
 nv=[transformed_view(v) for v in f.NamedViews];vv=[transformed_view(v) for v in f.Views];f.NamedViews.Clear();f.Views.Clear()
 for v in nv:f.NamedViews.Add(v)
 for v in vv:f.Views.Add(v)
 f.Strings.SetString('Rebuild_V25','Coordinates','ENU:TAO_PRIVATE_SITE_003,98.68275. Original project transform; not independently surveyed.');f.Strings.SetString('Rebuild_V25','LOCAL_to_ENU',json.dumps([[tr[i,j] for j in range(4)] for i in range(4)]));f.Strings.SetString('Rebuild_V25','Door_Hinges_Note','Door_Hinges_LOCAL remains original LOCAL; use LOCAL_to_ENU to transform pivots.')
 p=O/'Rhino/Architecture_Complete_V25_ALIGNED_ENU.3dm';temp=p.with_name('_Building_ENU.3dm');print('WRITE_CORRECTED_ENU',flush=True);assert f.Write(str(temp),8);temp.replace(p);report['files'].append({'file':str(p),'bytes':p.stat().st_size,'sha256':sha(p)});report['seconds_final_enu_rebuild']=time.monotonic()-T;report['source_unchanged']=sha(Path(json.loads((D/'Export_Report.json').read_text('utf8'))['source']))==report['source_sha256'];assert report['source_unchanged']
 for p in [O/'Reports/V25_Rhino_Build_QA.json',D/'Rhino_Build_Report.json']:p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print('FINAL_ENU_BUILD_OK',report['seconds_final_enu_rebuild'],flush=True)
finally:core.Dispose()
