import sys,json,copy,math,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
B=Path(r'E:/jz/JIA/Rebuild_V14');O=Path(r'E:/jz/JIA/Rebuild_V15');M=W/'v15';mu=json.loads((M/'Mutation.json').read_text(encoding='utf8'))
for p in ['02_Data','03_Textures','04_Rhino','05_Export','06_Report','07_Reference','08_Editable_Source']:(O/p).mkdir(exist_ok=True)
shutil.copytree(B/'03_Textures',O/'03_Textures',dirs_exist_ok=True)
C=json.loads((B/'02_Data/Coordinate.json').read_text(encoding='utf8'));(O/'02_Data/Coordinate.json').write_text(json.dumps(C,indent=2),encoding='utf8');a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);T=rh.Transform.Multiply(rh.Transform.Translation(*origin),rh.Transform.Rotation(a,rh.Vector3d(0,0,1),rh.Point3d(0,0,0)))
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V14.json').read_text(encoding='utf8'));old={e['name']:e for e in S['elements']};rep={e['name']:e for e in mu['replace']};add={e['name']:e for e in mu['add']};rem=set(mu['remove']);E={n:rep.get(n,e) for n,e in old.items() if n not in rem};E.update(add);S['elements']=list(E.values());S['revision_notes'].append('V15: explicit UV on native reconstruction meshes, sharp wall normals, inward mesh orientation correction, actual INSV-referenced inner gate and continuous approach pavement, trim porch roof from F3 bedroom, clean overlapping source wall faces.');ex.SCENE=S
F=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V14_ALIGNED_ENU.3dm'));mids={m.Name:i for i,m in enumerate(F.Materials)};ly={l.Name:l.Index for l in F.Layers};mats=json.loads((B/'02_Data/Materials.json').read_text(encoding='utf8'))
mat=rh.CommonObject.Decode(F.Materials[mids['M_Stone_Frame']].Encode());mat.Name='M_V15_GATE_GREY_STONE';mat.DiffuseColor=(132,134,130,255);mat.ToPhysicallyBased();mat.PhysicallyBased.BaseColor=(132/255,134/255,130/255,1);mat.PhysicallyBased.Roughness=.85;mids[mat.Name]=F.Materials.Add(mat);mats[mat.Name]={**mats['M_Stone_Frame'],'color':[132,134,130],'roughness':.85};S['materials'][mat.Name]=mats[mat.Name]
for m in F.Materials:
 for get,setter in [('GetBitmapTexture','SetBitmapTexture'),('GetBumpTexture','SetBumpTexture'),('GetTransparencyTexture','SetTransparencyTexture')]:
  tx=getattr(m,get)()
  if tx and 'Rebuild_V14' in tx.FileName:getattr(m,setter)(tx.FileName.replace('Rebuild_V14','Rebuild_V15'))
for sp in mats.values():
 if sp.get('source_bitmap'):sp['source_bitmap']=sp['source_bitmap'].replace('Rebuild_V14','Rebuild_V15')
(O/'02_Data/Materials.json').write_text(json.dumps(mats,ensure_ascii=False,indent=2),encoding='utf8')
def base(n):return n.rsplit('__',1)[0] if '__' in n and n.rsplit('__',1)[1].isdigit() else n
def gh(g):return hashlib.sha256(json.dumps(g.Encode(),sort_keys=True).encode()).hexdigest()
originals={str(ob.Attributes.Id):{'name':ob.Attributes.Name,'hash':gh(ob.Geometry)} for ob in F.Objects};obs={ob.Attributes.Name:ob for ob in F.Objects};groups={}
for ob in F.Objects:groups.setdefault(base(ob.Attributes.Name),[]).append(ob)
for n in rem:
 for ob in groups.get(n,[]):F.Objects.Delete(ob.Attributes.Id)
def closedmesh(gg):
 v,fs,_,_=ex.solid_data(gg);g=rh.Mesh();g.Vertices.UseDoublePrecisionVertices=True
 for q in v:g.Vertices.AddPoint3d(*map(float,q))
 for f in fs:
  if len(f)<=4:g.Faces.AddFace(*map(int,f))
  else:
   for ids in ex.triangulate(v[f]):g.Faces.AddFace(*[f[j] for j in ids])
 if not(g.IsValid and g.IsClosed):g.Vertices.CombineIdentical(True,True);g.Faces.CullDegenerateFaces()
 assert g.IsValid and g.IsClosed,gg['type'];g.Normals.ComputeNormals();return g
