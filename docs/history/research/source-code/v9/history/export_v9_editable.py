import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import export_v5 as ex
import rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid')
ex.OUT=O/'08_Editable_Source';ex.SCENE=json.loads((ex.OUT/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));ex.MATS=ex.SCENE['materials']
changed=set(json.loads((O/'02_Data/V9_Changed_Nodes.json').read_text())['changed'])
changed_polyhedra={id(p['geometry']) for e in ex.SCENE['elements'] if e['name'] in changed for p in e.get('parts',[]) if p['geometry']['type']=='polyhedron'}
original_native=ex.native;double_repairs=[]
def native_with_double_fallback(g):
 if id(g) not in changed_polyhedra:return original_native(g)
 if g['type']=='polyhedron':
  v,f,_,_=ex.solid_data(g);m=rh.Mesh();m.Vertices.UseDoublePrecisionVertices=True
  for q in v:m.Vertices.AddPoint3d(*map(float,q))
  for face in f:
   if len(face)<=4:m.Faces.AddFace(*face)
   else:
    for t in ex.triangulate(v[face]):m.Faces.AddFace(*[face[j] for j in t])
  m.Normals.ComputeNormals();m.Compact();b=rh.Brep.CreateFromMesh(m,True)
  if b is None:raise
  assert m.IsValid and m.IsClosed
  double_repairs.append({'vertices':len(v),'faces':len(f),'repair':'Original double precision coordinates; triangulate multi-sided caps in their actual 3D plane rather than XY projection; no parameter coordinates changed'})
  return b
ex.native=native_with_double_fallback
qa=ex.make_rhino('ARCH')
qa['double_precision_conversion_repairs']=double_repairs
(O/'06_Report/Editable_Local_Native_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
assert not qa['unexpected_open_solids']
print('RhinoCommon tolerance initialization required for faceted Breps before final QA',flush=True)
