import json,sys
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import export_v5 as ex, rhino3dm as rh,numpy as np
O=Path(__file__).parent
M=json.loads((O/'Mutation.json').read_text(encoding='utf8'))
S=json.loads(Path('E:/jz/JIA/Rebuild_V10_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf8'))
nodes=[];F=rh.File3dm();F.Settings.ModelUnitSystem=rh.UnitSystem.Meters;F.Settings.ModelAbsoluteTolerance=.001
ly=rh.Layer();ly.Name='V11_PAVILION';li=F.Layers.Add(ly);mids={}
for name,d in S['materials'].items():
    m=rh.Material();m.Name=name;m.DiffuseColor=(*d['color'],255);m.ToPhysicallyBased();m.PhysicallyBased.Roughness=d['roughness'];m.PhysicallyBased.Metallic=d.get('metallic',0);mids[name]=F.Materials.Add(m)
def native(g,m):
    if g['type'] in ['box','cylinder','prism']:return ex.native(g)
    v,fs,_,_=ex.solid_data(g);me=rh.Mesh();me.Vertices.UseDoublePrecisionVertices=True
    for q in v:me.Vertices.AddPoint3d(*map(float,q))
    for f in fs:
        if len(f)<=4:me.Faces.AddFace(*f)
        else:
            for t in ex.triangulate(v[f]):me.Faces.AddFace(*[f[i] for i in t])
    me.Normals.ComputeNormals();me.Compact();assert me.IsValid and me.IsClosed
    if m=='M_Roof':return me
    b=rh.Brep.CreateFromMesh(me,True)
    if not b:raise ValueError(('failed native conversion',CURRENT_NAME))
    return b
checks=[]
for e in M['replace']+M['add']:
    by={};gr=rh.Group();gr.Name=e['name'];gi=len(F.Groups);F.Groups.Add(gr)
    for j,part in enumerate(e['parts']):
        CURRENT_NAME=e['name']+'__'+str(j)
        g=native(part['geometry'],part['material']);at=rh.ObjectAttributes();at.Name=e['name']+'__'+str(j+1);at.LayerIndex=li;at.MaterialIndex=mids[part['material']];at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.AddToGroup(gi)
        at.SetUserString('V11_Element',e['name']);at.SetUserString('V11_Part_Index',str(j));at.SetUserString('Source',e['source']);at.SetUserString('Status',e['status']);F.Objects.Add(g,at)
        checks.append(dict(name=at.Name,type=type(g).__name__,valid_before_kernel=g.IsValid,closed_manifold_source=True))
        v,fs,_,_=ex.solid_data(part['geometry']);d=by.setdefault(part['material'],dict(name=e['name']+'__'+part['material'],vertices=[],faces=[],material=part['material']));off=len(d['vertices']);d['vertices']+=v.tolist();d['faces']+=[[int(k)+off for k in f] for f in fs]
    nodes+=list(by.values())
assert F.Write(str(O/'V11_Pavilion_LOCAL_Review.3dm'),8)
(O/'Preview_Mesh.json').write_text(json.dumps(dict(nodes=nodes,materials=S['materials']),separators=(',',':')),encoding='utf8')
(O/'Native_Geometry_QA.json').write_text(json.dumps(dict(status='PENDING_KERNEL',parts=len(checks),checks=checks,coordinate='LOCAL, metres; this is isolated review geometry, not ENU delivery'),indent=2),encoding='utf8')
print('Native pavilion written; kernel flags pending',len(checks),'objects',flush=True)
