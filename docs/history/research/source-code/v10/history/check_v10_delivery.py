import sys,json,math,hashlib,collections,base64,gc
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
O=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid');V9=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid');checks=[]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ck(id,ok,detail=None):
 checks.append({'id':id,'status':'PASS' if ok else 'FAIL','detail':detail});assert ok,(id,detail)
base=read(O/'06_Report/V10_Baseline_Hashes.json');change=read(O/'02_Data/V10_Changed_Nodes.json');changed=set(change['changed'])|set(change['removed'])
def affected(n):return any(n==k or n.startswith(k+'__') for k in changed)
ck('V9_native_untouched',sha(V9/'04_Rhino/Reality_Hybrid_V9.3dm')==base['baseline_native_sha256'])
ck('V9_editable_untouched',sha(V9/'04_Rhino/Architecture_Edit_V9_ALIGNED_ENU.3dm')==base['baseline_editable_sha256'])
ck('V9_snapshot_exact',sha(O/'01_Source/V9_Current_Before_V10.3dm')==base['baseline_native_sha256'])
ck('original_source_exact',sha(O/'01_Source/Pure_Site_UNMODIFIED.3dm')==base['original_source_sha256']==sha(r'E:\jz\纯场地版本.3dm'))
ck('working_source_exact',sha(O/'01_Source/Pure_Site_WORKING_V8.3dm')==base['working_source_sha256'])
native=O/'04_Rhino/Reality_Hybrid_V10.3dm';F=rh.File3dm.Read(str(native));B=rh.File3dm.Read(str(O/'01_Source/V9_Current_Before_V10.3dm'));actual={str(ob.Attributes.Id):ob for ob in F.Objects};kept=0
for ob in B.Objects:
 if affected(ob.Attributes.Name):continue
 oid=str(ob.Attributes.Id);ck('native_uuid_'+oid,oid in actual,ob.Attributes.Name);out=actual[oid]
 ck('native_attrs_'+oid,all(getattr(ob.Attributes,k)==getattr(out.Attributes,k) for k in ['Name','LayerIndex','MaterialIndex','MaterialSource','Visible','IsInstanceDefinitionObject']),ob.Attributes.Name)
 a=ob.Geometry;b=out.Geometry
 if isinstance(a,rh.Mesh):
  same=list(a.Faces)==list(b.Faces)
  for prop,keys in [('Vertices',['X','Y','Z']),('TextureCoordinates',['X','Y']),('Normals',['X','Y','Z'])]:same &= np.array_equal(np.array([[getattr(p,k) for k in keys] for p in getattr(a,prop)]),np.array([[getattr(p,k) for k in keys] for p in getattr(b,prop)]))
 elif isinstance(a,rh.InstanceReference):same=a.ParentIdefId==b.ParentIdefId and all(getattr(a.Xform,'M'+str(i)+str(j))==getattr(b.Xform,'M'+str(i)+str(j)) for i in range(4) for j in range(4))
 else:same=a.Encode()==b.Encode()
 ck('native_geometry_'+oid,bool(same),ob.Attributes.Name);kept+=1
for i,m in enumerate(B.Materials):
 n=F.Materials[i];t=m.GetBitmapTexture();u=n.GetBitmapTexture();ck('original_material_'+str(i),all(getattr(m,k)==getattr(n,k) for k in ['Id','Name','DiffuseColor','Transparency','RenderMaterialInstanceId']) and ((t is None and u is None) or (t is not None and u is not None and t.Id==u.Id and t.FileName==u.FileName)))
