import sys,json,math,copy,hashlib,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]+[str(W)]
import numpy as np,manifold3d as mf,rhino3dm as rh,export_v5 as ex
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']],type_ignores=[]),'<solid_helpers>','exec'))
O=Path(r'E:/jz/JIA/Rebuild_V15');P=O/'04_Rhino/Architecture_Complete_V15_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(P));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);si=O/'08_Editable_Source/Architecture_Scene_V15.json';S=json.loads(si.read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};ni=O/'02_Data/Native_Readback_Index_V15.json';I=json.loads(ni.read_text(encoding='utf8'));ii={r['name']:r for r in I};mi=O/'02_Data/Modeled_Index_V15.json';M=json.loads(mi.read_text(encoding='utf8'));aq=json.loads((O/'06_Report/V15_Assembly_QA.json').read_text(encoding='utf8'));reports=[]
def gh(g):return hashlib.sha256(json.dumps(g.Encode(),sort_keys=True).encode()).hexdigest()
def write(n,g,mat,new=False):
 vv,fs,_,_=ex.solid_data(g);faces=[]
 for f in fs:
  faces.extend([[f[k] for k in t] for t in ex.triangulate(vv[f])] if len(f)>3 else [f])
 faces=np.array(faces,np.int32);mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True;vs=[];uvs=[]
 for f in faces:
  q=vv[f];normal=np.cross(q[1]-q[0],q[2]-q[0]);axes=[j for j in range(3) if j!=int(np.argmax(abs(normal)))];enu=q@R.T+origin;k=len(vs)
  for pt,uv in zip(enu,q[:,axes]):mm.Vertices.AddPoint3d(*map(float,pt));mm.TextureCoordinates.__add__(*map(float,uv));uvs.append(uv)
  vs.extend(q.tolist());mm.Faces.AddFace(k,k+1,k+2)
 mm.Normals.ComputeNormals();assert mm.IsValid and mm.IsClosed
 if new:
  gr=rh.Group();gr.Name=n;gid=len(F.Groups);F.Groups.Add(gr);at=rh.ObjectAttributes();at.Name=n+'__1';at.LayerIndex=next(l.Index for l in F.Layers if l.Name=='60_SITE');at.AddToGroup(gid)
 else:
  ob=next(ob for ob in F.Objects if ob.Attributes.Name==n+'__1');at=ob.Attributes;F.Objects.Delete(at.Id)
 at.MaterialIndex=next(i for i,m in enumerate(F.Materials) if m.Name==mat);at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=F.Materials[at.MaterialIndex].DiffuseColor;idd=F.Objects.Add(mm,at)
 e=E[n] if not new else {'name':n,'layer':'60_SITE','family':'SITE_MODEL','confidence':'MEDIUM','source':'Existing aerial-referenced tree preserved; clear approach path and root pocket','parts':[]};e['parts']=[{'geometry':g,'material':mat}];e['v15_tree_pit']='400 mm radius root opening; tree location unchanged'
 if new:E[n]=e;S['elements'].append(e)
 v=(np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R;ff=np.array([f[:3] for f in mm.Faces],np.int32);uv=np.array([[p.X,p.Y] for p in mm.TextureCoordinates]);fn='Native_Readback/NATIVE_'+n+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=v,faces=ff,uv=uv,material_ids=np.zeros(len(ff),np.int32));row={'name':n,'file':fn,'materials':[mat],'triangles':len(ff),'native_objects':1,'element':{k:v for k,v in e.items() if k!='parts'}}
 I[:]=[r for r in I if r['name']!=n]+[row]
 mfname='MODEL_'+n+'.npz';np.savez_compressed(O/'02_Data'/mfname,vertices=v,faces=ff,uv=uv,material_ids=np.zeros(len(ff),np.int32));M[:]=[r for r in M if r['name']!=n]+[{**row,'file':mfname}]
 aq['native_created']=[r for r in aq['native_created'] if r['id']!=str(idd)]+[{'id':str(idd),'name':at.Name,'node':n,'geometry_hash':gh(mm)}]
 if new:aq['added'].append(n)
 reports.append({'node':n,'native_is_valid':mm.IsValid,'native_is_closed':mm.IsClosed,'complete_uv':len(uv)==len(v),'vertex_bbox_roundtrip_max_error_m':float(abs(np.array([v.min(0),v.max(0)])-np.array([vv.min(0),vv.max(0)])).max())})
cut=manifold({'type':'cylinder','origin':[-4,-13.5,-4],'radius':.40,'height':6,'segments':48})
for n,mat in [('SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT','M_V12_Road_Concrete'),('SITE_V15_ENTRY_PAVEMENT_SUPPORTED_SUBGRADE','M_V12_Terrain_Earth')]:
 r=manifold(E[n]['parts'][0]['geometry'])-cut;write(n,fromman(r),mat)
ring=[[-4+.385*math.cos(t),-13.5+.385*math.sin(t)] for t in np.linspace(0,2*math.pi,48,endpoint=False)];write('SITE_V15_EXISTING_TREE_ROOT_SOIL',{'type':'prism_holes','outer':ring,'holes':[],'z':-.88,'height':.228},'M_V12_Terrain_Earth',True)
si.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');ni.write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf8');mi.write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding='utf8');aq['objects']=len(F.Objects);(O/'06_Report/V15_Assembly_QA.json').write_text(json.dumps(aq,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V15_Editable_Scene_SHA256']=hashlib.sha256(si.read_bytes()).hexdigest();assert F.Write(str(P),8)
q=json.loads((O/'06_Report/V15_Native_Readback_QA.json').read_text(encoding='utf8'));q['sha256']=hashlib.sha256(P.read_bytes()).hexdigest();q['native_objects']=len(F.Objects);q['nodes']=len(I);q['post_tree_pit_native_verification']=reports;(O/'06_Report/V15_Native_Readback_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8');(O/'06_Report/V15_Tree_Pit_QA.json').write_text(json.dumps({'status':'PASS_CLEAR_TREE_ROOT_POCKET','tree_position_unchanged':[-4,-13.5],'radius_m':.40,'checks':reports},ensure_ascii=False,indent=2),encoding='utf8');print('TREE ROOT POCKET PASS',len(F.Objects),len(I),flush=True)