index={r['name']:r for r in json.loads((B/'02_Data/Modeled_Index_V14.json').read_text(encoding='utf8')) if r['name'] in E}
for n,rr in index.items():
 if n not in rep:shutil.copy2(B/'02_Data'/rr['file'],O/'02_Data'/rr['file'])
er={r['node']:r for r in mu['external_rows']}
for ni,(n,e) in enumerate({**rep,**add}.items()):
 orig=groups.get(n,[]);gid=orig[0].Attributes.GetGroupList()[0] if orig and orig[0].Attributes.GetGroupList() else None
 if gid is None:gr=rh.Group();gr.Name=n;gid=len(F.Groups);F.Groups.Add(gr)
 for ob in orig:F.Objects.Delete(ob.Attributes.Id)
 if e.get('external_mesh_file'):
  d=np.load(M/'data'/e['external_mesh_file']);v=d['vertices'];ff=d['faces'];uv=d['uv'];mi=d['material_ids'];materials=er[n]['materials'];g=rh.Mesh();g.Vertices.UseDoublePrecisionVertices=True
  for q in v:g.Vertices.AddPoint3d(*map(float,q))
  for f in ff:g.Faces.AddFace(*map(int,f))
  for q in uv:g.TextureCoordinates.__add__(*map(float,q))
  g.Normals.ComputeNormals();g.Transform(T);geos=[(g,materials[0])]
 else:
  ps=ex.expand_parts(e);geos=[];tr=[];uvs=[];matnames=[]
  for pp in ps:
   gg=pp['geometry'];g=ex.native(gg) if gg['type'] in ['box','prism_holes','cylinder'] else closedmesh(gg);g.Transform(ex.rh_transform(e));g.Transform(T);geos.append((g,pp['material']))
   v0,fs=ex.world_part(pp,e)
   for f in fs:
    for ids in ex.triangulate(v0[f]) if len(f)>3 else [[0,1,2]]:
     q=v0[[f[j] for j in ids]];nn=np.cross(q[1]-q[0],q[2]-q[0]);axes=[j for j in range(3) if j!=int(np.argmax(abs(nn)))];tr.append(q);uvs.append(q[:,axes]);matnames.append(pp['material'])
  v=np.array(tr).reshape(-1,3);ff=np.arange(len(v),dtype=np.int32).reshape(-1,3);uv=np.array(uvs).reshape(-1,2);materials=list(dict.fromkeys(matnames));mi=np.array([materials.index(m) for m in matnames],np.int32)
 for j,(g,m) in enumerate(geos):
  pr=obs.get(n+'__'+str(j+1)) or (orig[0] if len(geos)==1 and len(orig)==1 else None);at=pr.Attributes if pr else rh.ObjectAttributes();at.Name=n+'__'+str(j+1);at.LayerIndex=ly[e['layer']];at.MaterialIndex=mids[m];at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=(*mats[m]['color'],255)
  if not pr:at.AddToGroup(gid)
  at.SetUserString('V15_Element',n);at.SetUserString('Parameters',json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False));F.Objects.Add(g,at)
 fn='MODEL_'+n+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=v,faces=ff,uv=uv,material_ids=mi);index[n]={'name':n,'file':fn,'materials':materials,'triangles':len(ff),'element':{k:v for k,v in e.items() if k!='parts'}};print('GEOMETRY',ni,n,len(geos),flush=True)
