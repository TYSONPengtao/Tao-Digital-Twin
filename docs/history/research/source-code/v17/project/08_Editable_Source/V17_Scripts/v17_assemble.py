"""Selective native 3DM edits; all other object geometries keep their hashes."""
import sys,json,math,hashlib,shutil,copy,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
B=Path(r'E:/jz/JIA/Rebuild_V16');O=Path(r'E:/jz/JIA/Rebuild_V17');D=W/'v17';P=O/'04_Rhino/Architecture_Complete_V17_ALIGNED_ENU.3dm'
assert not P.exists(),'V17 model already exists; preserve it'
for n in ['01_Source','02_Data/Native_Readback','03_Textures','04_Rhino','05_Export','06_Report','07_Reference','08_Editable_Source/V17_Scripts']:(O/n).mkdir(parents=True,exist_ok=True)
shutil.copytree(B/'03_Textures',O/'03_Textures',dirs_exist_ok=True);shutil.copytree(B/'07_Reference/INSV',O/'07_Reference/INSV',dirs_exist_ok=True)
for fp in [r'D:/Desktop/问题/屏幕截图 2026-10-12 125511.jpg',r'D:/Desktop/问题/屏幕截图 2026-10-12 112805.jpg',r'D:/DJI/0002/DCIM/101MEDIA/DJI_0525.JPG',r'D:/DJI/0002/DCIM/101MEDIA/DJI_0526.JPG']:
 pp=Path(fp)
 if pp.exists():shutil.copy2(pp,O/'07_Reference'/pp.name)
for n in ['Coordinate.json','Materials.json']:shutil.copy2(B/'02_Data'/n,O/'02_Data'/n)
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V16.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'))
I=json.loads((B/'02_Data/Native_Readback_Index_V16.json').read_text(encoding='utf8'));ii={r['name']:r for r in I}
F=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V16_ALIGNED_ENU.3dm'));C=json.loads((B/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
obs={o.Attributes.Name:o for o in F.Objects}
def gh(g):return hashlib.sha256(json.dumps(g.Encode(),sort_keys=True).encode()).hexdigest()
def node_obs(n):return [ob for ob in F.Objects if ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__')]
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles']],type_ignores=[]),'<triangulation>','exec'))
edits=[]
for p in Q['part_edits']:
 assert p['native_name'] in obs,p['native_name'];edits.append({**p,'old':obs[p['native_name']]})
for e in Q['replace']:
 if e.get('v17_partwise'):continue
 oo=node_obs(e['name']);assert len(oo)==1,(e['name'],len(oo));edits.append({'node':e['name'],'native_name':oo[0].Attributes.Name,'old':oo[0],'element':e,'material':e['parts'][0]['material'] if e['parts'] else ii[e['name']]['materials'][0]})
changedids={str(e['old'].Attributes.Id) for e in edits};retained=[{'id':str(ob.Attributes.Id),'name':ob.Attributes.Name,'geometry_hash':gh(ob.Geometry)} for ob in F.Objects if str(ob.Attributes.Id) not in changedids]
print('BASE LOADED; UNCHANGED HASHED',len(retained),'EDITS',len(edits),flush=True)
for m in F.Materials:
 for getter,setter in [('GetBitmapTexture','SetBitmapTexture'),('GetBumpTexture','SetBumpTexture')]:
  tx=getattr(m,getter)()
  if tx:
   pp=Path(tx.FileName.replace('Rebuild_V16','Rebuild_V17'));assert pp.exists(),pp;getattr(m,setter)(str(pp))
m=rh.Material();m.Name='M_V17_Garden_Soil';m.DiffuseColor=(101,105,82,255);m.ToPhysicallyBased();m.PhysicallyBased.BaseColor=(.62,.66,.52,1);m.PhysicallyBased.Roughness=.98;m.SetBitmapTexture(str(O/'03_Textures/V16_Soil_Drain/Graded_Earth_1m.png'));m.SetBumpTexture(str(O/'03_Textures/V16_Soil_Drain/Earth_Microheight.png'));F.Materials.Add(m)
S['materials']['M_V17_Garden_Soil']={'color':[101,105,82],'roughness':.98,'source':'Lower exterior garden soil; same fine grain field as V16 earth, subdued green/brown tint'}
created=[];deleted=[];checks=[]
def make_mesh(g=None,source=None,smooth=False):
 if source is not None:
  dd=np.load(source);v=dd['vertices'];ff=dd['faces'];uv=dd['uv'];used=np.unique(ff);remap=np.full(len(v),-1,np.int32);remap[used]=np.arange(len(used));v=v[used];uv=uv[used];ff=remap[ff]
 else:v,fs,_,_=ex.solid_data(g);ff=triangles(v,fs);uv=None
 mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True
 if source is not None:
  for p,u in zip(v@R.T+origin,uv):mm.Vertices.AddPoint3d(*map(float,p));mm.TextureCoordinates.__add__(*map(float,u))
  for tri in ff:mm.Faces.AddFace(*map(int,tri))
 else:
  t=v[ff];fn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);unit=fn/(np.linalg.norm(fn,axis=1)[:,None]+1e-30);top=unit[:,2]>.45;nn=np.zeros_like(v)
  if smooth:
   for j in range(3):np.add.at(nn,ff[top,j],fn[top])
   nn/=np.linalg.norm(nn,axis=1)[:,None]+1e-30
  for k,tri in enumerate(ff):
   q=v[tri];axes=[j for j in range(3) if j!=int(np.argmax(abs(unit[k])))];pu=q[:,axes]
   for p,u in zip(q@R.T+origin,pu):mm.Vertices.AddPoint3d(*map(float,p));mm.TextureCoordinates.__add__(*map(float,u))
   mm.Faces.AddFace(k*3,k*3+1,k*3+2)
 mm.Normals.ComputeNormals();mm.Normals.UnitizeNormals()
 if source is None and smooth:
  for k,tri in enumerate(ff):
   if top[k]:
    for j,vid in enumerate(tri):mm.Normals[k*3+j]=rh.Vector3f(*map(float,nn[vid]@R.T))
 assert mm.IsValid
 if source is None:assert mm.IsClosed
 return mm,v,ff,uv
