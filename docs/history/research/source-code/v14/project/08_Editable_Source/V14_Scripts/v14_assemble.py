import sys,json,copy,math,shutil,hashlib,base64
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
O=Path(r'E:\jz\JIA\Rebuild_V14');B=Path(r'E:\jz\JIA\Rebuild_V13');M=W/'v14'
for p in ['02_Data','03_Textures','04_Rhino','05_Export','06_Report','07_Reference','08_Editable_Source']: (O/p).mkdir(exist_ok=True)
for p in ['03_Textures/Modeled_PBR']:shutil.copytree(B/p,O/p,dirs_exist_ok=True)
for n in ['Coordinate.json','Materials.json']:shutil.copy2(B/'02_Data'/n,O/'02_Data'/n)
mut=[json.loads((M/n).read_text(encoding='utf8')) for n in ['Building_Mutation.json','Terrain_Mutation.json']];S=json.loads((B/'08_Editable_Source/Architecture_Scene_V13.json').read_text(encoding='utf8'));old={e['name']:e for e in S['elements']}
rep={e['name']:e for mu in mut for e in mu['replace']};rem={n for mu in mut for n in mu['remove']};new={e['name']:e for mu in mut for e in mu['add']};E={n:rep.get(n,e) for n,e in old.items() if n not in rem};E.update(new);S['elements']=list(E.values());S['revision_notes'].append('V14 replaces exterior synthetic terrain with source 3DM UV meshes, corrects F3 floor-supported circulation, connects inner and half-open outer storage with main kitchen. V13 native inner-profile correction retained.');ex.SCENE=S
P=O/'04_Rhino/Architecture_Complete_V14_ALIGNED_ENU.3dm';F=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Complete_V13_ALIGNED_ENU.3dm'));C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);T=rh.Transform.Multiply(rh.Transform.Translation(*C['origin']),rh.Transform.Rotation(a,rh.Vector3d(0,0,1),rh.Point3d(0,0,0)));mids={m.Name:i for i,m in enumerate(F.Materials)};ly={l.Name:l.Index for l in F.Layers}
def base(n):return n.rsplit('__',1)[0] if '__' in n and n.rsplit('__',1)[1].isdigit() else n
assert all(p['material'] in mids for e in list(rep.values())+list(new.values()) for p in e['parts']), 'Unknown material in mutation'
obs={ob.Attributes.Name:ob for ob in F.Objects};groups={};retained=[];changed_ids=[];newids=[]
for ob in F.Objects:groups.setdefault(base(ob.Attributes.Name),[]).append(ob)
def gh(g):return hashlib.sha256(json.dumps(g.Encode(),sort_keys=True).encode()).hexdigest()
for ob in F.Objects:
 if base(ob.Attributes.Name) not in rem|set(rep):retained.append({'id':str(ob.Attributes.Id),'name':ob.Attributes.Name,'geometry_hash':gh(ob.Geometry)})
for n in rem:
 for ob in groups.get(n,[]):F.Objects.Delete(ob.Attributes.Id)
