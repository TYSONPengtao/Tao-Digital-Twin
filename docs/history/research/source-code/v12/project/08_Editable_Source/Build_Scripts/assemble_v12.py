"""Incremental V12 modeled site assembly. Source inputs are never written."""
import sys,json,math,hashlib,shutil,collections,gc
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
O=Path(r'E:\jz\JIA\Rebuild_V12');B=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid')
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,x):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
S=read(B/'08_Editable_Source/05_Intermediate/Architecture_Scene.json');baseline_scene_sha=sha(B/'08_Editable_Source/05_Intermediate/Architecture_Scene.json');names={e['name']:e for e in S['elements']};changed=[];removed=[];sources=[]
for folder in sys.argv[1:]:
 mp=W/folder/'Mutation.json';m=read(mp);ns=[e['name'] for e in m.get('replace',[])+m.get('add',[])]+m.get('remove',[]);assert not set(ns)&set(changed+removed),(folder,'overlap')
 for e in m.get('replace',[]):assert e['name'] in names,e['name'];names[e['name']]=e;changed.append(e['name'])
 for e in m.get('add',[]):assert e['name'] not in names,e['name'];names[e['name']]=e;changed.append(e['name'])
 for n in m.get('remove',[]):assert n in names,n;del names[n];removed.append(n)
 S['definitions'].update(m.get('definitions',{}));S['materials'].update(m.get('materials',{}));sources.append({'folder':folder,'mutation_sha256':sha(mp),'names':ns})
 dst=O/'07_Reference'/folder;dst.mkdir(exist_ok=True)
 for src in (W/folder).iterdir():
  if src.is_file() and src.suffix in ['.json','.py','.md','.txt','.png','.jpg']:shutil.copy2(src,dst/src.name)
 # Agent evidence subdirectories may contain analytical images, not heavy raw originals.
 for ed in ['Evidence','evidence']:
  if (W/folder/ed).is_dir():shutil.copytree(W/folder/ed,dst/ed,dirs_exist_ok=True)
# Old photo projection/edge repair meshes must not enter the all-modeled version.
for n,e in list(names.items()):
 if n.startswith('PHOTO_') or e.get('family')=='VIS_MODEL':del names[n];removed.append(n)
S['elements']=list(names.values());S['name']='Architecture_Complete_V12';S['status']='Photo-referenced editable modeled architecture and topography; provisional field dimensions';S['revision_notes'].append('V12 direct INSV roaming reference, aerial roof review, traditional visible timber kitchen, curved screen ornaments, rebuilt ground and ramps; no photographic source triangles used to fill gaps.')
ex.SCENE=S;ex.MATS=S['materials'];save(O/'08_Editable_Source/Architecture_Scene_V12.json',S);save(O/'02_Data/Materials.json',S['materials'])
texture_index=read(O/'03_Textures/Modeled_PBR/Material_Texture_Index.json')['materials']
manifest={'version':'V12','baseline_scene_sha256':baseline_scene_sha,'sources':sources,'changed':changed,'removed':sorted(set(removed)),'scene_sha256':sha(O/'08_Editable_Source/Architecture_Scene_V12.json'),'photographic_scan_triangles_in_primary':0}
save(O/'02_Data/V12_Changed_Nodes.json',manifest)
C=read(O/'02_Data/Coordinate.json');aa=math.radians(C['rotation_deg']);R=np.array([[math.cos(aa),-math.sin(aa),0],[math.sin(aa),math.cos(aa),0],[0,0,1]]);origin=np.array(C['origin']);T=rh.Transform.Multiply(rh.Transform.Translation(*C['origin']),rh.Transform.Rotation(aa,rh.Vector3d(0,0,1),rh.Point3d(0,0,0)))
F=rh.File3dm.Read(str(B/'04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm'));retire=set(changed+removed);before_ids={str(o.Attributes.Id) for o in F.Objects if not o.Attributes.IsInstanceDefinitionObject};deleted=[]
for ob in list(F.Objects):
 if not ob.Attributes.IsInstanceDefinitionObject and any(ob.Attributes.Name==n or ob.Attributes.Name.startswith(n+'__') for n in retire):deleted.append(str(ob.Attributes.Id));F.Objects.Delete(ob.Attributes.Id)
layerids={l.Name:l.Index for l in F.Layers};mids={m.Name:i for i,m in enumerate(F.Materials)}
for name,spec in S['materials'].items():
 if name in mids:continue
 m=rh.Material();m.Name=name;m.DiffuseColor=(*spec['color'],255);m.Transparency=1-spec.get('alpha',1);m.ToPhysicallyBased();m.PhysicallyBased.Roughness=spec.get('roughness',.6);m.PhysicallyBased.Metallic=spec.get('metallic',0);mids[name]=F.Materials.Add(m)
