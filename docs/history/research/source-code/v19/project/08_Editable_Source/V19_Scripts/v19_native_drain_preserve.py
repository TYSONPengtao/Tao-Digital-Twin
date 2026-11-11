"""Preserve native drain cavities while changing only the road shoulder material."""
import sys,json,math,ast,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,manifold3d as mf,export_v5 as ex
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
O=Path(r'E:/jz/JIA/Rebuild_V19');B=Path(r'E:/jz/JIA/Rebuild_V18');D=W/'v19';P=O/'04_Rhino/Architecture_Complete_V19_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));BF=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V18_ALIGNED_ENU.3dm'));S=json.loads((O/'08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'));ex.SCENE=S;Q=json.loads((O/'08_Editable_Source/Mutation_V19.json').read_text(encoding='utf8'));I=json.loads((O/'02_Data/Native_Readback_Index_V19.json').read_text(encoding='utf8'));AQ=json.loads((O/'06_Report/V19_Assembly_QA.json').read_text(encoding='utf8'));proof=json.loads((D/'Design_Control.json').read_text(encoding='utf8'));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));ang=math.radians(C['rotation_deg']);R=np.array([[math.cos(ang),-math.sin(ang),0],[math.sin(ang),math.cos(ang),0],[0,0,1]]);origin=np.array(C['origin']);NM=json.loads((D/'Materials.json').read_text(encoding='utf8'))
for file,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold']),('v19_design.py',['fromman']),('v19_native_final_corrections.py',['native_man']),('v19_assemble.py',['gh','uv_for','make'])]:
 t=ast.parse((W/file).read_text(encoding='utf8'));ns=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in names]
 if file=='v19_assemble.py':ns=[n for n in t.body if (isinstance(n,ast.FunctionDef) and n.name in names) or (isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id in ['FD','routes'] for x in n.targets)) or (isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='kind')]
 exec(compile(ast.Module(ns,type_ignores=[]),'<helpers>','exec'))
def node(model,n):return [ob for ob in model.Objects if ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__')]
def addall(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
n='SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE';original=addall([native_man(ob)[0] for ob in node(BF,n)]);segs=json.loads((W/'v16/Drain_Segments.json').read_text(encoding='utf8'));masks=[]
for s in segs:
 if not s['roadzone']:continue
 a,b=np.array(s['a']),np.array(s['b']);oa=(np.array(s['outer_a'])-a)/1.05;ob=(np.array(s['outer_b'])-b)/1.05;masks.append(Polygon([a+oa*.431,b+ob*.431,b+ob*1.052,a+oa*1.052]))
mask=unary_union(masks).buffer(0);clips=[]
for p in ([mask] if mask.geom_type=='Polygon' else mask.geoms):
 p=orient(p,1);clips.append(manifold({'type':'prism_holes','outer':list(p.exterior.coords)[:-1],'holes':[list(r.coords)[:-1] for r in p.interiors],'z':-8,'height':12}))
e=next(e for e in Q['replace'] if e['name']==n);baseobjs=node(BF,n);e['parts']=[]
for ob in baseobjs:
 a,v,f=native_man(ob);e['parts'].append({'geometry':{'type':'polyhedron','vertices':v.tolist(),'faces':f.tolist()},'material':'M_V19_Perimeter_Road_Shoulder'})
e['v19_native_drain_voids_preserved']=True;e['v19_note']='Exact original native drainage mesh preserved, including its cavities and survey tie; entire drainage/shoulder solid toned with weathered fine-aggregate concrete';oldobjs=node(F,n);ids={str(ob.Attributes.Id) for ob in oldobjs};AQ['created']=[r for r in AQ['created'] if r['id'] not in ids];AQ['deleted']+=[{'id':str(ob.Attributes.Id),'name':ob.Attributes.Name,'reason':'Superseded drain partition draft'} for ob in oldobjs]
for ob in oldobjs:F.Objects.Delete(ob.Attributes.Id)
gr=rh.Group();gr.Name=n;gid=len(F.Groups);F.Groups.Add(gr)
for j,p in enumerate(e['parts']):
 mm=baseobjs[j].Geometry;assert mm.IsValid and mm.IsClosed;at=rh.ObjectAttributes();at.Name=f'{n}__{j+1}';at.LayerIndex=next(l.Index for l in F.Layers if l.Name=='60_SITE');at.AddToGroup(gid);at.MaterialIndex=next(i for i,m in enumerate(F.Materials) if m.Name==p['material']);at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=F.Materials[at.MaterialIndex].DiffuseColor;at.SetUserString('V19_Node',n);at.SetUserString('V19_Reference','Retained V18 actual native drain and survey tie; source voids preserved');ident=F.Objects.Add(mm,at);AQ['created'].append({'id':str(ident),'name':at.Name,'node':n,'geometry_hash':gh(mm),'closed_expected':True})
assert [gh(ob.Geometry) for ob in node(F,n)]==[gh(ob.Geometry) for ob in baseobjs];dv=0.;print('NATIVE DRAIN EXACT GEOMETRY HASH PRESERVED',flush=True)
S['elements']=[e if x['name']==n else x for x in S['elements']];sp=O/'08_Editable_Source/Architecture_Scene_V19.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V19_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();assert F.Write(str(P),8);r=next(r for r in I if r['name']==n);vv=[];ff=[];uv=[];nn=[];mi=[];mats=[];oo=node(F,n)
for ob in oo:
 mm=ob.Geometry;mat=F.Materials[ob.Attributes.MaterialIndex].Name
 if mat not in mats:mats.append(mat)
 off=len(vv);vv.extend(((np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R).tolist());uv.extend([[p.X,p.Y] for p in mm.TextureCoordinates]);nn.extend((np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R).tolist())
 for f in mm.Faces:ff.append((np.array(f[:3])+off).tolist());mi.append(mats.index(mat))
np.savez_compressed(O/'02_Data'/r['file'],vertices=np.array(vv),faces=np.array(ff,np.int32),uv=np.array(uv),normals=np.array(nn),material_ids=np.array(mi,np.int32));r.update(materials=mats,triangles=len(ff),native_objects=len(oo),element={k:v for k,v in e.items() if k!='parts'})
for fn in ['Native_Readback_Index_V19.json','Modeled_Index_V19.json']:(O/'02_Data'/fn).write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf8')
AQ.update(status='AWAITING_FINAL_DRAIN_READBACK',native_objects=len(F.Objects));proof['native_drain_exact_geometry_symmetric_volume_m3']=dv;proof['native_drain_internal_voids_preserved']=True;proof['native_drain_finish']='Uniform weathered fine-aggregate concrete on the exact original native solid; no geometric material partition retained'
(O/'06_Report/V19_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8')
for fp in [D/'Design_Control.json',O/'06_Report/V19_Design_Control.json']:fp.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
for fp in [D/'Mutation.json',O/'08_Editable_Source/Mutation_V19.json']:fp.write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
print('V19 NATIVE DRAIN PRESERVATION SAVED',P.stat().st_size,flush=True)