# Keep the original source texture bytes and UVs; make material paths portable in the folder.
SF=rh.File3dm.Read(r'E:\jz\纯场地版本.3dm');texture_rows=[];mats=json.loads((O/'02_Data/Materials.json').read_text(encoding='utf8'));texdir=O/'03_Textures/Original_Exterior';texdir.mkdir(exist_ok=True)
for i,srcmat in enumerate(SF.Materials):
 name='M_V14_ORIGINAL_EXTERIOR_'+str(i);p=Path(srcmat.GetBitmapTexture().FileName);dst=texdir/p.name;prior=W/'v12_terrain/Reference_Textures'/p.name;assert prior.exists();shutil.copy2(prior,dst)
 srcmat.Name=name;srcmat.SetBitmapTexture(str(dst));mids[name]=F.Materials.Add(srcmat);F.EmbeddedFiles.Add(rh.EmbeddedFile.Read(str(dst)))
 mats[name]={'color':[255,255,255],'roughness':.9,'metallic':0,'alpha':1,'source_bitmap':str(dst),'original_uv':True};texture_rows.append({'material':name,'file':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
(O/'02_Data/Materials.json').write_text(json.dumps(mats,ensure_ascii=False,indent=2),encoding='utf8')
for m in F.Materials:
 tex=m.GetBitmapTexture()
 if tex and 'Rebuild_V13' in tex.FileName:m.SetBitmapTexture(tex.FileName.replace('Rebuild_V13','Rebuild_V14'))
def mesh(g):
 v,fs,_,_=ex.solid_data(g);mm=rh.Mesh();mm.Vertices.UseDoublePrecisionVertices=True
 for q in v:mm.Vertices.AddPoint3d(*map(float,q))
 for f in fs:
  if len(f)<=4:mm.Faces.AddFace(*map(int,f))
  else:
   for t in ex.triangulate(v[f]):mm.Faces.AddFace(*[f[i] for i in t])
 if not(mm.IsValid and mm.IsClosed):mm.Vertices.CombineIdentical(True,True);mm.Faces.CullDegenerateFaces()
 mm.Normals.ComputeNormals();mm.Compact()
 assert mm.IsValid and mm.IsClosed,(mm.IsValidWithLog,mm.IsClosed,len(v),len(fs))
 return mm
index={r['name']:r for r in json.loads((B/'02_Data/Modeled_Index_V13.json').read_text(encoding='utf8')) if r['name'] in E}
for n,row in index.items():
 if n not in rep:shutil.copy2(B/'02_Data'/row['file'],O/'02_Data'/row['file'])
for ni,(n,e) in enumerate({**rep,**new}.items()):
 original=groups.get(n,[]);group_id=original[0].Attributes.GetGroupList()[0] if original and original[0].Attributes.GetGroupList() else None
 if group_id is None:
  gr=rh.Group();gr.Name=n;group_id=len(F.Groups);F.Groups.Add(gr)
 for ob in original:F.Objects.Delete(ob.Attributes.Id)
 if e.get('external_mesh_file'):
  d=np.load(M/'data'/e['external_mesh_file']);v=d['vertices'];fs=d['faces'];uv=d['uv'];mi=d['material_ids'];materials=next(r['materials'] for r in mut[1]['source_rows'] if r['name']==n);g=rh.Mesh();g.Vertices.UseDoublePrecisionVertices=True
  for q in v:g.Vertices.AddPoint3d(*map(float,q))
  for f in fs:g.Faces.AddFace(*map(int,f))
  for q in uv:g.TextureCoordinates.__add__(*map(float,q))
  g.Normals.ComputeNormals();g.Compact();g.Transform(T);geos=[(g,materials[0])]
 else:
  ps=ex.expand_parts(e);geos=[];tr=[];uvs=[];matnames=[]
  for p in ps:
   if 'definition' in e:continue
   gg=p['geometry'];g=ex.native(gg) if gg['type'] in ['box','prism_holes','cylinder'] else mesh(gg);g.Transform(ex.rh_transform(e));g.Transform(T);geos.append((g,p['material']))
  if 'definition' in e:
   assert len(original)==1;g=original[0].Geometry;delta=(np.array(e['origin'])-np.array(old[n]['origin']))@R.T;g.Transform(rh.Transform.Translation(*delta));geos=[(g,None)]
  for p in ps:
   vv,ff=ex.world_part(p,e)
   for f in ff:
    for ids in ex.triangulate(vv[f]) if len(f)>3 else [[0,1,2]]:
     q=vv[[f[k] for k in ids]];normal=np.cross(q[1]-q[0],q[2]-q[0]);axes=[j for j in range(3) if j!=int(np.argmax(abs(normal)))];tr.append(q);uvs.append(q[:,axes]);matnames.append(p['material'])
  v=np.array(tr).reshape(-1,3);fs=np.arange(len(v),dtype=np.int32).reshape(-1,3);uv=np.array(uvs).reshape(-1,2);materials=list(dict.fromkeys(matnames));mi=np.array([materials.index(m) for m in matnames],np.int32)
 for i,(g,mat) in enumerate(geos):
  prior=obs.get(n+'__'+str(i+1)) or (original[0] if len(geos)==1 and len(original)==1 else None)
  at=prior.Attributes if prior else rh.ObjectAttributes();ident=at.Id if prior else None;at.Name=n+'__'+str(i+1) if not e.get('definition') else n;at.LayerIndex=ly[e['layer']]
  if mat is not None:at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.MaterialIndex=mids[mat]
  if not prior:at.AddToGroup(group_id)
  at.SetUserString('V14_Element',n);at.SetUserString('Parameters',json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False));idd=F.Objects.Add(g,at)
  if ident:assert idd==ident
  changed_ids.append(str(idd));newids.append({'id':str(idd),'name':at.Name,'node':n,'geometry_hash':gh(g)})
 fn='MODEL_'+n+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=v,faces=fs,uv=uv,material_ids=mi);index[n]={'name':n,'file':fn,'materials':materials,'triangles':len(fs),'element':{k:v for k,v in e.items() if k!='parts'}}
 print('ASSEMBLED',ni,n,len(geos),flush=True)
sp=O/'08_Editable_Source/Architecture_Scene_V14.json';sp.write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8');F.Strings['V14_Editable_Scene_SHA256']=hashlib.sha256(sp.read_bytes()).hexdigest();F.Strings['V14_Source_Exterior_3DM_SHA256']=mut[1]['source_sha256'];F.Strings['V14_Circulation']=json.dumps(mut[0]['circulation']);F.Strings['V14_Structure']='Visible geometry fitting; no strength calculation';assert F.Write(str(P),8)
(O/'02_Data/Modeled_Index_V14.json').write_text(json.dumps(list(index.values()),ensure_ascii=False,indent=2),encoding='utf8')
qa={'status':'ASSEMBLED_PENDING_READBACK','model':str(P),'changed_nodes':list(rep),'removed_nodes':sorted(rem),'added_nodes':list(new),'changed_native_ids':changed_ids,'native_created':newids,'retained_native':retained,'original_exterior_textures':texture_rows,'source_sha256':mut[1]['source_sha256'],'source_triangles':sum(r['output_triangles'] for r in mut[1]['source_rows']),'objects':len(list(F.Objects))}
(O/'06_Report/V14_Assembly_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
for n in ['Building_Mutation.json','Terrain_Mutation.json','Merge_Boundary_LOCAL.json','Source_Site_Inventory.json']:shutil.copy2(M/n,O/'06_Report'/n)
for p in [Path(r'D:\Desktop\问题')/f'屏幕截图 2026-10-12 {t}.jpg' for t in ['002123','002238','002257','002422']]+[Path(r'D:\DJI\0002\DCIM\101MEDIA')/n for n in ['DJI_0508.JPG','DJI_0581.JPG']]+[Path(r'D:\Desktop\f413975e-c65f-4505-883b-b8594c25356f.png')]:shutil.copy2(p,O/'07_Reference'/p.name)
print('WROTE',str(P),qa['objects'],flush=True)
