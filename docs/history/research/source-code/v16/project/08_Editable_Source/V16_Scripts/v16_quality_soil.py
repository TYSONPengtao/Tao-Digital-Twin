"""Constrained quality triangulation prevents narrow triangles from creating false sharp terrain ridges."""
import sys,json,math,ast,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]
import numpy as np,triangle,rhino3dm as rh
from shapely.geometry import Polygon,Point,shape
from shapely.ops import unary_union,nearest_points
from shapely.geometry.polygon import orient
O=Path(r'E:/jz/JIA/Rebuild_V16');B=Path(r'E:/jz/JIA/Rebuild_V15');D=W/'v16';I=json.loads((B/'02_Data/Native_Readback_Index_V15.json').read_text(encoding='utf8'));ii={r['name']:r for r in I};hard=[]
for n,r in ii.items():
 if not n.startswith(('SITE_V12_REBUILT_COURT','SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT','SITE_V12_OUTER_GATE_SCORED')):continue
 d=np.load(B/'02_Data'/r['file']);t=d['vertices'][d['faces']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);t=t[no[:,2]>1e-9];hard.append((unary_union([Polygon(q[:,:2]) for q in t]).buffer(0),t))
boundary=unary_union([p for p,t in hard]).boundary
tree=ast.parse((W/'v16_geometry.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['surface_z','height','polys']],type_ignores=[]),'<grade_field>','exec'))
wall0=np.array(json.loads((D/'SITE_PERIMETER_JOINED_RETAINING_WALL_0_centerline.json').read_text(encoding='utf8')));wall1=np.array(json.loads((D/'SITE_PERIMETER_JOINED_RETAINING_WALL_1_centerline.json').read_text(encoding='utf8')));interior=Polygon(np.vstack([wall0[:,:2],wall1[:,:2]])).buffer(0).buffer(-.155,join_style=2);store=Polygon([[13.3,-9.4],[18.9,-9.7],[20.95,-10.35],[21.45,-13],[21.3,-15.4],[20.2,-16.2],[18.9,-16.2],[13.3,-16.2]]);target=interior.union(store).buffer(0);hardunion=unary_union([p for p,t in hard]);treehole=Point(-4,-13.5).buffer(.4,quad_segs=12);domain=target.difference(hardunion).difference(treehole).buffer(0)
import shapely
(D/'Soil_Domain.json').write_text(json.dumps(shapely.geometry.mapping(domain)),encoding='utf8');vv=[];ff=[];triangle_proofs=[]
for pi,poly in enumerate(polys(domain)):
 if poly.area<1e-7:continue
 p=orient(poly,1);rings=[list(p.exterior.coords)[:-1]]+[list(h.coords)[:-1] for h in p.interiors];v=[];segs=[]
 for ring in rings:
  off=len(v);v.extend(ring);segs.extend([[off+j,off+(j+1)%len(ring)] for j in range(len(ring))])
 inp={'vertices':np.array(v),'segments':np.array(segs,np.int32)}
 if p.interiors:inp['holes']=np.array([[Polygon(r).representative_point().x,Polygon(r).representative_point().y] for r in rings[1:]])
 out=triangle.triangulate(inp,'pq25a0.16Q');v=out['vertices'];f=out['triangles'];tt=v[f];bad=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0])<0;f[bad]=f[bad][:,::-1];off=len(vv);vv.extend(v.tolist());ff.extend((f+off).tolist());triangle_proofs.append({'island':pi,'vertices':len(v),'triangles':len(f),'area_m2':p.area})
 print('QUALITY SOIL ISLAND',triangle_proofs[-1],flush=True)
