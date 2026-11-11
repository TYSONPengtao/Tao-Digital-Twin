import sys,json,hashlib,math,collections,base64
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,rhino3dm as rh,shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');V7=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid')
native=O/'04_Rhino/Reality_Hybrid_V8.3dm';checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ck(id,ok,detail=None):
    checks.append({'id':id,'status':'PASS' if ok else 'FAIL','detail':detail})
    assert ok,(id,detail)
ck('original_site_file_byte_unchanged',sha(r'E:\jz\纯场地版本.3dm')==sha(O/'01_Source/Pure_Site_UNMODIFIED.3dm'))
v7qa=json.loads((V7/'06_Report/Independent_V7_QA.json').read_text(encoding='utf-8'))
ck('V7_native_not_overwritten',sha(V7/'04_Rhino/Reality_Hybrid_V7.3dm')==v7qa['native_sha256'])
A=rh.File3dm.Read(str(O/'01_Source/Pure_Site_UNMODIFIED.3dm'));D=rh.File3dm.Read(str(O/'01_Source/Pure_Site_WORKING_V8.3dm'));F=rh.File3dm.Read(str(native))
actual={str(o.Attributes.Id):o for o in F.Objects if not o.Attributes.IsInstanceDefinitionObject}
ck('Rhino_main_units_metres',F.Settings.ModelUnitSystem==rh.UnitSystem.Meters)
ck('Rhino_computational_tolerance_m',abs(F.Settings.ModelAbsoluteTolerance-.001)<1e-12)
base_report=[]
for i,(source,derived) in enumerate(zip(A.Objects,D.Objects)):
    out=actual[str(source.Attributes.Id)];a=source.Geometry;b=derived.Geometry;c=out.Geometry
    counts={}
    for prop,keys in [('Vertices',['X','Y','Z']),('TextureCoordinates',['X','Y']),('Normals',['X','Y','Z'])]:
        aa=np.array([[getattr(p,k) for k in keys] for p in getattr(a,prop)])
        bb=np.array([[getattr(p,k) for k in keys] for p in getattr(b,prop)])
        cc=np.array([[getattr(p,k) for k in keys] for p in getattr(c,prop)])
        ck(f'base_{i}_{prop}_native_derivative_exact',np.array_equal(bb,cc))
        ck(f'base_{i}_{prop}_original_prefix_exact',len(bb)>=len(aa) and np.array_equal(aa,bb[:len(aa)]))
        counts[prop]=[len(aa),len(bb)]
    ck(f'base_{i}_derived_faces_native_exact',list(b.Faces)==list(c.Faces))
    if i:
        ck(f'base_{i}_all_original_faces_unchanged',list(a.Faces)==list(b.Faces))
    else:
        mask=np.load(O/'02_Data/Source_Base_Face_Selection_Masks.npz')
        # Unchanged complete faces from the independent terrain agent are
        # exact source index tuples, unaffected by subsequent roof cleanup.
        kept=next((mask[k] for k in mask.files if 'retain' in k.lower() and 'whole' in k.lower()),None)
        if kept is not None:
            original_faces=np.array(list(a.Faces));working_faces=np.array(list(b.Faces))
            lookup={tuple(x) for x in working_faces}
            ck('base_0_retained_whole_original_faces',all(tuple(original_faces[int(j)]) in lookup for j in kept))
    ck(f'base_{i}_attributes_retained',source.Attributes.MaterialIndex==out.Attributes.MaterialIndex and source.Attributes.LayerIndex==out.Attributes.LayerIndex and source.Attributes.Name==out.Attributes.Name)
    ma=A.Materials[source.Attributes.MaterialIndex];mf=F.Materials[out.Attributes.MaterialIndex]
    for prop in ['Id','Name','DiffuseColor','Transparency','RenderMaterialInstanceId','RenderPlugInId','Shine','Reflectivity']:
        ck(f'base_{i}_material_{prop}',getattr(ma,prop)==getattr(mf,prop))
    ta=ma.GetBitmapTexture();tb=mf.GetBitmapTexture()
    ck(f'base_{i}_texture_binding_retained',ta.Id==tb.Id and ta.FileName==tb.FileName)
    ck(f'base_{i}_source_photo_copy',sha(ta.FileName)==sha(O/'03_Textures/Base'/Path(ta.FileName).name))
    base_report.append({'index':i,'data_counts_original_then_working':counts,'original_faces':len(a.Faces),'working_faces':len(b.Faces),'whole_source_unchanged':i>0})
ck('all_native_geometry_valid',all(o.Geometry.IsValid for o in F.Objects),len(F.Objects))
embeds=[]
for e in F.EmbeddedFiles:
    blob=base64.b64decode(F.GetEmbeddedFileAsBase64(e.Filename));expected=Path(e.Filename).read_bytes()
    ck('embedded_original_bytes_'+Path(e.Filename).name,blob==expected)
    embeds.append({'name':Path(e.Filename).name,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()})
