import sys,json,math,hashlib,collections,base64,gc
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
O=Path(r'E:\jz\JIA\Rebuild_V11_Hybrid');V10=Path(r'E:\jz\JIA\Rebuild_V10_Hybrid');checks=[]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ck(id,ok,detail=None):
 checks.append({'id':id,'status':'PASS' if ok else 'FAIL','detail':detail});assert ok,(id,detail)
base=read(O/'06_Report/V11_Baseline_Hashes.json');change=read(O/'02_Data/V11_Changed_Nodes.json');changed=set(change['changed'])|set(change['removed'])
def affected(n):return any(n==k or n.startswith(k+'__') for k in changed)
ck('V10_native_untouched',sha(V10/'04_Rhino/Reality_Hybrid_V10.3dm')==base['baseline_native_sha256'])
ck('V10_editable_untouched',sha(V10/'04_Rhino/Architecture_Edit_V10_ALIGNED_ENU.3dm')==base['baseline_editable_sha256'])
ck('V10_snapshot_exact',sha(O/'01_Source/V10_Current_Before_V11.3dm')==base['baseline_native_sha256'])
ck('original_source_exact',sha(O/'01_Source/Pure_Site_UNMODIFIED.3dm')==base['original_source_sha256']==sha(r'E:\jz\纯场地版本.3dm'))
ck('working_source_exact',sha(O/'01_Source/Pure_Site_WORKING_V8.3dm')==base['working_source_sha256'])
native=O/'04_Rhino/Reality_Hybrid_V11.3dm';F=rh.File3dm.Read(str(native));B=rh.File3dm.Read(str(O/'01_Source/V10_Current_Before_V11.3dm'));actual={str(ob.Attributes.Id):ob for ob in F.Objects};kept=0
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
I=read(O/'02_Data/Patch_Index.json');oldI={r['name']:r for r in read(V10/'02_Data/Patch_Index.json')};scope=read(O/'02_Data/V11_Allowed_Repair_Scope.json');allowed=unary_union([Polygon(p['outer'],p.get('holes',[])) for p in scope['polygons']]);hd=read(O/'02_Data/Hole_Polygon.json');H=Polygon(hd['local']['outer'],hd['local']['holes'])
cov=read(O/'06_Report/Final_Ground_Coverage_QA.json');projection_inputs={r['name']:r for r in cov['patch_proof']}
allowed_tol=allowed.buffer(1e-7);shapely.prepare(allowed_tol)
ck('exact_projection_audit_all_inputs',cov['all_indexed_nodes_checked'] and len(projection_inputs)==len(I) and cov['source_index_sha256']==sha(O/'02_Data/Patch_Index.json') and cov['hole_polygon_sha256']==sha(O/'02_Data/Hole_Polygon.json'))
ck('exact_projection_residual_wkb',cov['residual_wkb_sha256']==sha(O/'07_Evidence/Final_Ground_Coverage/Residual.wkb'))
for r in I:
 if r['name'] not in changed:ck('patch_exact_'+r['name'],sha(O/'02_Data'/r['file'])==sha(V10/'02_Data'/oldI[r['name']]['file']))
 d=np.load(O/'02_Data'/r['file']);v=d['vertices'];f=d['faces'];u=d['uv'];m=d['material_ids'];t=v[f]
 ck('array_valid_'+r['name'],bool(np.isfinite(v).all() and np.isfinite(u).all() and len(v)==len(u) and len(f)==len(m) and m.min()>=0 and m.max()<len(r['materials'])))
 cross=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1);ck('nonzero_triangles_'+r['name'],bool((cross>1e-12).all()),float(cross.min()))
 ck('void_scope_'+r['name'],bool(shapely.covers(allowed_tol,shapely.points(v[:,:2])).all()))
 ck('projection_input_exact_'+r['name'],projection_inputs[r['name']]['file']==r['file'] and projection_inputs[r['name']]['sha256']==sha(O/'02_Data'/r['file']))
