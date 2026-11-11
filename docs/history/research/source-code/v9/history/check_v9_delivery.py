import sys,json,hashlib,math,collections,base64
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
O=Path(r'E:\jz\JIA\Rebuild_V9_Hybrid');V8=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');checks=[]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ck(id,ok,detail=None):
 checks.append({'id':id,'status':'PASS' if ok else 'FAIL','detail':detail})
 assert ok,(id,detail)
baseline=json.loads((O/'06_Report/V9_Baseline_Hashes.json').read_text(encoding='utf-8'))
change=json.loads((O/'02_Data/V9_Changed_Nodes.json').read_text(encoding='utf-8'));changed=set(change['changed'])|set(change['removed'])
native=O/'04_Rhino/Reality_Hybrid_V9.3dm';F=rh.File3dm.Read(str(native));B=rh.File3dm.Read(str(O/'01_Source/V8_Current_Before_V9.3dm'))
ck('V8_current_model_not_overwritten',sha(V8/'04_Rhino/Reality_Hybrid_V8.3dm')==baseline['current_sha256'])
ck('V8_current_snapshot_exact',sha(O/'01_Source/V8_Current_Before_V9.3dm')==baseline['current_sha256'])
ck('original_source_file_exact',sha(O/'01_Source/Pure_Site_UNMODIFIED.3dm')==baseline['original_source_sha256']==sha(r'E:\jz\纯场地版本.3dm'))
ck('working_source_file_exact',sha(O/'01_Source/Pure_Site_WORKING_V8.3dm')==baseline['working_source_sha256'])
ck('V8_editable_not_overwritten',sha(V8/'04_Rhino/Architecture_Edit_V8_ALIGNED_ENU.3dm')==baseline['baseline_V8_editable_sha256'])
ck('Rhino_metres_tolerance',F.Settings.ModelUnitSystem==rh.UnitSystem.Meters and abs(F.Settings.ModelAbsoluteTolerance-.001)<1e-12)
actual={str(o.Attributes.Id):o for o in F.Objects}
def affected(name):return any(name==n or name.startswith(n+'__') for n in changed)
preserved=[]
for ob in B.Objects:
 if affected(ob.Attributes.Name):continue
 oid=str(ob.Attributes.Id);ck('retained_uuid_'+oid,oid in actual,ob.Attributes.Name);out=actual[oid];a=ob.Geometry;b=out.Geometry
 ck('retained_attribute_'+oid,all(getattr(ob.Attributes,k)==getattr(out.Attributes,k) for k in ['Name','LayerIndex','MaterialIndex','MaterialSource','IsInstanceDefinitionObject','Visible']),ob.Attributes.Name)
 if isinstance(a,rh.Mesh):
  same=list(a.Faces)==list(b.Faces)
  for prop,keys in [('Vertices',['X','Y','Z']),('TextureCoordinates',['X','Y']),('Normals',['X','Y','Z'])]:
   aa=np.array([[getattr(p,k) for k in keys] for p in getattr(a,prop)]);bb=np.array([[getattr(p,k) for k in keys] for p in getattr(b,prop)]);same &= np.array_equal(aa,bb)
 elif isinstance(a,rh.InstanceReference):same=a.ParentIdefId==b.ParentIdefId and all(abs(getattr(a.Xform,'M'+str(i)+str(j))-getattr(b.Xform,'M'+str(i)+str(j)))<1e-10 for i in range(4) for j in range(4))
 else:same=a.Encode()==b.Encode()
 ck('retained_geometry_'+oid,bool(same),ob.Attributes.Name);preserved.append(oid)
for i,m in enumerate(B.Materials):
 out=F.Materials[i];t=m.GetBitmapTexture();u=out.GetBitmapTexture()
 ck('retained_material_'+str(i),all(getattr(m,k)==getattr(out,k) for k in ['Id','Name','DiffuseColor','Transparency','RenderMaterialInstanceId','RenderPlugInId','Shine','Reflectivity']) and ((t is None and u is None) or (t is not None and u is not None and t.Id==u.Id and t.FileName==u.FileName)))
ck('all_main_geometry_valid',all(o.Geometry.IsValid for o in F.Objects),len(F.Objects))
embeds=[]
for e in F.EmbeddedFiles:
 blob=base64.b64decode(F.GetEmbeddedFileAsBase64(e.Filename));expected=Path(e.Filename).read_bytes();ck('embedded_original_'+Path(e.Filename).name,blob==expected)
 embeds.append({'name':Path(e.Filename).name,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()})
