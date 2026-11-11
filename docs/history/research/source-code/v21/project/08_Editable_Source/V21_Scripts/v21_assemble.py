"""Assemble V21 selectively from the verified V20 native document."""
import sys,json,math,hashlib,shutil,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
B=Path('E:/jz/JIA/Rebuild_V20');O=Path('E:/jz/JIA/Rebuild_V21');D=W/'v21';P=O/'04_Rhino/Architecture_Complete_V21_ALIGNED_ENU.3dm';BP=B/'04_Rhino/Architecture_Complete_V20_ALIGNED_ENU.3dm'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
assert sha(BP)=='087a4457d3df7feea42503cf6ea27788fd1374e55b8d4a8dbd1853b75424d4d4'
for n in ['02_Data/Native_Readback','03_Textures','04_Rhino','05_Export','06_Report','07_Reference/V21_AsBuilt','08_Editable_Source/V21_Scripts']:(O/n).mkdir(parents=True,exist_ok=True)
shutil.copytree(B/'03_Textures',O/'03_Textures',dirs_exist_ok=True);shutil.copytree(B/'07_Reference',O/'07_Reference',dirs_exist_ok=True)
for a in ['house','gate','site']:
 rr=W/f'v21_{a}'/'Reference'
 if rr.exists():shutil.copytree(rr,O/'07_Reference/V21_AsBuilt'/a,dirs_exist_ok=True)
for s in list(Path('D:/Desktop/问题').glob('屏幕截图 2026-10-13 15*.jpg'))+list(Path('D:/Desktop/问题').glob('屏幕截图 2026-10-13 033*.jpg'))+list(Path('D:/Desktop/问题').glob('download.jfif')):shutil.copy2(s,O/'07_Reference/V21_AsBuilt'/s.name)
for n in ['Coordinate.json','Materials.json']:shutil.copy2(B/'02_Data'/n,O/'02_Data'/n)
Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'));NM=Q.get('materials',{});S=json.loads((B/'08_Editable_Source/Architecture_Scene_V20.json').read_text(encoding='utf8'));ex.SCENE=S
I=json.loads((B/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'));F=rh.File3dm.Read(str(BP));C=json.loads((B/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented']],type_ignores=[]),'<geometry>','exec'))
def gh(g):return hashlib.sha256(json.dumps(g.Encode(),sort_keys=True).encode()).hexdigest()
groups={}
for ob in F.Objects:
 ss=ob.Attributes.Name.split('__')
 for k in range(1,len(ss)+1):groups.setdefault('__'.join(ss[:k]),[]).append(ob)
def node(n):return groups.get(n,[])
changed={e['name'] for e in Q['replace']+Q['add']};removed=set(Q['remove']);delete_names=changed|removed;to_delete={str(ob.Attributes.Id):ob for n in delete_names for ob in node(n)}
retained=[{'id':str(ob.Attributes.Id),'name':ob.Attributes.Name,'geometry_hash':gh(ob.Geometry)} for ob in F.Objects if str(ob.Attributes.Id) not in to_delete];deleted=[{'id':ident,'name':ob.Attributes.Name} for ident,ob in to_delete.items()];created=[]
print('V20 RETAINED',len(retained),'DELETE',len(deleted),flush=True)
for m in F.Materials:
 for getter,setter in [('GetBitmapTexture','SetBitmapTexture'),('GetBumpTexture','SetBumpTexture')]:
  tx=getattr(m,getter)()
  if tx:
   pp=Path(tx.FileName.replace('Rebuild_V20','Rebuild_V21'));assert pp.exists(),pp;getattr(m,setter)(str(pp))
for n,md in NM.items():
 if any(m.Name==n for m in F.Materials):continue
 m=rh.Material();m.Name=n;m.DiffuseColor=tuple(md['color'])+(255,);m.ToPhysicallyBased();m.PhysicallyBased.BaseColor=tuple(c/255 for c in md['color'])+(1,);m.PhysicallyBased.Roughness=md.get('roughness',.85)
 for k,setter in [('bitmap','SetBitmapTexture'),('bump','SetBumpTexture')]:
  if k in md or ('native_'+k) in md:
   pp=Path(md.get(k,md.get('native_'+k)));dest=O/'03_Textures/V21_AsBuilt'/pp.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(pp,dest);getattr(m,setter)(str(dest));md[k]=str(dest)
 F.Materials.Add(m);S['materials'][n]=md
mids={m.Name:i for i,m in enumerate(F.Materials)};layers={l.Name:l.Index for l in F.Layers}
for e in Q['replace']+Q['add']:
 if e.get('reference_layer_name'):
  key='V21_GATE_'+e['reference_layer_name']
  if key not in layers:
   layer=rh.Layer();layer.Name=key;layer.ParentLayerId=F.Layers[layers['60_SITE']].Id;layer.Color=(125,130,132,255)
   layers[key]=F.Layers.Add(layer)
  e['layer']=key
