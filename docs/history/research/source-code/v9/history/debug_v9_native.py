import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import export_v5 as ex,numpy as np,rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid');S=json.loads((O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));changed=set(json.loads((O/'02_Data/V9_Changed_Nodes.json').read_text())['changed']);bad=[]
for e in S['elements']:
 if e['name'] not in changed:continue
 for i,p in enumerate(e['parts']):
  try:ex.native(p['geometry'])
  except Exception as err:
   g=p['geometry'];v,f,_,_=ex.solid_data(g);m=rh.Mesh();m.Vertices.UseDoublePrecisionVertices=True
   for q in v:m.Vertices.AddPoint3d(*map(float,q))
   for face in f:
    if len(face)<=4:m.Faces.AddFace(*face)
    else:
     for t in ex.triangulate(v[face]):m.Faces.AddFace(*[face[j] for j in t])
   m.Normals.ComputeNormals();m.Compact();b=rh.Brep.CreateFromMesh(m,True)
   row={'name':e['name'],'part':i,'type':g['type'],'error':str(err),'double_brep_exists':b is not None,'double_mesh_valid':m.IsValid,'double_mesh_closed':m.IsClosed,'vertices':len(v),'faces':len(f)};bad.append(row);print(row,flush=True)
(O/'06_Report/Native_Conversion_Repair_Diagnostic.json').write_text(json.dumps(bad,indent=2),encoding='utf-8');print('Failed default native parts',len(bad),flush=True)
