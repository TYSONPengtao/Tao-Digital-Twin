import sys,json,hashlib,collections
from pathlib import Path
W=Path(__file__).parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W),str(W/'v6_reality_inventory')]
import numpy as np,shapely,mapbox_earcut,rhino3dm as rh
from shapely.geometry import Polygon,mapping
from shapely.geometry.polygon import orient
from nearest_photo_projection import closest_on_triangles
import export_v5 as ex
D=Path(__file__).parent;O=Path(r'E:/jz/JIA/Rebuild_V11_Hybrid')
S=json.loads((O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));ex.SCENE=S
I=json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'));idx={r['name']:r for r in I}
R=shapely.from_wkb((D/'Residual.wkb').read_bytes());ps=sorted([p for p in R.geoms if p.area>1e-8],key=lambda p:p.area,reverse=True)
groundrow=idx['PHOTO_BOUNDARY_GROUND_RECOVERY'];gd=np.load(O/'02_Data'/groundrow['file']);gt=gd['vertices'][gd['faces']]
gn=np.cross(gt[:,1]-gt[:,0],gt[:,2]-gt[:,0]);gn/=np.linalg.norm(gn,axis=1)[:,None];glo=gt[:,:,:2].min(1);ghi=gt[:,:,:2].max(1)
gm=(ghi[:,0]>-.9)&(glo[:,0]<.1)&(ghi[:,1]>-5.8)&(glo[:,1]<-3.8)&(abs(gn[:,2])>.7)&(gt[:,:,2].max(1)<.5)&(np.ptp(gt[:,:,2],axis=1)<.22)
source_ids=np.flatnonzero(gm);source_tri=gt[gm];source_xy=source_tri.copy();source_xy[:,:,2]=0
reference_vertices=[];reference_ids=[];reference_distance=[]
def terrain_z(xy):
 z=[]
 for q in xy:
  _,b,d=closest_on_triangles(np.repeat(np.r_[q,0.][None,:],len(source_tri),axis=0),source_xy);j=int(d.argmin());z.append(float(b[j]@source_tri[j,:,2]));reference_vertices.append(q.tolist());reference_ids.append(int(source_ids[j]));reference_distance.append(float(d[j]))
 return np.array(z)
parts=[];footprints=[];pieces=[]
for j,p in enumerate(ps):
 p=orient(p.simplify(1e-5,preserve_topology=True),sign=1)
 xy=np.array(p.exterior.coords[:-1]);footprints.append(p)
 if p.centroid.x>=0:
  g={'type':'prism_holes','outer':xy.tolist(),'holes':[],'z':-.48,'height':.03};parts.append({'geometry':g,'material':'M_Site_Paving'});pieces.append({'gap':j,'area_m2':p.area,'bounds':list(p.bounds),'parts':1,'top_z_m':-.45,'elevation_source':'Exact surrounding SITE_MAIN_COURTYARD_PAVING vertex grade -0.45m; V11 pavilion platform foundation also starts -0.45m.'})
 else:
  z=terrain_z(xy);tri=mapbox_earcut.triangulate_float64(xy,np.array([len(xy)],np.uint32)).reshape(-1,3);N=len(xy)
  v=np.vstack([np.c_[xy,z-.03],np.c_[xy,z]]);faces=[t[::-1].tolist() for t in tri]+[(t+N).tolist() for t in tri]
  faces.extend([[i,(i+1)%N,(i+1)%N+N,i+N] for i in range(N)])
  g={'type':'polyhedron','vertices':v.tolist(),'faces':faces};parts.append({'geometry':g,'material':'M_Soil'})
  pieces.append({'gap':j,'area_m2':p.area,'bounds':list(p.bounds),'parts':1,'top_z_range_m':[float(z.min()),float(z.max())],'elevation_source':'Nearest exact XY projection on original measured retained PHOTO_BOUNDARY_GROUND_RECOVERY low up-facing ground triangles. Abs(normal.z)>.7, maxZ<.5m, faceZspread<.22m reject low retaining-wall faces. Barycentric Z then triangulated to close only narrow ground strip.'})