scope=json.loads((O/'02_Data/V8_Allowed_Repair_Scope.json').read_text(encoding='utf-8'));allowed=unary_union([Polygon(p['outer'],p.get('holes',[])) for p in scope['polygons']]);Hdata=json.loads((O/'02_Data/Hole_Polygon.json').read_text());H=Polygon(Hdata['local']['outer'],Hdata['local']['holes'])
I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));coverage=[];counts=collections.Counter()
for r in I:
    d=np.load(O/'02_Data'/r['file']);v=d['vertices'];f=d['faces'];u=d['uv'];m=d['material_ids'];t=v[f]
    ck('finite_and_materials_'+r['name'],np.isfinite(v).all() and np.isfinite(u).all() and len(v)==len(u) and len(f)==len(m) and len(m)>0 and m.min()>=0 and m.max()<len(r['materials']))
    ck('nondegenerate_'+r['name'],bool((np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-10).all()))
    ck('vertices_authorized_scope_'+r['name'],bool(shapely.covers(allowed.buffer(1e-7),shapely.points(v[:,:2])).all()))
    xy=t[:,:,:2];ar=abs(np.cross(xy[:,1]-xy[:,0],xy[:,2]-xy[:,0]))/2;pol=shapely.polygons(xy[ar>1e-10]);cov=shapely.union_all(pol);coverage.append(cov)
    ck('footprint_authorized_scope_'+r['name'],cov.difference(allowed).area<1e-7)
    counts['patch_triangles']+=len(f)
    counts['photo_triangles']+=sum(int((m==j).sum()) for j,name in enumerate(r['materials']) if name.startswith(('PATCH_PHOTO_','BASE_PHOTO_','DJI_GABLE_')))
union=unary_union(coverage);residual=H.difference(union).area
ck('original_void_projection_covered',residual<1e-5,{'residual_m2':residual})
S=json.loads((O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));E={e['name']:e for e in S['elements']}
manifest=json.loads((W/'v8_terrain_clear/Merge_Manifest.json').read_text(encoding='utf-8'))
ck('west_removed_objects_absent_scene_and_native_patches',not(set(manifest['delete_names'])&set(E)) and not(set(manifest['delete_names'])&{r['name'] for r in I}))
from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location('interior_v8',W/'v8_interior/mutation.py');mod=module_from_spec(spec);spec.loader.exec_module(mod)
old=json.loads((V7/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));iq=mod.validate(S,old)
ck('merged_wall_stair_door_room_topology',iq['status']=='PASS',len(iq['checks']))
for z,target in [(0,3.77),(3.9,7.37)]:
    for x in [3.9,9.1]:
        e=E['ROMAN_COLUMN_X'+str(x)+'_Z'+str(z)];d=S['definitions'][e['definition']]
        ck(f'Roman_column_{x}_{z}_at_slab',abs(max(q[1] for p in d['parts'] for q in p['geometry']['profile'])+z-target)<1e-9)
    ck('Roman_arch_side_contact_'+str(z),'junction_v8' in E['PORCH_ARCH_BEAM_Z'+str(z)])
cks=S['v8_column_arch_changes']['checks'];ck('Roman_arch_boolean_contact_no_overlap',all(q['pass'] for q in cks))
eq=json.loads((O/'06_Report/Chinese_Eaves_Geometry_QA.json').read_text(encoding='utf-8'));ck('Chinese_closed_curved_eaves',eq['status']=='PASS_CLOSED_MANIFOLD_GEOMETRY')
ck('gate_kitchen_separation_positive',eq['gate_kitchen_separation_m_min']>0,eq['gate_kitchen_separation_m_min'])
C=json.loads((O/'02_Data/Coordinate.json').read_text());a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);names={o.Attributes.Name:o for o in F.Objects if not o.Attributes.IsInstanceDefinitionObject};hinges=[]
for r in S['door_registry']:
    if not r.get('leaf_element'):continue
    ob=names[r['leaf_element']];tr=ob.Geometry.Xform;expected=np.array(r['hinge_world_m'])@R.T+origin;actual=np.array([tr.M03,tr.M13,tr.M23]);err=float(np.linalg.norm(expected-actual));ck('native_leaf_actual_hinge_'+r['door_id'],err<1e-8);hinges.append({'id':r['door_id'],'error_m':err})
for k in ['DOOR_FRONT_CENTER_F2__SLIDE_1','DOOR_FRONT_CENTER_F2__SLIDE_2']:ck('independent_sliding_block_'+k,k in names and isinstance(names[k].Geometry,rh.InstanceReference))
report={'status':'PASS','checks':checks,'status_counts':dict(collections.Counter(c['status'] for c in checks)),'native_sha256':sha(native),'main_native':str(native),'original_source_sha256':sha(O/'01_Source/Pure_Site_UNMODIFIED.3dm'),'working_source_sha256':sha(O/'01_Source/Pure_Site_WORKING_V8.3dm'),'source_geometry_edits':'Base0 authorized west clearance only; four other source meshes fully retained; original source file unmodified','base':base_report,'counts':dict(counts),'native_objects':len(F.Objects),'embedded_original_images':embeds,'hinges':hinges,'original_void_projection_residual_m2':residual,'allowed_xy_area_m2':allowed.area,'limits':['Door offset and small opposite washroom boundary need field measurements.','Occluded cleared shed floors use interpolated terrain and provisional soil material.','Source preservation and model kernel QA are not construction survey precision or full scene watertight union certification.']}
(O/'06_Report/Independent_V8_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['checks','base','embedded_original_images','hinges']},ensure_ascii=False,indent=2),flush=True)
