import sys,json,math,hashlib,shutil,ast,copy
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
from PIL import Image
B=Path(r'E:/jz/JIA/Rebuild_V15');O=Path(r'E:/jz/JIA/Rebuild_V16');D=W/'v16';P=O/'04_Rhino/Architecture_Complete_V16_ALIGNED_ENU.3dm'
assert not P.exists(),'V16 already exists; preserve prior output'
for n in ['01_Source','02_Data/Native_Readback','03_Textures','04_Rhino','05_Export','06_Report','07_Reference','08_Editable_Source/V16_Scripts']:(O/n).mkdir(parents=True,exist_ok=True)
shutil.copytree(B/'03_Textures',O/'03_Textures',dirs_exist_ok=True)
shutil.copytree(B/'07_Reference/INSV',O/'07_Reference/INSV',dirs_exist_ok=True)
for p in [Path(r'D:/Desktop/问题/屏幕截图 2026-10-12 110221.jpg')]:
 if p.exists():shutil.copy2(p,O/'07_Reference'/p.name)
for n in ['Coordinate.json','Materials.json']:shutil.copy2(B/'02_Data'/n,O/'02_Data'/n)
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V15.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'));I=json.loads((B/'02_Data/Native_Readback_Index_V15.json').read_text(encoding='utf8'));ii={r['name']:r for r in I}
F=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V15_ALIGNED_ENU.3dm'));C=json.loads((B/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
def gh(g):return hashlib.sha256(json.dumps(g.Encode(),sort_keys=True).encode()).hexdigest()
def node_obs(n):return [ob for ob in F.Objects if ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__')]
changed_names=set(Q['remove']+[e['name'] for e in Q['replace']]);changed_ids={str(ob.Attributes.Id) for n in changed_names for ob in node_obs(n)}
retained=[]
for ob in F.Objects:
 if str(ob.Attributes.Id) not in changed_ids:retained.append({'id':str(ob.Attributes.Id),'name':ob.Attributes.Name,'geometry_hash':gh(ob.Geometry)})
print('BASE LOADED; RETAINED HASHED',len(retained),flush=True)
# Quiet, fine-grained soil surface; no macro diagonal field that could mimic grooves.
TX=O/'03_Textures/V16_Soil_Drain';TX.mkdir(exist_ok=True);rng=np.random.default_rng(161012);noise=rng.normal(0,1.3,(512,512,1));col=np.clip(np.array([125,116,87])[None,None,:]+noise,0,255).astype('uint8');Image.fromarray(col).save(TX/'Graded_Earth_1m.png');Image.fromarray(np.clip(128+rng.normal(0,1,(512,512)),0,255).astype('uint8')).save(TX/'Earth_Microheight.png')
for m in F.Materials:
 for getter,setter in [('GetBitmapTexture','SetBitmapTexture'),('GetBumpTexture','SetBumpTexture')]:
  tx=getattr(m,getter)()
  if tx:
   pp=Path(tx.FileName.replace('Rebuild_V15','Rebuild_V16'));assert pp.exists(),pp;getattr(m,setter)(str(pp))
 if m.Name=='M_V12_Terrain_Earth':m.SetBitmapTexture(str(TX/'Graded_Earth_1m.png'));m.SetBumpTexture(str(TX/'Earth_Microheight.png'));m.ToPhysicallyBased();m.PhysicallyBased.BaseColor=(1,1,1,1);m.PhysicallyBased.Roughness=.96
m=rh.Material();m.Name='M_V16_Drain_Concrete';m.DiffuseColor=(101,106,103,255);m.ToPhysicallyBased();m.PhysicallyBased.BaseColor=(.28,.30,.29,1);m.PhysicallyBased.Roughness=.92;F.Materials.Add(m)
S['materials']['M_V16_Drain_Concrete']={'color':[101,106,103],'roughness':.92,'source':'INSV wall-side shallow open drain; modeled sealing transition'}
proof=[];created=[];rows=[r for r in I if r['name'] not in changed_names];modeled=[]
for n in Q['remove']:
 oo=node_obs(n);assert len(oo)==1,(n,len(oo));F.Objects.Delete(oo[0].Attributes.Id)
S['elements']=[e for e in S['elements'] if e['name'] not in changed_names]
for r in rows:shutil.copy2(B/'02_Data'/r['file'],O/'02_Data'/r['file'])
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles']],type_ignores=[]),'<triangulation>','exec'))
for e in Q['replace']+Q['add']:
 n=e['name'];issource='native_source_file' in e
 if issource:
  dat=np.load(D/e['native_source_file']);v=dat['vertices'];ff=dat['faces'];uv=dat['uv'];used=np.unique(ff);remap=np.full(len(v),-1,np.int32);remap[used]=np.arange(len(used));v=v[used];uv=uv[used];ff=remap[ff];mat=ii[n]['materials'][0];e['parts']=[{'geometry':{'type':'mesh','vertices':v.tolist(),'faces':ff.tolist(),'uv':uv.tolist()},'material':mat}]
 else:
  mat=e['parts'][0]['material'];v,fs,_,_=ex.solid_data(e['parts'][0]['geometry']);ff=triangles(v,fs);uv=None
 mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True
 if issource:
  for p,pu in zip(v@R.T+origin,uv):mm.Vertices.AddPoint3d(*map(float,p));mm.TextureCoordinates.__add__(*map(float,pu))
  for tri in ff:mm.Faces.AddFace(*map(int,tri))
 else:
  t=v[ff];norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);unit=norm/(np.linalg.norm(norm,axis=1)[:,None]+1e-30);is_top=unit[:,2]>.6;smooth=np.zeros_like(v)
  if n=='SITE_V16_GRADED_INTERIOR_SOIL':
   for j in range(3):np.add.at(smooth,ff[is_top,j],norm[is_top])
   smooth/=np.linalg.norm(smooth,axis=1)[:,None]+1e-30
  for k,tri in enumerate(ff):
   q=v[tri];axes=[j for j in range(3) if j!=int(np.argmax(abs(unit[k])))];pu=q[:,axes];penu=q@R.T+origin
   for p,u in zip(penu,pu):mm.Vertices.AddPoint3d(*map(float,p));mm.TextureCoordinates.__add__(*map(float,u))
   j=k*3;mm.Faces.AddFace(j,j+1,j+2)
 mm.Normals.ComputeNormals();mm.Normals.UnitizeNormals()
 if n=='SITE_V16_GRADED_INTERIOR_SOIL':
  for k,tri in enumerate(ff):
   if is_top[k]:
    for j,vid in enumerate(tri):mm.Normals[k*3+j]=rh.Vector3f(*map(float,smooth[vid]@R.T))
 assert mm.IsValid,(n,'invalid')
 if not issource:assert mm.IsClosed,(n,'not closed')
 old=node_obs(n)
 if old:
  assert len(old)==1,(n,len(old));at=old[0].Attributes;F.Objects.Delete(at.Id)
 else:
  gr=rh.Group();gr.Name=n;gid=len(F.Groups);F.Groups.Add(gr);at=rh.ObjectAttributes();at.Name=n+'__1';at.LayerIndex=next(l.Index for l in F.Layers if l.Name=='60_SITE');at.AddToGroup(gid)
 at.MaterialIndex=next(i for i,m in enumerate(F.Materials) if m.Name==mat);at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=F.Materials[at.MaterialIndex].DiffuseColor;at.SetUserString('V16_Node',n);at.SetUserString('V16_Repair','Interior grade and continuous sealed wall-drain interface');ident=F.Objects.Add(mm,at);created.append({'id':str(ident),'name':at.Name,'geometry_hash':gh(mm),'node':n})
 # Indexed mesh data will be replaced by fresh saved-file readback below.
 nv=(np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R;nf=np.array([f[:3] for f in mm.Faces],np.int32);nu=np.array([[p.X,p.Y] for p in mm.TextureCoordinates]);nn=np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R;fn='Native_Readback/NATIVE_'+n+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=nv,faces=nf,uv=nu,normals=nn,material_ids=np.zeros(len(nf),np.int32));r={'name':n,'file':fn,'materials':[mat],'triangles':len(nf),'native_objects':1,'element':{k:v for k,v in e.items() if k!='parts'}};rows.append(r);S['elements'].append(e)
 proof.append({'node':n,'is_valid':mm.IsValid,'is_closed':mm.IsClosed,'vertices':len(nv),'triangles':len(nf),'full_uv':len(nu)==len(nv),'max_coordinate_difference_m':float(np.max(abs(np.array([nv.min(0),nv.max(0)])-np.array([v.min(0),v.max(0)]))))});print('WRITTEN',n,len(nf),mm.IsClosed,flush=True)