e={'name':'SITE_V11_LOCAL_EXPOSED_PAVILION_GROUND_GAPS','layer':'60_SITE','family':'SITE_MODEL','confidence':'MEDIUM','source':'Read-only exact current V11 Patch projection residual; adjacent retained V10 site paving grade and original measured PHOTO_BOUNDARY_GROUND_RECOVERY low up-facing terrain triangles','status':'V11_ONLY_ACTUAL_PROJECTION_GROUND_GAPS; GROUND_GRADE_INHERITED_NOT_NEW_SURVEY','classification':'LOCAL_GROUND_ONLY_GAP_REPAIR','parts':parts,'repair_scope_area_m2':sum(p.area for p in footprints),'ground_top_source':'SITE_MAIN_COURTYARD_PAVING / screened PHOTO_BOUNDARY_GROUND_RECOVERY low terrain; no elevated roof is lowered into ground','nominal_thickness_m':.03}
coverage=[];tri3=[];checks=[];invalid=[];notclosed=[];minarea=1e9;model=rh.File3dm();model.Settings.ModelUnitSystem=rh.UnitSystem.Meters
for j,part in enumerate(parts):
 v,fs=ex.world_part(part,e);t=[]
 for f in fs:
  for ix in ex.triangulate(v[f]) if len(f)>3 else [[0,1,2]]:
   t.append(v[[f[k] for k in ix]])
 t=np.array(t);a=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2
 ob=ex.native(part['geometry']);valid=bool(ob.IsValid);closed=bool(ob.IsSolid);vol=abs(float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6));at=rh.ObjectAttributes();at.Name=e['name']+'__'+str(j+1);model.Objects.Add(ob,at)
 if not valid:invalid.append(j)
 if not closed:notclosed.append(j)
 minarea=min(minarea,float(a.min()));checks.append({'part':j,'native_type':type(ob).__name__,'valid':valid,'closed':closed,'positive_volume_m3':vol,'minimum_face_area_m2':float(a.min())});assert np.isfinite(t).all() and (a>1e-12).all(),(j,a.min());tri3.append(t)
 ta=t[:,:,:2];aa=abs(np.cross(ta[:,1]-ta[:,0],ta[:,2]-ta[:,0]))/2;coverage.append(shapely.union_all(shapely.polygons(ta[aa>1e-10])))
C=shapely.union_all(coverage);missing=R.difference(C);outside=C.difference(R)
allowed=json.loads((O/'02_Data/V11_Allowed_Repair_Scope.json').read_text(encoding='utf-8'));A=shapely.union_all([Polygon(p['outer'],p.get('holes',[])) for p in allowed['polygons']])
sourceproof={name:{'file':idx[name]['file'],'sha256':hashlib.sha256((O/'02_Data'/idx[name]['file']).read_bytes()).hexdigest()} for name in ['SITE_MAIN_COURTYARD_PAVING','PHOTO_BOUNDARY_GROUND_RECOVERY']}
qa={'status':'PASS_CANDIDATE' if not invalid and not notclosed and missing.area<1e-5 and outside.area<1e-7 else 'FAIL','input_residual_m2':R.area,'patch_xy_coverage_m2':C.area,'remaining_numerical_residual_m2':missing.area,'outside_true_gap_m2':outside.area,'outside_allowed_scope_m2':C.difference(A).area,'parts':len(parts),'triangles':sum(len(t) for t in tri3),'invalid_parts':invalid,'open_parts':notclosed,'minimum_face_area_m2':minarea,'per_gap':pieces,'native_checks':checks,'grade_reference_patch_proof':sourceproof,'west_earth_reference_triangle_ids':reference_ids,'west_earth_reference_query_xy':reference_vertices,'west_earth_reference_projection_distance_m_max':max(reference_distance,default=0),'west_earth_measured_donor_triangle_count':len(source_tri),'west_earth_donor_screen':'abs(normal.z)>.7; maxZ<.5m; faceZspread<.22m; local bbox[-.9,-5.8,.1,-3.8]. Low retaining-wall/photo triangles with positive z and steep normal rejected.','dropped_numerical_slivers_m2':sum(p.area for p in R.geoms if p.area<=1e-8),'scan_and_existing_mesh_uv_modified':False,'root_scene_and_deliverable_modified':False,'limits':'Only prepared candidate JSON in work folder. RhinoCommon validation after root merge remains required. Ground inherits existing modeled paving and locally measured original source ground grades, not newly certified field measurements. New photo UV is not assigned beyond actual measured source footprint.'}
mutation={'replace':[e],'remove':[],'materials':{},'construction_control':[{'names':[e['name']],'description':'Close only true newly exposed old-pavilion ground gaps and west-wall numerical contact strips after V11 footprint change.','evidence':[str(D/'Gaps.json'),str(D/'Geometry_QA.json')],'metric_status':'INHERITED_RETAINED_GROUND_GRADE; ACTUAL_XY_PATCH_RESIDUAL'}]}
(D/'Mutation.json').write_text(json.dumps(mutation,ensure_ascii=False,indent=2),encoding='utf-8');(D/'Geometry_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8');(D/'Repair_Projection.wkb').write_bytes(shapely.to_wkb(C));(D/'Remaining_After_Repair.wkb').write_bytes(shapely.to_wkb(missing));np.savez_compressed(D/'Candidate_Triangles.npz',triangles=np.concatenate(tri3))
assert model.Write(str(D/'Candidate_Ground_LOCAL.3dm'),8)
print(json.dumps({k:qa[k] for k in ['status','input_residual_m2','patch_xy_coverage_m2','remaining_numerical_residual_m2','outside_true_gap_m2','parts','triangles','invalid_parts','open_parts','west_earth_reference_projection_distance_m_max']},indent=2),flush=True)