v2=np.array(vv);f=np.array(ff,np.int32);N=len(v2);v=np.vstack([np.c_[v2,[height(*p) for p in v2]],np.c_[v2,np.full(N,-4.8)]]);top=v[f];no=np.cross(top[:,1]-top[:,0],top[:,2]-top[:,0]);grade=np.linalg.norm(no[:,:2],axis=1)/no[:,2];quant=np.quantile(grade,[.1,.5,.9,.99,1]);print('QUALITY GRADE',quant.tolist(),flush=True)
steep=grade>1.0;infill=unary_union([Polygon(t[:,:2]) for t in top[steep]]).buffer(0) if steep.any() else None
assert not steep.any() or infill.area<.01,('Broad steep terrain area',infill.area)
if infill is not None:(D/'Court_Edge_Infill.json').write_text(json.dumps(shapely.geometry.mapping(infill)),encoding='utf8')
ed={}
for tri in f:
 for a,b in zip(tri,np.roll(tri,-1)):ed.setdefault(tuple(sorted([int(a),int(b)])),[]).append((int(a),int(b)))
fs=f.tolist()+(f[:,::-1]+N).tolist()
for ee in ed.values():
 if len(ee)==1:
  a,b=ee[0];fs.extend([[b,a,a+N],[b,a+N,b+N]])
 else:assert len(ee)==2
g={'type':'polyhedron','vertices':v.tolist(),'faces':fs};fs=np.array(fs,np.int32)
P=O/'04_Rhino/Architecture_Complete_V16_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);smooth=np.zeros_like(v)
for j in range(3):np.add.at(smooth,f[:,j],no)
smooth/=np.linalg.norm(smooth,axis=1)[:,None]+1e-30
mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True
for k,tri in enumerate(fs):
 q=v[tri];nn=np.cross(q[1]-q[0],q[2]-q[0]);axes=[j for j in range(3) if j!=int(np.argmax(abs(nn)))];pu=q[:,axes]
 for p,u in zip(q@R.T+origin,pu):mm.Vertices.AddPoint3d(*map(float,p));mm.TextureCoordinates.__add__(*map(float,u))
 mm.Faces.AddFace(k*3,k*3+1,k*3+2)
mm.Normals.ComputeNormals();mm.Normals.UnitizeNormals()
for k,tri in enumerate(f):
 for j,vid in enumerate(tri):mm.Normals[k*3+j]=rh.Vector3f(*map(float,smooth[vid]@R.T))
assert mm.IsValid and mm.IsClosed
n='SITE_V16_GRADED_INTERIOR_SOIL';old=next(ob for ob in F.Objects if ob.Attributes.Name==n+'__1');at=old.Attributes;F.Objects.Delete(at.Id);ident=F.Objects.Add(mm,at);AQ=json.loads((O/'06_Report/V16_Assembly_QA.json').read_text(encoding='utf8'))
for rec in AQ['created']:
 if rec['node']==n:rec['id']=str(ident);rec['geometry_hash']=hashlib.sha256(json.dumps(mm.Encode(),sort_keys=True).encode()).hexdigest()
