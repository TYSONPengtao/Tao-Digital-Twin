import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,shapely
from shapely.geometry import shape
from scipy.spatial import cKDTree
D=W/'v8_terrain_clear/contact_gap';s=np.load(D/'Ground_Support_And_Donor_Indices.npz')['support'];tree=cKDTree(s[:,:2]);meta=json.loads((D/'Significant_Residual_Polygons.json').read_text());G=shape(meta['geometry']);rows=[]
for p in G.geoms:
 points=np.array(list(p.exterior.coords));ds,ids=tree.query(points,k=1);rows.append({'area_m2':p.area,'bounds_local':p.bounds,'nearest_measured_support_distance_m_max':float(ds.max()),'nearest_measured_support_distance_m_median':float(np.median(ds)),'nearest_measured_support_z_range_m':[float(s[ids,2].min()),float(s[ids,2].max())]})
q=json.loads((D/'Contact_Gap_Ground_QA.json').read_text(encoding='utf-8'));q['per_gap_ground_support']=rows;q['existing_base_low_ground_coverage_m2']=0.0;q['significant_polygons_only']=4;q['dropped_numerical_slivers_m2']=.31034868342669475-G.area;(D/'Contact_Gap_Ground_QA.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rows,indent=2))
