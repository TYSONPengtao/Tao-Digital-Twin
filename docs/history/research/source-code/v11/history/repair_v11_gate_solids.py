"""Retain exact source geometry for six faceted solids rejected by Rhino Brep flags."""
import sys,json,hashlib,collections
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import export_v5 as ex,numpy as np,rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid');path=O/'04_Rhino/V11_Changed_Wall_Solids_LOCAL.3dm'
S=json.loads((O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf8'));ex.SCENE=S
E={e['name']:e for e in S['elements']};F=rh.File3dm.Read(str(path))
names=['SITE_SW_GATE_POST_0_CORE__1','SITE_SW_GATE_POST_0_EXPOSED_BRICK_UNITS__331','SITE_SW_GATE_POST_0_EXPOSED_BRICK_UNITS__354','SITE_SW_GATE_POST_1_CORE__1','SITE_SW_GATE_POST_1_EXPOSED_BRICK_UNITS__356','SITE_SW_GATE_WALL_ENDPOINT_CONNECTOR_1__1'];records=[]
for ob in list(F.Objects):
 if ob.Attributes.Name not in names:continue
 at=ob.Attributes;node=at.GetUserString('V11_Element');idx=int(at.GetUserString('V11_Part_Index'));e=E[node];p=ex.expand_parts(e)[idx];v,faces,_,_=ex.solid_data(p['geometry']);m=rh.Mesh();m.Vertices.UseDoublePrecisionVertices=True
 for q in v:m.Vertices.AddPoint3d(*map(float,q))
 for f in faces:
  if len(f)<=4:m.Faces.AddFace(*f)
  else:
   for t in ex.triangulate(v[f]):m.Faces.AddFace(*[f[j] for j in t])
 m.Normals.ComputeNormals();m.Compact();assert m.IsValid and m.IsClosed,at.Name;assert m.Transform(ex.rh_transform(e));uid=at.Id
 at.SetUserString('Native_Representation','Closed double-precision mesh; identical source vertices/faces; faceted Brep closure flags rejected by Rhino tolerance')
 F.Objects.Delete(uid);assert F.Objects.Add(m,at)==uid
 records.append({'name':at.Name,'vertices':len(m.Vertices),'faces':len(m.Faces),'uuid_preserved':str(uid),'is_valid':m.IsValid,'is_closed':m.IsClosed,'geometry_source':'Exact frozen Mutation / Scene part, no remesh or simplified geometry'})
assert len(records)==len(names);assert F.Write(str(path),8)
types=collections.Counter(type(ob.Geometry).__name__ for ob in F.Objects)
p=O/'06_Report/Changed_CAD_Conversion_QA.json';r=json.loads(p.read_text(encoding='utf8'));r['types']=dict(types);r['exact_source_closed_mesh_fallbacks']=records;p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print('Exact-source closure fallback',len(records),'parts',dict(types),flush=True)
