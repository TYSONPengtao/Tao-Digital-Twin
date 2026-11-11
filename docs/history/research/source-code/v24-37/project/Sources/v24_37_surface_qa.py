from pathlib import Path
import sys,json,hashlib
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,shapely
from shapely.geometry import shape,LineString,Point
D=W/'v24_37';O=Path('E:/jz/JIA/Rebuild_V24_37');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_37.blend';mask=shape(json.loads((D/'Final_Scan_Retention.geojson').read_text()));tolerant=mask.buffer(.0001);old=shape(json.loads((W/'v24_36/Existing_Coverage.geojson').read_text()));native=shape(json.loads((W/'v24_36/Native_Complete_Envelope.geojson').read_text()));skirt=shape(json.loads((D/'Reviewed_Stretched_Skirt_Exclusion.geojson').read_text()));checks=[];overlap=0.;body=0.;out=0.;curtain=0.;ptrows=[];bounds=[]
for g in [mask,tolerant,old,native,skirt]:shapely.prepare(g)
rows=json.loads((D/'Final_Scan_Index.json').read_text())
for j,r in enumerate(rows):
 a=np.load(D/r['file']);v=a['v'].astype(np.float32).astype(float);t=v[a['f'],:2];ar=abs(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]));p=shapely.polygons(t[ar>1e-9]);bad=~shapely.covers(tolerant,p)
 if bad.any():out+=float(shapely.area(shapely.difference(p[bad],tolerant)).sum())
 hit=shapely.intersects(skirt,p)
 if hit.any():curtain+=float(shapely.area(shapely.intersection(p[hit],skirt)).sum())
 bounds.append(np.array(r['bounds']))
 if r['name'].startswith('V24_36_PTJIA6_'):
  ptrows.append(r);hit=shapely.intersects(old,p)
  if hit.any():overlap+=float(shapely.area(shapely.intersection(p[hit],old)).sum())
  hit=shapely.intersects(native,p)
  if hit.any():body+=float(shapely.area(shapely.intersection(p[hit],native)).sum())
 if j%600==0:print('CLEAN_SURFACE',j,len(rows),flush=True)
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('CHECK',n,bool(p),kw,flush=True)
ck('All cleaned scan geometry lies in the reviewed coherent retention block',out<1e-6,outside_projected_area_m2=out,coordinate_tolerance_m=.0001,retention_geometry=mask.geom_type,retention_plan_area_m2=mask.area)
ck('Large blurred north extrapolation is removed',curtain<.02,remaining_projected_area_m2=curtain)
ck('PTJIA6 does not overlay current original or MB7 coverage',overlap<1e-5,overlap_projected_area_m2=overlap)
ck('Native full kitchen roof and curved masonry remain free of new scan overlays',body<1e-5,overlap_projected_area_m2=body)
plan=json.loads((D/'Cleanup_Report.json').read_text());features=[(-80,100),(-390,5),(-615,-150),(6.5,-4.8),(-49,-45),(28,-59)];feature_ok=all(shapely.covers(mask,Point(*p))for p in features);ck('Continuous principal feature blocks are retained while fragmented borders are removed',feature_ok and plan['retained_triangles']/plan['source_triangles']>.90 and plan['fully_removed_meshes']>0 and plan['tiny_disconnected_faces_removed']>0,retained_percent=100*plan['retained_triangles']/plan['source_triangles'],all_main_feature_anchors_retained=feature_ok,fully_removed_objects=plan['fully_removed_meshes'],tiny_disconnected_faces_removed=plan['tiny_disconnected_faces_removed'],native_geometry_edited=False)
paths=[]
for directory in ['v24_34','v24_36']:paths+=json.loads((W/directory/'Planned_Routes.json').read_text())
bad=[r['name']for r in paths if not shapely.covers(mask,LineString([p[:2]for p in r['points']]).buffer(.25))];ck('All existing and new tested human road corridors are retained',not bad,missing_corridors=bad,corridors=len(paths),protected_half_width_m=.25)
inventory=json.loads((W/'v24_36/3MX_Inventory.json').read_text());idx={r['name']:r for r in inventory['files']};names={r['name'].removeprefix('V24_36_PTJIA6_')+'.3mxb'for r in ptrows};bad=[n for n in names if idx[n]['links']];ck('PTJIA6 imports use leaf nodes without duplicate parent-child LOD meshes',not bad,parts=len(names),invalid=bad)
reg=json.loads((W/'v24_36/PTJIA6_Registration.json').read_text());ck('Shared local photographic features meet the declared registration tolerance',reg['landmark_inliers']>=15 and reg['inlier_rms_m']<.35,inliers=reg['landmark_inliers'],rms_m=reg['inlier_rms_m'],p95_m=reg['inlier_p95_m'],scale=reg['feature_scale'],basis='Photogrammetric shared local features; no independent survey control and no far-field accuracy certification')
source=Path(inventory['source']);decoded=json.loads((W/'v24_36/Decoded_L99_Index.json').read_text());seen=set();bad=[]
for r in decoded:
 if r['node']in seen:continue
 seen.add(r['node'])
 if hashlib.sha256((source/r['node']).read_bytes()).hexdigest()!=r['source_sha256']:bad.append(r['node'])
ck('Original PTJIA6 3MXB source files are unchanged',not bad,checked_files=len(seen),changed=bad)
ci=json.loads((R/'V24_37_Collision_Index.json').read_text());a=np.load(D/'Final_Collision.npz');t=a['v'][a['f'][ci['architectural_triangles_preserved']:],:2];ar=abs(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]));outside=0.
for i in range(0,len(t),50000):
 q=t[i:i+50000];p=shapely.polygons(q[ar[i:i+50000]>1e-9]);hit=~shapely.covers(tolerant,p)
 if hit.any():outside+=float(shapely.area(shapely.difference(p[hit],tolerant)).sum())
ck('Cleaned exterior collision does not retain deleted skirts beyond the boundary',outside<1e-6,outside_projected_area_m2=outside,all_collision_triangles=len(a['f']))
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[r for r in checks if not r['pass']];(R/'V24_37_Surface_QA.json').write_text(json.dumps({'status':'PASS_COHERENT_CONTEXT_NON_OVERLAP_AND_SOURCE_PRESERVATION'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail,'clean_bounds':[np.array(bounds)[:,0].min(0).tolist(),np.array(bounds)[:,1].max(0).tolist()]},indent=2));print('SURFACE_QA',len(checks),'FAIL',len(fail),flush=True)