def uv_for(q,no,mat):
 axes=[j for j in range(3) if j!=int(np.argmax(abs(no)))];uv=q[:,axes].copy()
 dim={'M_V18_Storage_Rubble':[3.2,2.3],'M_V18_Storage_Dark_Courses':[3.6,.64],'M_V20_Perimeter_Rubble':[3.2,2.3],'M_V20_Perimeter_Dark_Stone':[3.6,.56],'M_V20_Perimeter_Brick':[1.6,.9]}.get(mat)
 if dim:uv/=np.array(dim)
 return uv
def make(g,mat,n):
 g=oriented(g);v=np.array(g['vertices']);ff=triangles(v,g['faces']);t=v[ff];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ll=np.linalg.norm(nn,axis=1);assert ll.min()>1e-12,(n,ll.min());nn/=ll[:,None];mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True
 for j,q in enumerate(t):
  uv=uv_for(q,nn[j],mat)
  for p,u in zip(q@R.T+origin,uv):mm.Vertices.AddPoint3d(*map(float,p));mm.TextureCoordinates.__add__(*map(float,u))
  mm.Faces.AddFace(j*3,j*3+1,j*3+2)
 mm.Normals.ComputeNormals();mm.Normals.UnitizeNormals();assert mm.IsValid and mm.IsClosed,n
 return mm
def addmesh(n,e,mm,mat,j,gid):
 at=rh.ObjectAttributes();at.Name=f'{n}__{j+1}';at.LayerIndex=layers.get(e.get('layer','60_SITE'),layers['60_SITE']);at.AddToGroup(gid);at.MaterialIndex=mids[mat];at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.ColorSource=rh.ObjectColorSource.ColorFromObject;at.ObjectColor=F.Materials[mids[mat]].DiffuseColor
 at.SetUserString('V21_Node',n);at.SetUserString('V21_Reference',str(e.get('source','Original INSV and user marked errors')));at.SetUserString('Parameters',json.dumps({k:v for k,v in e.items() if k not in ['parts','external_native_cache']},ensure_ascii=False))
 if e.get('v21_door') or e.get('v20_door'):at.SetUserString('UE_Door_Pivot_LOCAL_m',json.dumps(e.get('pivot_world_m',e.get('hinge_local_m'))));at.SetUserString('UE_Default_Pose','OPEN');at.SetUserString('UE_Door_Operation',e.get('operation','HINGED_INWARD'))
 ident=F.Objects.Add(mm,at);created.append({'id':str(ident),'name':at.Name,'node':n,'geometry_hash':gh(mm),'closed_expected':not e.get('open_expected',False)})
for ob in to_delete.values():F.Objects.Delete(ob.Attributes.Id)
for e in Q['replace']+Q['add']:
 n=e['name'];gr=rh.Group();gr.Name=n;gid=len(F.Groups);F.Groups.Add(gr)
 if e.get('external_native_cache') or e.get('v21_native_cache_override') or e.get('v20_native_cache_override'):
  d=np.load(e.get('external_native_cache') or e.get('v21_native_cache_override') or e['v20_native_cache_override']);vv=d['vertices'];ff=d['faces'];uv=d['uv'];mi=d['material_ids'];mats=e.get('external_native_materials') or e.get('v21_native_cache_materials') or e.get('v20_native_cache_materials') or next((r['materials'] for r in I if r['name']==n),None) or list(dict.fromkeys(p['material'] for p in e['parts']));assert mats,(n,'missing cache material names')
  for j,mat in enumerate(mats):
   fs=ff[mi==j];mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True
   for q in fs:
    off=len(mm.Vertices)
    for idx in q:mm.Vertices.AddPoint3d(*map(float,vv[idx]@R.T+origin));mm.TextureCoordinates.__add__(*map(float,uv[idx]))
    mm.Faces.AddFace(off,off+1,off+2)
   mm.Normals.ComputeNormals();mm.Normals.UnitizeNormals();assert mm.IsValid and (mm.IsClosed or e.get('open_expected',False)),(n,mat,mm.IsValidWithLog);addmesh(n,e,mm,mat,j,gid)
 else:
  for j,p in enumerate(e['parts']):addmesh(n,e,make(p['geometry'],p['material'],n),p['material'],j,gid)
 print('V21 CREATED',n,len(groups.get(n,[])) if False else len(e['parts']),flush=True)
S['elements']=[e for e in S['elements'] if e['name'] not in delete_names]+Q['replace']+Q['add'];groups={}
for ob in F.Objects:
 ss=ob.Attributes.Name.split('__')
 for k in range(1,len(ss)+1):groups.setdefault('__'.join(ss[:k]),[]).append(ob)