def write_mesh(n,mm,mat,at,name):
 at.Name=name;at.MaterialIndex=next(i for i,m in enumerate(F.Materials) if m.Name==mat);at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=F.Materials[at.MaterialIndex].DiffuseColor;at.SetUserString('V17_Node',n);at.SetUserString('V17_Repair','Kitchen-storage concave junction; real exterior boundary and lower garden ground');ident=F.Objects.Add(mm,at);created.append({'id':str(ident),'name':at.Name,'node':n,'geometry_hash':gh(mm),'closed_expected':not n.startswith('SITE_V14_ORIGINAL_EXTERIOR')});checks.append({'name':name,'is_valid':mm.IsValid,'is_closed':mm.IsClosed,'vertices':len(mm.Vertices),'faces':len(mm.Faces),'full_uv':len(mm.TextureCoordinates)==len(mm.Vertices)})
for ed in edits:
 n=ed['node'];old=ed['old'];at=old.Attributes;ident=at.Id;F.Objects.Delete(ident)
 if 'geometry' in ed and ed['geometry'] is None:deleted.append({'id':str(ident),'name':ed['native_name'],'node':n});continue
 if 'element' in ed:
  e=ed['element'];source=D/e['v17_native_source_file'] if e.get('v17_native_source_file') else None;g=None if source else e['parts'][0]['geometry'];mm,v,ff,uv=make_mesh(g,source,'GRADED_INTERIOR' in n)
  if source:e['parts']=[{'geometry':{'type':'mesh','vertices':v.tolist(),'faces':ff.tolist(),'uv':uv.tolist()},'material':ed['material']}]
 else:mm,_,_,_=make_mesh(ed['geometry'])
 write_mesh(n,mm,ed['material'],at,ed['native_name'])
for e in Q['add']:
 n=e['name'];gr=rh.Group();gr.Name=n;gid=len(F.Groups);F.Groups.Add(gr)
 for j,part in enumerate(e['parts']):
  mm,_,_,_=make_mesh(part['geometry'],smooth='TERRAIN' in n);at=rh.ObjectAttributes();at.LayerIndex=next(l.Index for l in F.Layers if l.Name=='60_SITE');at.AddToGroup(gid);write_mesh(n,mm,part['material'],at,f'{n}__{j+1}')
changednames={e['name'] for e in Q['replace']+Q['add']};S['elements']=[e for e in S['elements'] if e['name'] not in changednames]+Q['replace']+Q['add'];rows=[]
for r in I:
 if r['name'] not in changednames:shutil.copy2(B/'02_Data'/r['file'],O/'02_Data'/r['file']);rows.append(r)
