"""Append only exact uncovered ground polygons after the pavilion/wall corrections."""
import sys,json,hashlib,shutil,gc,math,collections
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,export_v5 as ex
O=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid');D=W/'v11_ground_gap'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
SP=O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json';before=sha(SP);S=read(SP);m=read(D/'Mutation.json');qa=read(D/'Geometry_QA.json');assert qa['status']=='PASS';assert not m.get('replace') and not m.get('remove')
if m.get('source_scene_sha256'):assert m['source_scene_sha256']==before
names={e['name'] for e in S['elements']};new=m['add'];assert not(names&{e['name'] for e in new})
S['elements'].extend(new);S['materials'].update(m.get('materials',{}));S['v11_changes'].extend(m['changes'] if isinstance(m['changes'],list) else [m['changes']]);S['revision_notes'].append('V11 final projection audit: only the exposed local ground gaps left by corrected pavilion/wall footprints are filled at retained adjoining paving/earth elevations. Source reality meshes and original photographs remain exact.')
save(SP,S);after=sha(SP);ex.SCENE=S;ex.MATS=S['materials'];C=read(O/'02_Data/Coordinate.json');a=math.radians(C['rotation_deg']);co,si=math.cos(a),math.sin(a);R=np.array([[co,-si,0],[si,co,0],[0,0,1]]);origin=np.array(C['origin']);T=rh.Transform.Multiply(rh.Transform.Translation(*C['origin']),rh.Transform.Rotation(a,rh.Vector3d(0,0,1),rh.Point3d(0,0,0)))
src={'folder':'v11_ground_gap','sha256':sha(D/'Mutation.json'),'names':[e['name'] for e in new],'source_scene_before_append_sha256':before}
ch=read(O/'02_Data/V11_Changed_Nodes.json');ch['changed']=sorted(ch['changed']+src['names']);ch['sources'].append(src);ch['scene_sha256']=after;save(O/'02_Data/V11_Changed_Nodes.json',ch)
manifest=read(O/'06_Report/V11_Merge_Manifest.json');manifest['changed'].extend(src['names']);manifest['sources'].append(src);manifest['scene_sha256']=after;manifest['ground_gap_repair']={'before_uncovered_area_m2':2.3843038355791633,'input_scene_sha256':before,'nodes':len(new)};save(O/'06_Report/V11_Merge_Manifest.json',manifest)
reg=read(O/'02_Data/Interaction_Registry_V11.json');reg['source_scene_sha256']=after;save(O/'02_Data/Interaction_Registry_V11.json',reg)
dest=O/'07_Evidence/v11_ground_gap';shutil.copytree(D,dest,dirs_exist_ok=True)
M=read(O/'02_Data/Materials.json');M.update(m.get('materials',{}));save(O/'02_Data/Materials.json',M);I=read(O/'02_Data/Patch_Index.json');full=read(O/'02_Data/Full_Wall_Index_V11.json');pieces={};added_parts=0
for e in new:
 tri=[];mat=[];native=[]
 for j,p in enumerate(ex.expand_parts(e)):
  v,fs=ex.world_part(p,e);mesh=rh.Mesh();mesh.Vertices.UseDoublePrecisionVertices=True
  for q in v:mesh.Vertices.AddPoint3d(*map(float,q))
  for f in fs:
   inds=ex.triangulate(v[f]) if len(f)>3 else [[0,1,2]]
   for t in inds:
    ids=[f[k] for k in t];mesh.Faces.AddFace(*ids);tt=v[ids]
    assert np.linalg.norm(np.cross(tt[1]-tt[0],tt[2]-tt[0]))>1e-12
    tri.append(tt);mat.append(p['material'])
  mesh.Normals.ComputeNormals();mesh.Compact();assert mesh.IsValid and mesh.IsClosed
  native.append((j,mesh,p['material']));added_parts+=1
 tri=np.array(tri);vv=tri.reshape(-1,3);ff=np.arange(len(vv),dtype=np.int32).reshape(-1,3);uv=vv[:,:2];ms=list(dict.fromkeys(mat));mi=np.array([ms.index(x) for x in mat],np.int32)
 fn='V11_'+e['name']+'.npz';np.savez_compressed(O/'02_Data'/fn,vertices=vv,faces=ff,uv=uv,material_ids=mi)
 row={'index':len(I),'name':e['name'],'file':fn,'element':{k:v for k,v in e.items() if k!='parts'},'materials':ms,'triangles':len(tri),'vertices':len(vv),'photo_triangles':0,'role':'V11_EXACT_EXPOSED_GROUND_GAP_ONLY'};I.append(row)
 fullfn='FULL_V11_'+e['name']+'.npz';shutil.copy2(O/'02_Data'/fn,O/'02_Data'/fullfn);full.append(dict(row,index=len(full),file=fullfn));pieces[e['name']]=native