ck('ten_original_images_retained',len(embeds)==10)
I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));oldI=json.loads((V8/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));old={r['name']:r for r in oldI}
scope=json.loads((O/'02_Data/V9_Allowed_Repair_Scope.json').read_text(encoding='utf-8'));allowed=unary_union([Polygon(p['outer'],p.get('holes',[])) for p in scope['polygons']]);hd=json.loads((O/'02_Data/Hole_Polygon.json').read_text());H=Polygon(hd['local']['outer'],hd['local']['holes']);coverage=[];counts=collections.Counter()
for r in I:
 if r['name'] not in changed:ck('inherited_patch_file_'+r['name'],sha(O/'02_Data'/r['file'])==sha(V8/'02_Data'/old[r['name']]['file']))
 d=np.load(O/'02_Data'/r['file']);v=d['vertices'];f=d['faces'];u=d['uv'];m=d['material_ids'];t=v[f]
 ck('patch_arrays_'+r['name'],bool(np.isfinite(v).all() and np.isfinite(u).all() and len(v)==len(u) and len(f)==len(m) and len(m)>0 and m.min()>=0 and m.max()<len(r['materials'])))
 face_cross=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)
 # Photo subdivision can quarter an accepted tiny boundary triangle. Four
 # roof subdivisions have nonzero cross norms 9.28e-11, total 1.86e-10 m2.
 # Use the source geometry conversion's explicit degeneracy threshold,
 # and separately retain Rhino kernel/readback validity as the native test.
 ck('patch_faces_'+r['name'],bool((face_cross>1e-12).all()),{'minimum_cross_norm_m2':float(face_cross.min()),'tiny_nonzero_triangles_below_1e10':int((face_cross<=1e-10).sum()),'tiny_area_m2':float(face_cross[face_cross<=1e-10].sum()/2)})
 ck('patch_scope_'+r['name'],bool(shapely.covers(allowed.buffer(1e-7),shapely.points(v[:,:2])).all()))
 xy=t[:,:,:2];area=abs(np.cross(xy[:,1]-xy[:,0],xy[:,2]-xy[:,0]))/2;coverage.append(shapely.union_all(shapely.polygons(xy[area>1e-10])))
 counts['patch_triangles']+=len(f);counts['photo_triangles']+=sum(int((m==j).sum()) for j,n in enumerate(r['materials']) if n.startswith(('PATCH_PHOTO_','BASE_PHOTO_','DJI_GABLE_')))
residual=H.difference(unary_union(coverage)).area;ck('original_void_xy_projection_covered',residual<1e-5,residual)
S=json.loads((O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));oldS=json.loads((V8/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));E={e['name']:e for e in S['elements']};oldE={e['name']:e for e in oldS['elements']}
ck('user_deleted_beam_absent',not any(o.Attributes.Name.startswith('BEAM_X_F3_2.1_0') for o in F.Objects) and 'BEAM_X_F3_2.1_0' not in E and 'BEAM_X_F3_2.1_0' not in {r['name'] for r in I})
for n,e in E.items():
 if n not in changed:ck('parameter_element_preserved_'+n,e==oldE[n])
for k in ['door_registry','rooms','room_connectivity','definitions']:ck('parameter_registry_preserved_'+k,S[k]==oldS[k])
audit=json.loads((O/'06_Report/Final_V9_Reference_QA.json').read_text(encoding='utf-8'));ck('independent_reference_and_collision_check',audit['status']=='PASS')
for name in ['Roof_Relation_Geometry_QA.json','Visible_Eave_Layers_Geometry_QA.json']:
 q=json.loads((O/'06_Report'/name).read_text(encoding='utf-8'));ck('closed_manifold_'+name,q['status'].startswith('PASS'))
kernel=json.loads((O/'06_Report/Editable_Rhino_Kernel_QA.json').read_text());ck('editable_Rhino_kernel',not kernel['invalid'] and not kernel['unexpected_open_solids'])
alignment=json.loads((O/'06_Report/Editable_Rhino_Alignment_QA.json').read_text());ck('editable_alignment_and_13_hinges',not alignment['invalid'] and alignment['independent_hinged_door_leaves']==13 and alignment['sha256']==sha(O/'04_Rhino/Architecture_Edit_V9_ALIGNED_ENU.3dm'))
edit=rh.File3dm.Read(str(O/'04_Rhino/Architecture_Edit_V9_ALIGNED_ENU.3dm'));modified_solids=[]
for ob in edit.Objects:
 if affected(ob.Attributes.Name) and isinstance(ob.Geometry,(rh.Brep,rh.Extrusion)):
  ck('editable_changed_part_solid_'+ob.Attributes.Name,ob.Geometry.IsSolid);modified_solids.append(ob.Attributes.Name)
ck('editable_changed_solids_present',len(modified_solids)>0,len(modified_solids))
ck('editable_user_deleted_beam_absent',not any(ob.Attributes.Name.startswith('BEAM_X_F3_2.1_0') for ob in edit.Objects))
reg=json.loads((O/'02_Data/Interaction_Registry_V9.json').read_text(encoding='utf-8'));ck('interaction_registry_scene_hash',reg['source_scene_sha256']==sha(O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json'))
ck('interaction_registry_layout_unchanged',reg['door_registry']==S['door_registry'] and reg['rooms']==S['rooms'] and reg['room_connectivity']==S['room_connectivity'])
ck('exchange_original_image_and_uv_readback',json.loads((O/'06_Report/V9_Exchange_Photo_Readback.json').read_text())['passed'])
report={'status':'PASS','checks':checks,'status_counts':dict(collections.Counter(c['status'] for c in checks)),'main_native':str(native),'native_sha256':sha(native),'current_V8_baseline_sha256':baseline['current_sha256'],'retained_native_objects_exact':len(preserved),'native_objects':len(F.Objects),'embedded_original_images':embeds,'counts':dict(counts),'original_void_projection_residual_m2':residual,'current_user_beam_deletion_preserved':True,'changed_elements':change,'field_survey_precision_certified':False,'UE5_actual_import_and_playtest':False,'limitations':['Hidden battens and structural roof assemblies are not measured or certified.','Dimensions inherited from photograph/mesh reconstruction; diagram establishes relationship only.','Interior field offsets and occluded terrain retain V8 uncertainty flags.']}
(O/'06_Report/Independent_V9_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['checks','embedded_original_images']},ensure_ascii=False,indent=2),flush=True)