ck('native_valid',all(ob.Geometry.IsValid for ob in F.Objects),len(F.Objects));ck('native_metres',F.Settings.ModelUnitSystem==rh.UnitSystem.Meters)
images=[]
for e in F.EmbeddedFiles:
 blob=base64.b64decode(F.GetEmbeddedFileAsBase64(e.Filename));ck('image_'+e.Filename,blob==Path(e.Filename).read_bytes());images.append({'name':Path(e.Filename).name,'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob)})
ck('ten_original_images',len(images)==10);native_count=len(F.Objects);del F,B,actual;gc.collect();print('Native preservation verified',kept,flush=True)
I=read(O/'02_Data/Patch_Index.json');oldI={r['name']:r for r in read(V9/'02_Data/Patch_Index.json')};scope=read(O/'02_Data/V10_Allowed_Repair_Scope.json');allowed=unary_union([Polygon(p['outer'],p.get('holes',[])) for p in scope['polygons']]);hd=read(O/'02_Data/Hole_Polygon.json');H=Polygon(hd['local']['outer'],hd['local']['holes']);coverage=[]
for r in I:
 if r['name'] not in changed:ck('patch_exact_'+r['name'],sha(O/'02_Data'/r['file'])==sha(V9/'02_Data'/oldI[r['name']]['file']))
 d=np.load(O/'02_Data'/r['file']);v=d['vertices'];f=d['faces'];u=d['uv'];m=d['material_ids'];t=v[f]
 ck('array_valid_'+r['name'],bool(np.isfinite(v).all() and np.isfinite(u).all() and len(v)==len(u) and len(f)==len(m) and m.min()>=0 and m.max()<len(r['materials'])))
 cross=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1);ck('nonzero_triangles_'+r['name'],bool((cross>1e-12).all()),float(cross.min()))
 ck('void_scope_'+r['name'],bool(shapely.covers(allowed.buffer(1e-7),shapely.points(v[:,:2])).all()))
 xy=t[:,:,:2];ar=abs(np.cross(xy[:,1]-xy[:,0],xy[:,2]-xy[:,0]))/2;coverage.append(shapely.union_all(shapely.polygons(xy[ar>1e-10])))
residual=H.difference(unary_union(coverage)).area;ck('original_void_xy_covered',residual<1e-5,residual)
S=read(O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json');oldS=read(V9/'08_Editable_Source/05_Intermediate/Architecture_Scene.json');oldE={e['name']:e for e in oldS['elements']}
for e in S['elements']:
 if e['name'] not in changed:ck('scene_exact_'+e['name'],e==oldE[e['name']])
for k in ['door_registry','rooms','room_connectivity','definitions']:ck('unchanged_'+k,S[k]==oldS[k])
ck('deleted_user_beam_not_restored',not any(e['name']=='BEAM_X_F3_2.1_0' for e in S['elements']))
kernel=read(O/'06_Report/Changed_CAD_Kernel_QA.json');ck('all_new_site_solids_kernel',kernel['status']=='PASS' and not kernel['invalid'] and not kernel['open_solids'],kernel['parts'])
alignment=read(O/'06_Report/Editable_Rhino_Alignment_QA.json');ck('alignment_hash',alignment['sha256']==sha(O/'04_Rhino/Architecture_Edit_V10_ALIGNED_ENU.3dm'))
E=rh.File3dm.Read(str(O/'04_Rhino/Architecture_Edit_V10_ALIGNED_ENU.3dm'));P=rh.File3dm.Read(str(V9/'04_Rhino/Architecture_Edit_V9_ALIGNED_ENU.3dm'));actual={str(ob.Attributes.Id):ob for ob in E.Objects};editkept=0;newsolids=0
for ob in P.Objects:
 if affected(ob.Attributes.Name):continue
 oid=str(ob.Attributes.Id);out=actual.get(oid);ok=out is not None and ob.Geometry.Encode()==out.Geometry.Encode() and all(getattr(ob.Attributes,k)==getattr(out.Attributes,k) for k in ['Name','LayerIndex','MaterialIndex','Visible','IsInstanceDefinitionObject']);ck('editable_exact_'+oid,ok,ob.Attributes.Name);editkept+=1
for ob in E.Objects:
 if ob.Attributes.GetUserString('V10_Element'):
  closed=(isinstance(ob.Geometry,(rh.Brep,rh.Extrusion)) and ob.Geometry.IsSolid) or (isinstance(ob.Geometry,rh.Mesh) and ob.Geometry.IsClosed)
  ck('new_native_solid_'+ob.Attributes.Name,ob.Geometry.IsValid and closed);newsolids+=1
ck('all_changed_solids_count',newsolids==kernel['parts']);ck('editable_all_geometry_valid',all(ob.Geometry.IsValid for ob in E.Objects))
C=read(O/'02_Data/Coordinate.json');theta=math.radians(C['rotation_deg']);co=math.cos(theta);si=math.sin(theta);doors={r['leaf_element']:r for r in S['door_registry'] if r.get('leaf_element')};hinges=0
for ob in E.Objects:
 if ob.Attributes.Name not in doors or ob.Attributes.IsInstanceDefinitionObject:continue
 x,y,z=doors[ob.Attributes.Name]['hinge_world_m'];expected=[x*co-y*si+C['origin'][0],x*si+y*co+C['origin'][1],z+C['origin'][2]];tr=ob.Geometry.Xform;ck('door_hinge_'+ob.Attributes.Name,math.dist(expected,[tr.M03,tr.M13,tr.M23])<1e-8);hinges+=1
ck('13_hinged_doors',hinges==13)
reg=read(O/'02_Data/Interaction_Registry_V10.json');ck('registry_scene_hash',reg['source_scene_sha256']==sha(O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json'))
audit=read(O/'06_Report/Final_V10_Wall_QA.json');ck('independent_wall_reference_geometry',audit['status']=='PASS')
report={'status':'PASS','checks':checks,'passed_checks':len(checks),'native_sha256':sha(native),'editable_sha256':alignment['sha256'],'retained_native_objects_exact':kept,'retained_editable_objects_exact':editkept,'new_closed_native_solids':newsolids,'native_objects':native_count,'embedded_original_images':images,'original_void_projection_residual_m2':residual,'field_survey_precision_certified':False,'UE5_actual_import_and_playtest':False}
(O/'06_Report/Independent_V10_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['checks','embedded_original_images']},ensure_ascii=False,indent=2),flush=True)