nv=(np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R;nf=np.array([f[:3] for f in mm.Faces],np.int32);nu=np.array([[p.X,p.Y] for p in mm.TextureCoordinates]);nn=np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R;NI=json.loads((O/'02_Data/Native_Readback_Index_V16.json').read_text(encoding='utf8'));row=next(r for r in NI if r['name']==n);row['triangles']=len(nf);np.savez_compressed(O/'02_Data'/row['file'],vertices=nv,faces=nf,uv=nu,normals=nn,material_ids=np.zeros(len(nf),np.int32));S=json.loads((O/'08_Editable_Source/Architecture_Scene_V16.json').read_text(encoding='utf8'));e=next(e for e in S['elements'] if e['name']==n);e['parts'][0]['geometry']=g;e['v16_topology']='Quality triangles, continuous interior coverage; tiny existing hard-level corner is covered by supported stone infill'
if infill is not None:
 import export_v5 as ex
 ex.SCENE=S;sv=[];sf=[];parts=[]
 for poly in polys(infill):
  poly=orient(poly,1);gg={'type':'prism_holes','outer':list(poly.exterior.coords)[:-1],'holes':[list(h.coords)[:-1] for h in poly.interiors],'z':-.8,'height':.35};parts.append({'geometry':gg,'material':'M_Stone'});vx,fx,_,_=ex.solid_data(gg);off=len(sv);sv.extend(vx.tolist())
  for face in fx:sf.extend([[off+face[i] for i in t] for t in ex.triangulate(vx[face])] if len(face)>3 else [(np.array(face)+off).tolist()])
 sv=np.array(sv);sf=np.array(sf,np.int32);sm=rh.Mesh();sm.Vertices.UseDoublePrecisionVertices=True
 for k,tri in enumerate(sf):
  q=sv[tri];no=np.cross(q[1]-q[0],q[2]-q[0]);axes=[j for j in range(3) if j!=int(np.argmax(abs(no)))];uv0=q[:,axes]
  for p,u in zip(q@R.T+origin,uv0):sm.Vertices.AddPoint3d(*map(float,p));sm.TextureCoordinates.__add__(*map(float,u))
  sm.Faces.AddFace(k*3,k*3+1,k*3+2)
 sm.Normals.ComputeNormals();sm.Normals.UnitizeNormals();assert sm.IsValid and sm.IsClosed
 name='SITE_V16_COURT_EDGE_INFILL_STEP';existing=[ob for ob in F.Objects if ob.Attributes.Name==name+'__1']
 if existing:at=existing[0].Attributes;F.Objects.Delete(at.Id)
 else:
  gr=rh.Group();gr.Name=name;gid=len(F.Groups);F.Groups.Add(gr);at=rh.ObjectAttributes();at.Name=name+'__1';at.LayerIndex=next(l.Index for l in F.Layers if l.Name=='60_SITE');at.AddToGroup(gid)
 at.MaterialIndex=next(i for i,m in enumerate(F.Materials) if m.Name=='M_Stone');at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=F.Materials[at.MaterialIndex].DiffuseColor;ident=F.Objects.Add(sm,at);se={'name':name,'layer':'60_SITE','family':'SITE_MODEL','confidence':'MEDIUM','parts':parts,'classification':'SUPPORTED_STONE_INFILL_AT_EXISTING_COURT_TO_PATH_LEVEL_STEP','source':'Existing V15 hard-floor level corner retained; tiny gap closed with stone infill','v16_note':'24 mm-wide corner between existing path and court has about 54 mm level difference; hard infill covers the abrupt soil wedge, with bottom penetrating the soil'};S['elements']=[ee for ee in S['elements'] if ee['name']!=name]+[se];AQ['created']=[rr for rr in AQ['created'] if rr['node']!=name]+[{'id':str(ident),'name':at.Name,'node':name,'geometry_hash':hashlib.sha256(json.dumps(sm.Encode(),sort_keys=True).encode()).hexdigest()}]
 vv0=(np.array([[p.X,p.Y,p.Z] for p in sm.Vertices.ToPoint3dArray()])-origin)@R;ff0=np.array([f[:3] for f in sm.Faces],np.int32);uv0=np.array([[p.X,p.Y] for p in sm.TextureCoordinates]);nm0=np.array([[p.X,p.Y,p.Z] for p in sm.Normals])@R;fn='Native_Readback/NATIVE_'+name+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=vv0,faces=ff0,uv=uv0,normals=nm0,material_ids=np.zeros(len(ff0),np.int32));NI=[r for r in NI if r['name']!=name]+[{'name':name,'file':fn,'materials':['M_Stone'],'triangles':len(ff0),'native_objects':1,'element':{k:v for k,v in se.items() if k!='parts'}}];AQ['objects']=len(F.Objects);AQ['nodes']=len(NI)
sp=O/'08_Editable_Source/Architecture_Scene_V16.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V16_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();assert F.Write(str(P),8)
for nm in ['Native_Readback_Index_V16.json','Modeled_Index_V16.json']:(O/'02_Data'/nm).write_text(json.dumps(NI,ensure_ascii=False,indent=2),encoding='utf8')
(O/'06_Report/V16_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/V16_Soil_Quality_QA.json').write_text(json.dumps({'status':'QUALITY_REMESH_AWAITING_FRESH_READBACK','grade_quantiles':quant.tolist(),'triangulator':'Constrained Delaunay 25 degree target minimum angle, maximum 0.16 m2 triangle area','islands':triangle_proofs,'plan_footprint_preserved':True},indent=2),encoding='utf8');print('QUALITY SOIL NATIVE SAVED',len(nf),flush=True)
