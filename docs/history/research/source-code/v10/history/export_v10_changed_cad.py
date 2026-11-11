import sys,json,collections
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import export_v5 as ex,numpy as np,rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid')
ex.SCENE=json.loads((O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));ex.MATS=ex.SCENE['materials']
changed=set(json.loads((O/'02_Data/V10_Changed_Nodes.json').read_text())['changed'])
F=rh.File3dm();F.Settings.ModelUnitSystem=rh.UnitSystem.Meters;F.Settings.ModelAbsoluteTolerance=.001
ly=rh.Layer();ly.Name='60_SITE';li=F.Layers.Add(ly);mids={}
for name,spec in ex.MATS.items():
 m=rh.Material();m.Name=name;m.DiffuseColor=(*spec['color'],255);m.ToPhysicallyBased();m.PhysicallyBased.Roughness=spec['roughness'];m.PhysicallyBased.Metallic=spec.get('metallic',0);mids[name]=F.Materials.Add(m)
stats=collections.Counter();count=0
def native(g,material):
 mesh_solid=material=='M_Roof'
 if not mesh_solid and g['type'] in ['box','cylinder','lathe','prism_holes']:return ex.native(g)
 if g['type']=='prism':
  v,f,p,vec=ex.solid_data(g);normal=vec/np.linalg.norm(vec)
  if not mesh_solid and max(abs((p-p[0])@normal))<1e-7:return ex.native(g)
 else:v,f,_,_=ex.solid_data(g)
 m=rh.Mesh();m.Vertices.UseDoublePrecisionVertices=True
 for q in v:m.Vertices.AddPoint3d(*map(float,q))
 for face in f:
  if len(face)<=4:m.Faces.AddFace(*face)
  else:
   for t in ex.triangulate(v[face]):m.Faces.AddFace(*[face[j] for j in t])
 m.Normals.ComputeNormals();m.Compact();assert m.IsValid and m.IsClosed
 if mesh_solid:return m
 b=rh.Brep.CreateFromMesh(m,True);assert b is not None;return b
for e in ex.SCENE['elements']:
 if e['name'] not in changed:continue
 group=rh.Group();group.Name=e['name'];gi=len(F.Groups);F.Groups.Add(group)
 for j,p in enumerate(ex.expand_parts(e)):
  g=native(p['geometry'],p['material']);g.Transform(ex.rh_transform(e));at=rh.ObjectAttributes();at.Name=e['name']+'__'+str(j+1);at.LayerIndex=li;at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.MaterialIndex=mids[p['material']];at.AddToGroup(gi)
  for k in ['source','confidence','family','status','classification']:at.SetUserString(k,str(e.get(k,'')))
  at.SetUserString('Parameters',json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False));at.SetUserString('V10_Element',e['name']);at.SetUserString('V10_Part_Index',str(j));at.SetUserString('V10_Material',p['material']);F.Objects.Add(g,at);stats[type(g).__name__]+=1;count+=1
 print(e['name'],len(e.get('parts',[])),'CAD parts; cumulative',count,flush=True)
pth=O/'04_Rhino/V10_Changed_Wall_Solids_LOCAL.3dm';assert F.Write(str(pth),8)
save=O/'06_Report/Changed_CAD_Conversion_QA.json';save.write_text(json.dumps({'parts':count,'types':dict(stats),'double_precision_faceted_conversion':True,'ceramic_units':'Independent closed double-precision mesh solids; same source vertices/faces, avoids enormous one-Brep-face-per-triangle files','masonry_and_relief':'Native closed Breps/extrusions','kernel_validation_pending':True},indent=2),encoding='utf-8')
print('V10 changed solids',count,dict(stats),flush=True)