# Give all reconstructed native meshes explicit per-face metre-based box UV.
# Duplicate face vertices provide hard plaster/brick normals and prevent a smoothed vertical wave on a straight wall.
# Original exterior retains its original vertex/UV topology.
uvfix=[];flips=[];meshproof=[]
for ii,ob in enumerate(list(F.Objects)):
 g=ob.Geometry
 if not isinstance(g,rh.Mesh):continue
 n=base(ob.Attributes.Name);source=n.startswith('SITE_V14_ORIGINAL_EXTERIOR');v=(np.array([[p.X,p.Y,p.Z] for p in g.Vertices.ToPoint3dArray()])-origin)@R;fs=[list(f[:3]) if f[2]==f[3] else list(f) for f in g.Faces];t=[]
 for f in fs:t.extend([v[f[:3]],v[[f[0],f[2],f[3]]]] if len(f)==4 else [v[f]])
 tt=np.array(t);nn=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);vol=float(np.einsum('ij,ij->i',tt[:,0]-v.mean(0),nn).sum()/6);flip=g.IsClosed and vol<-1e-11
 if flip:fs=[f[::-1] for f in fs];flips.append({'name':ob.Attributes.Name,'old_signed_volume_m3':vol})
 if source:
  assert len(g.TextureCoordinates)==len(g.Vertices);meshproof.append({'name':ob.Attributes.Name,'original_uv_preserved':True,'vertices':len(g.Vertices),'normals':len(g.Normals),'closed':g.IsClosed});continue
 mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True;counter=0
 for f in fs:
  q=v[f];face=np.cross(q[1]-q[0],q[2]-q[0]);axes=[j for j in range(3) if j!=int(np.argmax(abs(face)))];enu=q@R.T+origin
  for pt,uv0 in zip(enu,q[:,axes]):mm.Vertices.AddPoint3d(*map(float,pt));mm.TextureCoordinates.__add__(*map(float,uv0))
  mm.Faces.AddFace(*range(counter,counter+len(f)));counter+=len(f)
 mm.Normals.ComputeNormals();assert mm.IsValid and (not g.IsClosed or mm.IsClosed),(ob.Attributes.Name,mm.IsValidWithLog,mm.IsClosed)
 at=ob.Attributes;matname=F.Materials[at.MaterialIndex].Name if at.MaterialIndex>=0 else None
 if matname in mats:at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=(*mats[matname]['color'],255)
 ident=at.Id;F.Objects.Delete(ident);assert F.Objects.Add(mm,at)==ident
 uvfix.append({'name':at.Name,'old_uv':len(g.TextureCoordinates),'new_uv':len(mm.TextureCoordinates),'old_vertices':len(g.Vertices),'new_vertices':len(mm.Vertices),'sharp_face_normals':True,'closed':mm.IsClosed});meshproof.append({'name':at.Name,'uv':len(mm.TextureCoordinates),'vertices':len(mm.Vertices),'normal_min_length':min(math.sqrt(p.X*p.X+p.Y*p.Y+p.Z*p.Z) for p in mm.Normals),'closed':mm.IsClosed})
 if len(uvfix)%500==0:print('UV NORMALS',len(uvfix),flush=True)
ret=[];created=[]
for ob in F.Objects:
 ident=str(ob.Attributes.Id);h=gh(ob.Geometry);rr={'id':ident,'name':ob.Attributes.Name,'node':base(ob.Attributes.Name),'geometry_hash':h}
 (ret if ident in originals and originals[ident]['hash']==h else created).append(rr)
sp=O/'08_Editable_Source/Architecture_Scene_V15.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V15_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();F.Strings['V15_Revision']='Explicit mesh UV, sharp hard-wall normals, outward closed mesh orientations; corrected entrance route; source-wall mask; photo-referenced inner gate; no porch roof inside F3 bedroom';F.Strings['V15_Source_INSV_SHA256']='3651a3e01ca8d94447aef544ce379a4ef984f6e91a7d7099699812f7a28c237f'
P=O/'04_Rhino/Architecture_Complete_V15_ALIGNED_ENU.3dm';assert F.Write(str(P),8);(O/'02_Data/Modeled_Index_V15.json').write_text(json.dumps(list(index.values()),ensure_ascii=False,indent=2),encoding='utf8')
qa={'status':'ASSEMBLED_PENDING_NATIVE_READBACK','model':str(P),'objects':len(F.Objects),'retained_native':ret,'native_created':created,'geometry_changes':list(rep),'added':list(add),'removed':sorted(rem),'uv_fixes':uvfix,'inward_closed_meshes_corrected':flips,'mesh_proof':meshproof};(O/'06_Report/V15_Assembly_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');print('WROTE',str(P),len(F.Objects),'UV',len(uvfix),'FLIPS',len(flips),flush=True)