paths=set()
for m in F.Materials:
 for get in ['GetBitmapTexture','GetBumpTexture']:
  tx=getattr(m,get)()
  if tx:paths.add(Path(tx.FileName))
already={ef.Filename for ef in F.EmbeddedFiles}
for p in paths:
 assert p.exists(),p
 if str(p) not in already:F.EmbeddedFiles.Add(rh.EmbeddedFile.Read(str(p)))
for name,pos,tar in [('V16_Graded_Courtyard',[-22,-5,4],[-5,0,-.48]),('V16_Screenwall_Inside',[9,-14.5,1.2],[2,-16.5,-.2]),('V16_West_Wall_Drain',[-19.3,-9.3,.35],[-21.6,-4.2,-.85]),('V16_South_Wall_Drain',[-4,-20,-.7],[7,-17,-2.0])]:
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pp=np.array(pos)@R.T+origin;tt=np.array(tar)@R.T+origin;vp.SetCameraLocation(rh.Point3d(*pp));vp.SetCameraDirection(rh.Vector3d(*(tt-pp)));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetScreenPort((0,1600,1100,0,0,1));vp.SetFrustum(-.1,.1,-.06875,.06875,.1,5000);F.NamedViews.Add(vi)
S['version']='V16';S['v16_base_model']=str(B/'04_Rhino/Architecture_Complete_V15_ALIGNED_ENU.3dm');S['v16_changes']=['Graded interior soil','Sealed wall toe and narrow drain','Local original exterior scan band trimmed and road boundary matched']
sp=O/'08_Editable_Source/Architecture_Scene_V16.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2).replace('Rebuild_V15\\\\03_Textures','Rebuild_V16\\\\03_Textures'),encoding='utf8');F.Strings['V16_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();F.Strings['V16_Status']='Interior soil and wall toe/drain connections repaired; unchanged architecture and entry slopes retained; modeled finish levels, not independently field measured.';F.Strings['V16_Base_Model_SHA256']=hashlib.sha256((B/'04_Rhino/Architecture_Complete_V15_ALIGNED_ENU.3dm').read_bytes()).hexdigest();assert F.Write(str(P),8)
(O/'02_Data/Native_Readback_Index_V16.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8');(O/'02_Data/Modeled_Index_V16.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
md={}
for m in F.Materials:
 tx=m.GetBitmapTexture();bu=m.GetBumpTexture();pb=m.PhysicallyBased;sup=pb.Supported;md[m.Name]={'color':[round(c*255) for c in list(pb.BaseColor)[:3]] if sup else list(m.DiffuseColor)[:3],'roughness':pb.Roughness if sup else .85,'metallic':pb.Metallic if sup else 0,'alpha':1-m.Transparency,'native_bitmap':tx.FileName if tx else None,'native_bump':bu.FileName if bu else None,'native_diffuse':list(m.DiffuseColor),'physically_based_supported':sup}
(O/'02_Data/Native_Render_Materials.json').write_text(json.dumps(md,ensure_ascii=False,indent=2),encoding='utf8')
(O/'06_Report/V16_Assembly_QA.json').write_text(json.dumps({'status':'AWAITING_FRESH_NATIVE_READBACK','retained':retained,'created':created,'mesh_checks':proof,'removed_nodes':Q['remove'],'objects':len(F.Objects),'nodes':len(rows)},ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(D/'Geometry_QA.json',O/'06_Report/V16_Design_Control.json');shutil.copy2(D/'Mutation.json',O/'08_Editable_Source/Mutation_V16.json')
for n in ['v16_probe.py','v16_compact.py','v16_profile.py','v16_geometry.py','v16_assemble.py']:shutil.copy2(W/n,O/'08_Editable_Source/V16_Scripts'/n)
print('V16 ASSEMBLY SAVED',len(F.Objects),len(rows),P.stat().st_size,flush=True)