rows=[]
for r in I:
 if r['name'] not in delete_names:shutil.copy2(B/'02_Data'/r['file'],O/'02_Data'/r['file']);rows.append(r)
for e in Q['replace']+Q['add']:
 n=e['name'];vv=[];ff=[];uv=[];nn=[];mi=[];mats=[];oo=node(n)
 for ob in oo:
  mm=ob.Geometry;mat=F.Materials[ob.Attributes.MaterialIndex].Name
  if mat not in mats:mats.append(mat)
  off=len(vv);vv.extend(((np.array([[p.X,p.Y,p.Z] for p in mm.Vertices.ToPoint3dArray()])-origin)@R).tolist());uv.extend([[p.X,p.Y] for p in mm.TextureCoordinates]);nn.extend((np.array([[p.X,p.Y,p.Z] for p in mm.Normals])@R).tolist())
  for f in mm.Faces:ff.append((np.array(f[:3])+off).tolist());mi.append(mats.index(mat))
 fn='Native_Readback/NATIVE_'+n+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=np.array(vv),faces=np.array(ff,np.int32),uv=np.array(uv),normals=np.array(nn),material_ids=np.array(mi,np.int32));e['native_geometry_file']=fn;rows.append({'name':n,'file':fn,'materials':mats,'triangles':len(ff),'native_objects':len(oo),'element':{k:v for k,v in e.items() if k not in ['parts','external_native_cache']}})
for m in F.Materials:
 for getter in ['GetBitmapTexture','GetBumpTexture']:
  tx=getattr(m,getter)()
  if tx and not any(ef.Filename==tx.FileName for ef in F.EmbeddedFiles):F.EmbeddedFiles.Add(rh.EmbeddedFile.Read(tx.FileName))
views=Q['cameras']
for name,pos,tar,fov in views:
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pp=np.array(pos)@R.T+origin;tt=np.array(tar)@R.T+origin;vp.SetCameraLocation(rh.Point3d(*pp));vp.SetCameraDirection(rh.Vector3d(*(tt-pp)));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetScreenPort((0,1600,1100,0,0,1));span=.05*math.tan(math.radians(fov/2));vp.SetFrustum(-span,span,-span*1100/1600,span*1100/1600,.05,5000);F.NamedViews.Add(vi)
S['version']='V21';S['v21_changes']=Q['change_notes'];sp=O/'08_Editable_Source/Architecture_Scene_V21.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2).replace('Rebuild_V20','Rebuild_V21'),encoding='utf8');F.Strings['V21_Editable_Scene_SHA256']=sha(sp);F.Strings['V21_Base_Model']='V20 preserved unchanged';F.Strings['V21_Status']='Original INSV and user as-built correction; independently saved native model; inward open doors';assert F.Write(str(P),8)
for n in ['Native_Readback_Index_V21.json','Modeled_Index_V21.json']:(O/'02_Data'/n).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
md={}
for m in F.Materials:
 tx=m.GetBitmapTexture();bu=m.GetBumpTexture();pb=m.PhysicallyBased;sup=pb.Supported;md[m.Name]={'color':[round(c*255) for c in list(pb.BaseColor)[:3]] if sup else list(m.DiffuseColor)[:3],'roughness':pb.Roughness if sup else .85,'metallic':pb.Metallic if sup else 0,'alpha':1-m.Transparency,'native_bitmap':tx.FileName if tx else None,'native_bump':bu.FileName if bu else None,'bump_distance_m':NM.get(m.Name,{}).get('bump_distance_m',.003)}
(O/'02_Data/Native_Render_Materials.json').write_text(json.dumps(md,ensure_ascii=False,indent=2),encoding='utf8')
(O/'02_Data/Materials.json').write_text(json.dumps(S['materials'],ensure_ascii=False,indent=2).replace('Rebuild_V20','Rebuild_V21'),encoding='utf8')
AQ={'status':'AWAITING_FRESH_READBACK','base_model':str(BP),'base_model_sha256':sha(BP),'retained':retained,'deleted':deleted,'created':created,'changed_nodes':sorted(changed),'removed_nodes':sorted(removed),'native_objects':len(F.Objects),'nodes':len(rows),'cameras':views};(O/'06_Report/V21_Assembly_QA.json').write_text(json.dumps(AQ,ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(D/'Mutation.json',O/'08_Editable_Source/Mutation_V21.json');shutil.copy2(D/'Door_Manifest.json',O/'02_Data/Door_Manifest_V21.json')
print('V21 NATIVE SAVED',len(F.Objects),len(rows),P.stat().st_size,flush=True)
