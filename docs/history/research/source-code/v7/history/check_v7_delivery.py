"""Read-back: exact intact photogrammetry invariance, scoped patches, user fixes."""
import sys,json,hashlib,math,collections
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh,shapely
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');V6=Path(r'E:\jz\JIA\Rebuild_V6_Hybrid');src=Path(r'E:\jz\纯场地版本.3dm');native=O/'04_Rhino/Reality_Hybrid_V7.3dm'
checks=[]
def ck(id,ok,detail=None):checks.append(dict(id=id,status='PASS' if ok else 'FAIL',detail=detail));assert ok,(id,detail)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
A=rh.File3dm.Read(str(src));B=rh.File3dm.Read(str(native));ob={str(x.Attributes.Id):x for x in B.Objects if not x.Attributes.IsInstanceDefinitionObject}
ck('source_copy_byte_identical',sha(src)==sha(O/'01_Source/Pure_Site_UNMODIFIED.3dm'))
for i,x in enumerate(A.Objects):
 y=ob[str(x.Attributes.Id)];a=x.Geometry;b=y.Geometry
 for prop,fields in [('Vertices',['X','Y','Z']),('TextureCoordinates',['X','Y']),('Normals',['X','Y','Z'])]:
  aa=np.array([[getattr(p,k) for k in fields] for p in getattr(a,prop)]);bb=np.array([[getattr(p,k) for k in fields] for p in getattr(b,prop)]);ck(f'base_{i}_{prop}_exact',np.array_equal(aa,bb),{'elements':len(aa),'double_precision_checked':True})
 ck(f'base_{i}_faces_exact',list(a.Faces)==list(b.Faces));ck(f'base_{i}_vertex_colors_exact',list(a.VertexColors)==list(b.VertexColors))
 ck(f'base_{i}_attributes_exact',x.Attributes.MaterialIndex==y.Attributes.MaterialIndex and x.Attributes.LayerIndex==y.Attributes.LayerIndex and x.Attributes.Name==y.Attributes.Name)
 ma=A.Materials[x.Attributes.MaterialIndex];mb=B.Materials[y.Attributes.MaterialIndex]
 for prop in ['Id','Name','DiffuseColor','Transparency','RenderMaterialInstanceId','RenderPlugInId','Shine','Reflectivity']:ck(f'base_{i}_material_{prop}',getattr(ma,prop)==getattr(mb,prop))
 ta=ma.GetBitmapTexture();tb=mb.GetBitmapTexture();ck(f'base_{i}_texture_binding',ta.Id==tb.Id and ta.FileName==tb.FileName)
 ck(f'base_{i}_original_pixels',sha(ta.FileName)==sha(O/'03_Textures/Base'/Path(ta.FileName).name))
 ck(f'base_{i}_texture_transform',all(getattr(ta.UvwTransform,f'M{j}{k}')==getattr(tb.UvwTransform,f'M{j}{k}') for j in range(4) for k in range(4)))
ck('native_all_objects_valid',all(x.Geometry.IsValid for x in B.Objects),{'objects':len(B.Objects)})
I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));HP=json.loads((O/'02_Data/Hole_Polygon.json').read_text());H=Polygon(HP['local']['outer'],HP['local']['holes']);coverage=[];counts=collections.Counter()
for row in I:
 d=np.load(O/'02_Data'/row['file']);v=d['vertices'];f=d['faces'];uv=d['uv'];mid=d['material_ids'];t=v[f]
 ck('patch_finite_'+row['name'],np.isfinite(v).all() and np.isfinite(uv).all() and len(uv)==len(v) and len(mid)==len(f) and mid.max()<len(row['materials']))
 xy=t[:,:,:2];ar=np.abs(np.cross(xy[:,1]-xy[:,0],xy[:,2]-xy[:,0]))/2;shapes=shapely.polygons(xy[ar>1e-10]);cov=shapely.union_all(shapes);coverage.append(cov);counts['patch_triangles']+=len(f);counts['photo_triangles']+=sum(int((mid==j).sum()) for j,m in enumerate(row['materials']) if m.startswith(('PATCH_PHOTO_','BASE_PHOTO_','DJI_GABLE_')))
 ck('scope_'+row['name'],cov.difference(H).area<1e-7)
 # Covers vertical geometry as well, allowing only clipping-roundoff epsilon.
 ck('all_vertices_in_hole_'+row['name'],bool(shapely.covers(H.buffer(1e-7),shapely.points(v[:,:2])).all()))