for name,i in mids.items():
 if name not in texture_index:continue
 ti=texture_index[name];mat=F.Materials.FindIndex(i);mat.SetBitmapTexture(str(O/ti['base_color']));mat.SetBumpTexture(str(O/ti['bump']));assert mat.GetBitmapTexture().FileName==str(O/ti['base_color']);assert mat.GetBumpTexture().FileName==str(O/ti['bump'])
 mat.SetUserString('V12_Appearance','Photo-referenced palette with modeled procedural microtexture; not a photogrammetric atlas')
for p in sorted((O/'03_Textures/Modeled_PBR').glob('*.png')):F.EmbeddedFiles.Add(rh.EmbeddedFile.Read(str(p)))
def closedmesh(g,mat):
 v,f,p,vec=ex.solid_data(g);assert v is not None
 mesh=rh.Mesh();mesh.Vertices.UseDoublePrecisionVertices=True
 for q in v:mesh.Vertices.AddPoint3d(*map(float,q))
 for face in f:
  if len(face)<=4:mesh.Faces.AddFace(*map(int,face))
  else:
   for t in ex.triangulate(v[face]):mesh.Faces.AddFace(*[face[j] for j in t])
 if mat in texture_index:
  ti=texture_index[mat];order=np.argsort(np.ptp(v,axis=0));long=int(order[-1]);wide=int(order[-2]);su,sv=ti['physical_tile_m']
  uv=np.c_[(v[:,wide]-v[:,wide].min())/su,(v[:,long]-v[:,long].min())/sv]
  for u0,v0 in uv:mesh.TextureCoordinates.__add__(float(u0),float(v0))
 mesh.Normals.ComputeNormals();mesh.Compact();assert mesh.IsValid and mesh.IsClosed
 return mesh
def native(g,mat):
 if g['type'] in ['box','cylinder','lathe','prism_holes']:return ex.native(g)
 if g['type']=='prism':
  v,f,p,vec=ex.solid_data(g);normal=vec/np.linalg.norm(vec)
  if max(abs((p-p[0])@normal))<1e-7:return ex.native(g)
 return closedmesh(g,mat)
count=0;stats=collections.Counter();new_ids=[];groups={}
for e in S['elements']:
 if e['name'] not in changed:continue
 if e['layer'] not in layerids:
  ly=rh.Layer();ly.Name=e['layer'];ly.Color=(156,146,121,255);layerids[e['layer']]=F.Layers.Add(ly)
 gr=rh.Group();gr.Name=e['name'];gi=len(F.Groups);F.Groups.Add(gr);groups[e['name']]=gi
 for j,p in enumerate(ex.expand_parts(e)):
  g=native(p['geometry'],p['material']);g.Transform(ex.rh_transform(e));g.Transform(T);at=rh.ObjectAttributes();at.Name=e['name']+'__'+str(j+1);at.LayerIndex=layerids[e['layer']];at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.MaterialIndex=mids[p['material']];at.AddToGroup(gi)
  for k in ['source','confidence','status','family','role','door_id','parent_door_id','assembly_id','classification']:at.SetUserString(k,str(e.get(k,'')))
  at.SetUserString('V12_Element',e['name']);at.SetUserString('V12_Material',p['material']);at.SetUserString('V12_Part',str(j));at.SetUserString('Parameters',json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False));at.SetUserString('CoordinateFrame','Original ENU metres Z-up')
  new_ids.append(str(F.Objects.Add(g,at)));stats[type(g).__name__]+=1;count+=1
 print('V12 native',e['name'],len(ex.expand_parts(e)),'parts',flush=True)
def view(name,pos,tar,top=False,extent=50):
 vi=rh.ViewInfo();vi.Name=name;vp=vi.Viewport;pos=np.array(pos)@R.T+origin;tar=np.array(tar)@R.T+origin;vp.SetCameraLocation(rh.Point3d(*pos));vp.SetCameraDirection(rh.Vector3d(*(tar-pos)));up=np.array([0,1,0])@R.T if top else np.array([0,0,1]);vp.SetCameraUp(rh.Vector3d(*up));vp.SetScreenPort((0,1600,1000,0,0,1))
 if top:vp.ChangeToParallelProjection(True);vp.SetFrustum(-extent/2,extent/2,-extent/3.2,extent/3.2,.1,5000)
 else:vp.ChangeToPerspectiveProjection(20,False,50);vp.SetFrustum(-.1,.1,-.0625,.0625,.1,5000)
 F.NamedViews.Add(vi);return vi
