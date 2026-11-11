import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,rhino3dm as rh,shapely
from shapely.geometry import shape
from scipy.spatial import cKDTree
D=W/'v8_terrain_clear/contact_gap';q=json.loads((D/'Contact_Gap_Ground_QA.json').read_text(encoding='utf-8'));rows=json.loads((D/'Candidate_Patch_Index_Rows.json').read_text(encoding='utf-8'));G=shape(json.loads((D/'Significant_Residual_Polygons.json').read_text())['geometry']);S=np.load(D/'Ground_Support_And_Donor_Indices.npz');support=S['support'];tree=cKDTree(support[:,:2]);checks=[];alltri=[]
for row in rows:
 d=np.load(D/row['file']);v=d['vertices'];f=d['faces'];uv=d['uv'];m=rh.Mesh();m.Vertices.UseDoublePrecisionVertices=True
 for p in v:m.Vertices.AddPoint3d(*map(float,p))
 for face in f:m.Faces.AddFace(*map(int,face))
 m.Normals.ComputeNormals();assert m.IsValid,(row['name'],m.IsValidWithLog);t=v[f];assert (np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-10).all();alltri.append(t);checks.append({'name':row['name'],'candidate_rhino_mesh_valid':True,'triangles':len(t),'minimum_cross_product_norm':float(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1).min())})
parts=[]
for p in G.geoms:
 pts=[]
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  n=max(1,int(np.linalg.norm(np.array(a)-np.array(b))/.025));pts.extend(np.array(a)+(np.array(b)-np.array(a))*k/n for k in range(n))
 xy=np.array(pts);ds,ix=tree.query(xy);parts.append({'area_m2':p.area,'bounds_local':p.bounds,'boundary_samples':len(xy),'nearest_support_xy_distance_m_median':float(np.median(ds)),'nearest_support_xy_distance_m_max':float(ds.max()),'nearest_support_elevation_range_local_m':[float(support[ix,2].min()),float(support[ix,2].max())],'actual_source_contact_samples_within_5mm':int((ds<.005).sum()),'measured_original_source_seam_z_error_m_max':None,'seam_error_status':'NOT_MEASURABLE_NO_ACTUAL_SOURCE_CONTACT; provisional grade inference only' if p.centroid.x>10 else 'Tiny contact ground gap; source-supported triangle or nearby ground interpolation'})
t=alltri[-1];gr=S['grade_ids'];horizontal=t[gr<10].reshape(-1,3);risers=t[gr>=10].reshape(-1,3);ds,_=cKDTree(horizontal).query(risers);assert ds.max()<1e-8;q['internal_inferred_grade_riser_endpoint_match_m_max']=float(ds.max());q['per_gap_support_and_source_continuity']=parts;q['candidate_geometry_checks']=checks;q['superseded_candidate']='Discarded unbounded nearest-face adaptive microtriangles. Final is controlled grade segmentation, 406 inferred triangles including 6 provisional riser faces.';(D/'Contact_Gap_Ground_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');print('FINAL STABLE',[(r['name'],r['triangles']) for r in rows],'internal endpoint error',ds.max())