for n in sorted(changednames):
 eo=next(e for e in S['elements'] if e['name']==n);vv=[];ff=[];uv=[];nn=[];mi=[];mats=[];oo=node_obs(n)
 for ob in oo:
  assert isinstance(ob.Geometry,rh.Mesh),(n,type(ob.Geometry));mm=ob.Geometry;mat=F.Materials[ob.Attributes.MaterialIndex].Name
  if mat not in mats:mats.append(mat)
  off=len(vv);vv.extend(((np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R).tolist());uv.extend([[p.X,p.Y] for p in mm.TextureCoordinates]);nn.extend((np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R).tolist())
  for f in mm.Faces:
   fs=[f[0],f[1],f[2]];ff.append((np.array(fs)+off).tolist());mi.append(mats.index(mat))
   if f[3]!=f[2]:ff.append((np.array([f[0],f[2],f[3]])+off).tolist());mi.append(mats.index(mat))
 fn='Native_Readback/NATIVE_'+n+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=np.array(vv),faces=np.array(ff,np.int32),uv=np.array(uv),normals=np.array(nn),material_ids=np.array(mi,np.int32));rows.append({'name':n,'file':fn,'materials':mats,'triangles':len(ff),'native_objects':len(oo),'element':{k:v for k,v in eo.items() if k!='parts'}});print('UPDATED NATIVE NODE',n,len(oo),len(ff),flush=True)
paths=set()
for m in F.Materials:
 for getter in ['GetBitmapTexture','GetBumpTexture']:
  tx=getattr(m,getter)()
  if tx:paths.add(Path(tx.FileName))
embedded={ef.Filename for ef in F.EmbeddedFiles}
for pp in paths:
 assert pp.exists(),pp
 if str(pp) not in embedded:F.EmbeddedFiles.Add(rh.EmbeddedFile.Read(str(pp)))
for name,pos,tar in [('V17_Kitchen_Storage_Concave_Corner',[24,-1.5,7],[15.2,-8.2,-.5]),('V17_Lower_Garden_Junction',[21,-7.0,-1.0],[14.8,-8.4,-1.6]),('V17_Outer_Storage_Return',[26,-14,5],[16,-9.8,-.3])]:
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pp=np.array(pos)@R.T+origin;tt=np.array(tar)@R.T+origin;vp.SetCameraLocation(rh.Point3d(*pp));vp.SetCameraDirection(rh.Vector3d(*(tt-pp)));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetScreenPort((0,1600,1100,0,0,1));vp.SetFrustum(-.1,.1,-.06875,.06875,.1,5000);F.NamedViews.Add(vi)
S['version']='V17';S['v17_base_model']=str(B/'04_Rhino/Architecture_Complete_V16_ALIGNED_ENU.3dm');S['v17_changes']=['Remove obsolete perimeter branch at kitchen/storage concave corner','Recess exterior soil to photo fitted low ground','Continuous masonry support and matched low ground/scan/drain boundary']
sp=O/'08_Editable_Source/Architecture_Scene_V17.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2).replace('Rebuild_V16','Rebuild_V17'),encoding='utf8');F.Strings['V17_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();F.Strings['V17_Base_Model_SHA256']=hashlib.sha256((B/'04_Rhino/Architecture_Complete_V16_ALIGNED_ENU.3dm').read_bytes()).hexdigest();F.Strings['V17_Status']='Kitchen/storage concave junction corrected; named views added; fitted exterior grade, not independently surveyed footing design';assert F.Write(str(P),8)
for nm in ['Native_Readback_Index_V17.json','Modeled_Index_V17.json']:(O/'02_Data'/nm).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
md={}
for m in F.Materials:
 tx=m.GetBitmapTexture();bu=m.GetBumpTexture();pb=m.PhysicallyBased;sup=pb.Supported;md[m.Name]={'color':[round(c*255) for c in list(pb.BaseColor)[:3]] if sup else list(m.DiffuseColor)[:3],'roughness':pb.Roughness if sup else .85,'metallic':pb.Metallic if sup else 0,'alpha':1-m.Transparency,'native_bitmap':tx.FileName if tx else None,'native_bump':bu.FileName if bu else None,'native_diffuse':list(m.DiffuseColor),'physically_based_supported':sup}
(O/'02_Data/Native_Render_Materials.json').write_text(json.dumps(md,ensure_ascii=False,indent=2),encoding='utf8')
(O/'06_Report/V17_Assembly_QA.json').write_text(json.dumps({'status':'AWAITING_FRESH_READBACK','retained':retained,'created':created,'deleted':deleted,'mesh_checks':checks,'changed_nodes':sorted(changednames),'native_objects':len(F.Objects),'nodes':len(rows)},ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(D/'Geometry_QA.json',O/'06_Report/V17_Design_Control.json');shutil.copy2(D/'Mutation.json',O/'08_Editable_Source/Mutation_V17.json')
for pp in W.glob('v17_*.py'):shutil.copy2(pp,O/'08_Editable_Source/V17_Scripts'/pp.name)
print('V17 NATIVE SAVED',len(F.Objects),len(rows),P.stat().st_size,flush=True)