save(O/'02_Data/Patch_Index.json',I);save(O/'02_Data/Full_Wall_Index_V11.json',full)
def material_table(F):
 ids={v.Name:i for i,v in enumerate(F.Materials)}
 for e in new:
  for _,_,name in pieces[e['name']]:
   if name in ids:continue
   spec=M[name];v=rh.Material();v.Name=name;v.DiffuseColor=(*spec['color'],255);v.ToPhysicallyBased();v.PhysicallyBased.Roughness=spec['roughness'];v.PhysicallyBased.Metallic=spec.get('metallic',0);ids[name]=F.Materials.Add(v)
 return ids
def attr(e,j,li,mi):
 at=rh.ObjectAttributes();at.Name=e['name']+'__'+str(j+1);at.LayerIndex=li;at.MaterialIndex=mi;at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject
 for k in ['source','confidence','family','status','classification']:at.SetUserString(k,str(e.get(k,'')))
 at.SetUserString('Parameters',json.dumps({k:v for k,v in e.items() if k!='parts'},ensure_ascii=False));at.SetUserString('V11_Element',e['name']);at.SetUserString('V11_Part_Index',str(j));at.SetUserString('Native_Representation','Exact closed double-precision polygonal ground repair slab, not a structural foundation design');return at
for filename,aligned in [('V11_Changed_Wall_Solids_LOCAL.3dm',False),('Architecture_Edit_V11_ALIGNED_ENU.3dm',True),('Courtyard_Pavilion_Gate_V11_ALIGNED_ENU.3dm',True)]:
 path=O/'04_Rhino'/filename;F=rh.File3dm.Read(str(path));mids=material_table(F);li=next(l.Index for l in F.Layers if l.Name=='60_SITE')
 for e in new:
  gr=rh.Group();gr.Name=e['name'];gi=len(F.Groups);F.Groups.Add(gr)
  for j,geometry,material in pieces[e['name']]:
   g=geometry.Duplicate();assert not aligned or g.Transform(T);at=attr(e,j,li,mids[material]);at.SetUserString('V11_Material',material);at.AddToGroup(gi);F.Objects.Add(g,at)
 assert F.Write(str(path),8);print('Ground appended',filename,len(F.Objects),flush=True);del F;gc.collect()
path=O/'04_Rhino/Reality_Hybrid_V11.3dm';F=rh.File3dm.Read(str(path));mids=material_table(F);li=next(l.Index for l in F.Layers if l.Name=='PATCH_60_SITE')
for row in I[-len(new):]:
 d=np.load(O/'02_Data'/row['file']);v=d['vertices']@R.T+origin;mesh=rh.Mesh();mesh.Vertices.UseDoublePrecisionVertices=True
 for q in v:mesh.Vertices.AddPoint3d(*map(float,q))
 for f in d['faces']:mesh.Faces.AddFace(*map(int,f))
 mapping=rh.TextureMapping.CreatePlaneMapping(rh.Plane.WorldXY(),rh.Interval(0,1),rh.Interval(0,1),rh.Interval(0,1));mesh.SetTextureCoordinates(mapping,rh.Transform.Identity(),False)
 for j,q in enumerate(d['uv']):mesh.TextureCoordinates[j]=rh.Point2f(*map(float,q))
 mesh.Normals.ComputeNormals();assert mesh.IsValid and len(row['materials'])==1
 e=next(e for e in new if e['name']==row['name']);at=attr(e,0,li,mids[row['materials'][0]]);at.Name=e['name'];at.SetUserString('PatchRole',row['role']);F.Objects.AddMesh(mesh,at)
assert F.Write(str(path),8);print('Ground appended Reality_Hybrid_V11.3dm',len(F.Objects),flush=True);del F;gc.collect()
q=read(O/'06_Report/Changed_CAD_Conversion_QA.json');q['parts']+=added_parts;q['types']['Mesh']+=added_parts;q['closed_ground_repair_parts']=added_parts;save(O/'06_Report/Changed_CAD_Conversion_QA.json',q)
q=read(O/'06_Report/Editable_Rhino_Alignment_QA.json');q['changed_native_solids']+=added_parts;q['walls_only_objects']+=added_parts;q['sha256']=sha(O/'04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm');q['site_only_sha256']=sha(O/'04_Rhino/Courtyard_Pavilion_Gate_V11_ALIGNED_ENU.3dm');save(O/'06_Report/Editable_Rhino_Alignment_QA.json',q)
q=read(O/'06_Report/Native_Hybrid_QA.json');q['total_objects']+=len(new);q['counts']['patch_meshes']+=len(new);q['ground_gap_repairs']=len(new);save(O/'06_Report/Native_Hybrid_QA.json',q)
guide=O/'使用说明.md';guide.write_text(guide.read_text(encoding='utf8')+'\n最终覆盖检查另补了亭旁及墙脚约2.38平方米局部露空地坪，沿用相邻保留地坪标高与坡面；未修改原实景网格或贴图。\n',encoding='utf8')
print('Ground repair append complete',len(new),'nodes',added_parts,'closed slabs; scene',after,flush=True)