residual=shapely.from_wkb((O/'07_Evidence/Final_Ground_Coverage/Residual.wkb').read_bytes()).area;ck('original_void_xy_covered',cov['status']=='PASS' and residual<1e-5 and abs(residual-cov['total_m2'])<1e-12,residual)
print('Patch preservation and scope verified',len(I),'nodes; void residual',residual,flush=True)
S=read(O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json');oldS=read(V10/'08_Editable_Source/05_Intermediate/Architecture_Scene.json');oldE={e['name']:e for e in oldS['elements']}
for e in S['elements']:
 if e['name'] not in changed:ck('scene_exact_'+e['name'],e==oldE[e['name']])
for k in ['rooms','room_connectivity','definitions']:ck('unchanged_'+k,S[k]==oldS[k])
ck('old_door_registry_preserved',S['door_registry'][:len(oldS['door_registry'])]==oldS['door_registry'])
ck('deleted_user_beam_not_restored',not any(e['name']=='BEAM_X_F3_2.1_0' for e in S['elements']))
kernel=read(O/'06_Report/Changed_CAD_Kernel_QA.json');ck('all_new_site_solids_kernel',kernel['status']=='PASS' and not kernel['invalid'] and not kernel['open_solids'],kernel['parts'])
alignment=read(O/'06_Report/Editable_Rhino_Alignment_QA.json');ck('alignment_hash',alignment['sha256']==sha(O/'04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm'))
E=rh.File3dm.Read(str(O/'04_Rhino/Architecture_Edit_V11_ALIGNED_ENU.3dm'));P=rh.File3dm.Read(str(V10/'04_Rhino/Architecture_Edit_V10_ALIGNED_ENU.3dm'));actual={str(ob.Attributes.Id):ob for ob in E.Objects};editkept=0;newsolids=0
for ob in P.Objects:
 if affected(ob.Attributes.Name):continue
 oid=str(ob.Attributes.Id);out=actual.get(oid);ok=out is not None and ob.Geometry.Encode()==out.Geometry.Encode() and all(getattr(ob.Attributes,k)==getattr(out.Attributes,k) for k in ['Name','LayerIndex','MaterialIndex','Visible','IsInstanceDefinitionObject']);ck('editable_exact_'+oid,ok,ob.Attributes.Name);editkept+=1
for ob in E.Objects:
 if ob.Attributes.GetUserString('V11_Element'):
  closed=(isinstance(ob.Geometry,(rh.Brep,rh.Extrusion)) and ob.Geometry.IsSolid) or (isinstance(ob.Geometry,rh.Mesh) and ob.Geometry.IsClosed)
  ck('new_native_solid_'+ob.Attributes.Name,ob.Geometry.IsValid and closed);newsolids+=1
ck('all_changed_solids_count',newsolids==kernel['parts']);ck('editable_all_geometry_valid',all(ob.Geometry.IsValid for ob in E.Objects))
C=read(O/'02_Data/Coordinate.json');theta=math.radians(C['rotation_deg']);co=math.cos(theta);si=math.sin(theta);doors={r['leaf_element']:r for r in S['door_registry'] if r.get('leaf_element')};hinges=0
for ob in E.Objects:
 if ob.Attributes.Name not in doors or ob.Attributes.IsInstanceDefinitionObject:continue
 x,y,z=doors[ob.Attributes.Name]['hinge_world_m'];expected=[x*co-y*si+C['origin'][0],x*si+y*co+C['origin'][1],z+C['origin'][2]];tr=ob.Geometry.Xform;ck('door_hinge_'+ob.Attributes.Name,math.dist(expected,[tr.M03,tr.M13,tr.M23])<1e-8);hinges+=1
ck('13_original_hinged_doors',hinges==13)
for d in S['door_registry'][len(oldS['door_registry']):]:
 ck('exterior_gate_registry_'+d['door_id'],bool(d.get('hinge_world_m') and d.get('leaf_element')))
ck('registry_door_entries',read(O/'02_Data/Interaction_Registry_V11.json')['door_registry']==S['door_registry'])
reg=read(O/'02_Data/Interaction_Registry_V11.json');ck('registry_scene_hash',reg['source_scene_sha256']==sha(O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json'))
audit=read(O/'06_Report/Final_V11_Site_QA.json');ck('independent_site_geometry',audit['status']=='PASS')
report={'status':'PASS','checks':checks,'passed_checks':len(checks),'native_sha256':sha(native),'editable_sha256':alignment['sha256'],'retained_native_objects_exact':kept,'retained_editable_objects_exact':editkept,'new_closed_native_solids':newsolids,'native_objects':native_count,'embedded_original_images':images,'original_void_projection_residual_m2':residual,'field_survey_precision_certified':False,'UE5_actual_import_and_playtest':False}
(O/'06_Report/Independent_V11_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['checks','embedded_original_images']},ensure_ascii=False,indent=2),flush=True)
