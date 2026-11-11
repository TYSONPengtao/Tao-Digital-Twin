import sys,json,ast
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W/'v6_reality_inventory')]
import numpy as np,shapely
from scipy.spatial import cKDTree
from shapely.geometry import shape
from nearest_photo_projection import closest_on_triangles
D=W/'v8_terrain_clear/contact_gap';qa=json.loads((D/'Contact_Gap_Ground_QA.json').read_text(encoding='utf-8'));S=np.load(D/'Ground_Support_And_Donor_Indices.npz');base=S['base3_support_triangles'];bxy=base.copy();bxy[:,:,2]=0;btree=cKDTree(base[:,:,:2].mean(1));sup=S['support'];stree=cKDTree(sup[:,:2]);G=shape(json.loads((D/'Significant_Residual_Polygons.json').read_text())['geometry']);rows=json.loads((D/'Candidate_Patch_Index_Rows.json').read_text(encoding='utf-8'));new=[]
for r in rows:
 d=np.load(D/r['file']);new.append(d['vertices'][d['faces']])
new=np.concatenate(new);nxy=new.copy();nxy[:,:,2]=0;ntree=cKDTree(new[:,:,:2].mean(1))
def proj(xy,tri,tt,tree):
 k=min(64,len(tri));_,ii=tree.query(xy,k=k);ii=np.asarray(ii).reshape(len(xy),k);query=np.repeat(np.c_[xy,np.zeros(len(xy))],k,axis=0);_,w,dist=closest_on_triangles(query,tt[ii].reshape(-1,3,3));dist=dist.reshape(-1,k);w=w.reshape(-1,k,3);pick=dist.argmin(1);j=np.arange(len(xy));return (w[j,pick]*tri[ii[j,pick],:,2]).sum(1),dist[j,pick]
parts=[]
for p in G.geoms:
 pts=[]
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  n=max(1,int(np.linalg.norm(np.array(a)-np.array(b))/.025));pts.extend(np.array(a)+(np.array(b)-np.array(a))*k/n for k in range(n))
 xy=np.array(pts);ds,ids=stree.query(xy);zh,dh=proj(xy,new,nxy,ntree);row={'area_m2':p.area,'bounds_local':p.bounds,'boundary_samples':len(xy),'support_xy_distance_m_median':float(np.median(ds)),'support_xy_distance_m_max':float(ds.max()),'support_local_z_range_m':[float(sup[ids,2].min()),float(sup[ids,2].max())],'patch_edge_coverage_distance_m_max':float(dh.max())}
 if p.centroid.x>10:
  true,dist=proj(xy,base,bxy,btree);error=abs(zh-true);contact=dist<.005;iw=int(error.argmax());row['worst_boundary_point']={'xy':xy[iw].tolist(),'candidate_z':float(zh[iw]),'nearest_measured_projection_z':float(true[iw]),'source_projection_distance_xy_m':float(dist[iw])};row.update(nearest_measured_base_projection_xy_distance_m_max=float(dist.max()),nearest_measured_base_projection_xy_distance_m_min=float(dist.min()),edge_z_difference_to_nearest_measured_base_ground_projection_m_max=float(error.max()),edge_z_difference_to_nearest_measured_base_ground_projection_m_p95=float(np.percentile(error,95)),actual_source_contact_samples_within_5mm=int(contact.sum()),actual_source_contact_edge_z_error_m_max=float(error[contact].max()) if contact.any() else None)
 parts.append(row)
qa['per_gap_ground_support_and_edge_continuity']=parts;qa['existing_base_low_ground_coverage_m2']=0.;qa['significant_polygons_only']=4;qa['dropped_numerical_slivers_m2']=.31034868342669475-G.area;qa['continuity_note']='East ground heights project from nearby actual measured Base3 low terrain, preserving its lower level. The gap has no source ground footprint overlap; edge projection comparison is measured against nearest original ground surface, and exact XY contact samples are separately reported. Original UV is only retained on true source-supported triangles.';(D/'Contact_Gap_Ground_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(parts,indent=2))
