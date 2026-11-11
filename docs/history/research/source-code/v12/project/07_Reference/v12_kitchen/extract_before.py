import sys,json,hashlib,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'netlibs'))
import rhinoinside
rhinoinside.__parse_rhino_id(r'D:\AJAVIS01\RHINO8\RUNING\System').load(rhinoinside.__parse_framework_id('net48'))
import clr;clr.AddReference('RhinoCommon');import Rhino,System
O=Path(__file__).parent;src=Path(r'E:\CODEXdata\before\厨房\厨房_V17_实景檐廊挂落_精细木窗_Rhino8.3dm')
core=Rhino.Runtime.InProcess.RhinoCore(System.Array[System.String](['/nosplash','/notemplate']),Rhino.Runtime.InProcess.WindowStyle.NoWindow)
try:
 f=Rhino.FileIO.File3dm.Read(str(src));rows=[];skip=[]
 keep={'03','05','06','07','15','16','18','19','20','21','22','25','26','27','28','29','30','31','32','33','34','35'}
 mp=Rhino.Geometry.MeshingParameters();mp.Tolerance=.5;mp.MinimumEdgeLength=.25;mp.MaximumEdgeLength=60;mp.RefineGrid=True;mp.GridAngle=math.radians(7);mp.SimplePlanes=True;mp.JaggedSeams=False
 for ob in f.Objects:
  g=ob.Geometry;name=ob.Attributes.Name or '';layer=f.AllLayers.FindIndex(ob.Attributes.LayerIndex).Name;code=layer.split('_')[0]
  if code not in keep and not(code=='04' and not name.startswith('PURLIN_')):continue
  if name.startswith(('CEILING_BATTEN_','CORRIDOR_TIE_','檐廊_椽下沿柱列长檩','檐廊_抱檩节点','中柱_椽底托梁','灯具_')):
   skip.append({'name':name,'reason':'Old symmetric roof-specific element replaced with fitted exposed V12 roof frame'});continue
  if isinstance(g,Rhino.Geometry.Mesh):mesh=g.DuplicateMesh()
  elif isinstance(g,Rhino.Geometry.Brep):
   g.SetTolerancesBoxesAndFlags();mesh=Rhino.Geometry.Mesh();ms=Rhino.Geometry.Mesh.CreateFromBrep(g,mp)
   for mm in ms:mesh.Append(mm)
  else:skip.append({'name':name,'reason':'Non-solid helper'});continue
  mesh.Vertices.CombineIdentical(True,True);mesh.Weld(math.pi);mesh.Faces.ConvertQuadsToTriangles();mesh.Compact();mesh.Normals.ComputeNormals()
  if not mesh.IsValid or not mesh.IsClosed:
   skip.append({'name':name,'reason':'Invalid/open donor detail excluded','valid':mesh.IsValid,'closed':mesh.IsClosed});continue
  mat=f.AllMaterials.FindIndex(ob.Attributes.MaterialIndex)
  rows.append({'name':name,'layer':layer,'material':mat.Name if mat else 'HONEY_WOOD','geometry':{'type':'polyhedron','vertices':[[v.X*.001,v.Y*.001,v.Z*.001] for v in mesh.Vertices],'faces':[[ff.A,ff.B,ff.C] for ff in mesh.Faces]},'source_id':str(ob.Attributes.ObjectId)})
 mats={}
 for ma in f.AllMaterials:
  c=ma.DiffuseColor;mats[ma.Name]={'color':[c.R,c.G,c.B],'roughness':.38 if 'WOOD' in ma.Name else .6,'alpha':1-ma.Transparency,'metallic':.4 if 'METAL' in ma.Name else 0}
 report={'status':'PASS','source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'units_source':'Millimeters','tessellation_tolerance_m':.0005,'included_parts':len(rows),'excluded':skip,'materials':mats,'parts':rows}
 (O/'Before_Donor.json').write_text(json.dumps(report,ensure_ascii=False),encoding='utf8');print('closed donor parts',len(rows),'skipped',len(skip),flush=True)
finally:core.Dispose()