v=view('V12_Whole_Site',[52,-68,49],[-3,-4,2])
if len(F.Views)==0:F.Views.Add(v)
else:
 oldview=F.Views[0];oldview.Name='V12_Whole_Site';vp=oldview.Viewport;pos=np.array([52,-68,49])@R.T+origin;tar=np.array([-3,-4,2])@R.T+origin
 vp.SetCameraLocation(rh.Point3d(*pos));vp.SetCameraDirection(rh.Vector3d(*(tar-pos)));vp.SetCameraUp(rh.Vector3d(0,0,1));vp.ChangeToPerspectiveProjection(20,False,50);vp.SetScreenPort((0,1600,1000,0,0,1));vp.SetFrustum(-.1,.1,-.0625,.0625,.1,5000)
view('V12_Top_Roofs',[-2,-4,70],[-2,-4,0],True,65);view('V12_Kitchen',[5,-10,3],[9.5,-7.0,1.8]);view('V12_Kitchen_Truss',[9.1,-7.2,1.0],[11,-7.2,3.3]);view('V12_Entrance_Ramp',[-20,-17,3],[-15,-11.2,-.1]);view('V12_Screenwall',[0,-24,7],[7,-16.9,2.7])
F.Strings['Usage']='V12 primary all-modeled architecture/site; previous correct building parts retained; no original photogrammetric source faces. Reference-only cleaned pure-site scan delivered separately.';F.Strings['Reference_Rules']='Human-view INSV frames; above-eye/roof G:/处理; before detail geometries adapted; terrain from source elevations, provisional datum.';F.Strings['Coordinate']=json.dumps(C);F.Strings['V12_Scene_SHA256']=manifest['scene_sha256']
path=O/'04_Rhino/Architecture_Complete_V12_ALIGNED_ENU.3dm';assert F.Write(str(path),8)
# Keep exact retained IDs/geometry proof, without bloating the report with encodings.
retained=[str(o.Attributes.Id) for o in F.Objects if str(o.Attributes.Id) in before_ids];assert len(retained)+len(deleted)==len(before_ids)
save(O/'06_Report/Native_Assembly_QA.json',{'status':'ASSEMBLED_PENDING_KERNEL','baseline_sha256':sha(B/'04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm'),'model':str(path),'sha256':sha(path),'objects':len(F.Objects),'new_parts':count,'types':dict(stats),'retained_ids':retained,'retired_ids':deleted,'new_ids':new_ids,'photogrammetry_source_meshes':0,'scene_sha256':manifest['scene_sha256'],'pbr_textured_materials':len(texture_index),'embedded_files':len(F.EmbeddedFiles)})
del F;gc.collect()
# Export every modeled node for reproducible LOCAL review and exchange.
rows=[]
for e in S['elements']:
 tris=[];mats=[];part_uv=[]
 for p in ex.expand_parts(e):
  v,fs=ex.world_part(p,e)
  if v is None:continue
  for face in fs:
   for ix in ex.triangulate(v[face]) if len(face)>3 else [[0,1,2]]:
    q=v[[face[j] for j in ix]]
    if np.linalg.norm(np.cross(q[1]-q[0],q[2]-q[0]))>1e-12:
     tris.append(q);mats.append(p['material']);normal=np.cross(q[1]-q[0],q[2]-q[0]);drop=int(np.argmax(abs(normal)));axes=[j for j in range(3) if j!=drop]
     if texture_index.get(p['material'],{}).get('category')=='Wood':
      long=int(np.argmax(np.ptp(v,axis=0)))
      if long in axes:axes=[j for j in axes if j!=long]+[long]
     part_uv.append(q[:,axes])
 if not tris:continue
 t=np.array(tris);vv=t.reshape(-1,3);ff=np.arange(len(vv),dtype=np.int32).reshape(-1,3);uv=np.array(part_uv)
 mm=list(dict.fromkeys(mats));mi=np.array([mm.index(m) for m in mats],np.int32);fn='MODEL_'+e['name']+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=vv,faces=ff,uv=uv.reshape(-1,2),material_ids=mi);rows.append({'name':e['name'],'file':fn,'materials':mm,'triangles':len(t),'element':{k:v for k,v in e.items() if k!='parts'},'sha256':sha(O/'02_Data'/fn)})
save(O/'02_Data/Modeled_Index_V12.json',rows)
active_npz={r['file'] for r in rows}
for stale in (O/'02_Data').glob('MODEL_*.npz'):
 if stale.name not in active_npz:
  assert stale.resolve().parent==(O/'02_Data').resolve()
  stale.unlink()
print('V12 complete modeled scene',len(rows),'nodes',sum(r['triangles'] for r in rows),'triangles;',count,'new CAD parts',flush=True)