union=unary_union(coverage);outside=union.difference(H).area;residual=H.difference(union).area
ck('no_patch_outside_hole',outside<1e-7,{'area_m2':outside});ck('no_source_island_overlap',sum(union.intersection(Polygon(q)).area for q in H.interiors)<1e-7);ck('hole_xy_covered',residual<1e-5,{'residual_m2':residual})
old={r['name']:r for r in json.loads((V6/'02_Data/Patch_Index.json').read_text(encoding='utf-8'))};unchanged=0
finish_nodes={q['name'] for q in json.loads((O/'06_Report/Plain_White_Finish_Revision.json').read_text(encoding='utf-8'))['nodes']}
for r in I:
 if r['name'] in old and r['file']==old[r['name']]['file'] and r['name'] not in finish_nodes:
  ck('unchanged_patch_data_'+r['name'],sha(O/'02_Data'/r['file'])==sha(V6/'02_Data'/old[r['name']]['file']));unchanged+=1
for r in I:
 if r['name'].startswith(('PHOTO_BOUNDARY_','PHOTO_RIM_')):ck('measured_ground_and_rim_retained_'+r['name'],sha(O/'02_Data'/r['file'])==sha(V6/'02_Data'/old[r['name']]['file']))
S=json.loads((O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));E={e['name']:e for e in S['elements']}
def occupied(name,x,y,z):
 return any(g['z']-1e-7<z<g['z']+g['height']+1e-7 and Polygon(g['outer'],g['holes']).covers(Point(x,y)) for p in E[name]['parts'] if (g:=p['geometry'])['type']=='prism_holes')
ck('F2_stair_front_closed',all(occupied('PARTITIONS_JOINED_F2',x,7.3,z) for x in [4.4,5.5,6.8,7.5] for z in [4.2,5.5,6.7]))
ck('F3_marked_wall_removed',not any(occupied('PARTITIONS_JOINED_F3',x,7.3,z) for x in [.4,1.5,2.8,3.4] for z in [7.8,8.5,9.9]))
ck('F3_side_door_opening',not any(occupied('PARTITIONS_JOINED_F3',3.9,y,z) for y in [7.6,7.9,8.4] for z in [7.8,8.7,9.5]))
ck('F3_separator_present',all(occupied('PARTITIONS_JOINED_F3',3.9,y,z) for y in [1.5,3,5,6.8,8.8] for z in [7.8,8.7,9.5]))
fo=E['DOOR_LAUNDRY_F3__FRAME'];le=E['DOOR_LAUNDRY_F3__LEAF'];ck('F3_exit_on_perpendicular_X_wall',fo['origin']==[3.9,7.55,7.5] and abs(fo['angle']-math.pi/2)<1e-9)
ck('gable_closed_native_geometry_present',len(E['CANOPY_FRONT_CLOSED_GABLE']['parts'])>0)
ck('F2_old_opaque_rail_retired','BALCONY_STONE_JOINED' not in E and 'BALCONY_STONE_COPING_JOINED' not in E)
ck('old_mouldings_retired',not any(k.startswith('BALCONY_STONE_PANEL_MOULDING_') for k in E))
ck('F2_sliding_leaf_pair',all(E[k]['role']=='SLIDING_LEAF' for k in ['DOOR_FRONT_CENTER_F2__SLIDE_1','DOOR_FRONT_CENTER_F2__SLIDE_2']))
# Read actual instance locations, not only metadata.
C=json.loads((O/'02_Data/Coordinate.json').read_text());a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin']);names={x.Attributes.Name:x for x in B.Objects if not x.Attributes.IsInstanceDefinitionObject};hinges=[]
for r in S['door_registry']:
 if not r.get('leaf_element'):continue
 x=names[r['leaf_element']];tr=x.Geometry.Xform;expected=np.array(r['hinge_world_m'])@R.T+origin;actual=np.array([tr.M03,tr.M13,tr.M23]);err=float(np.linalg.norm(expected-actual));hinges.append(dict(leaf=r['leaf_element'],error_m=err));ck('actual_hinge_'+r['door_id'],err<1e-8)
for k in ['DOOR_FRONT_CENTER_F2__SLIDE_1','DOOR_FRONT_CENTER_F2__SLIDE_2']:ck('independent_sliding_instance_'+k,k in names and isinstance(names[k].Geometry,rh.InstanceReference))
report=dict(main_native=str(native),native_sha256=sha(native),source_sha256=sha(src),checks=checks,counts=dict(counts),status_counts=dict(collections.Counter(c['status'] for c in checks)),source_original_meshes=len(A.Objects),unchanged_patch_npz_count=unchanged,xy_hole_residual_m2=residual,patch_outside_m2=outside,detail_counts=S['v7_detail_counts'],hinges=hinges,native_embedded_images=len(B.EmbeddedFiles),limit='Geometry/topology and source-preservation QA; not a field measurement accuracy or watertight Boolean union certification')
(O/'06_Report/Independent_V7_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['checks','hinges']},ensure_ascii=False,indent=2),flush=True)
