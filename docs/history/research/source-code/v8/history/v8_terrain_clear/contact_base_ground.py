import sys,json
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,shapely
from shapely.geometry import shape,Polygon
from shapely.ops import unary_union
O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');D=W/'v8_terrain_clear/contact_gap';D.mkdir(exist_ok=True);meta=json.loads((W/'v8_coverage_residual.json').read_text());gg=shape(meta['geometry']);ps=[p for p in gg.geoms if p.area>1e-7];G=unary_union(ps);C=json.loads((O/'02_Data/Coordinate.json').read_text());R=np.array(C['local_to_survey'])[:3,:3];org=np.array(C['origin']);basepolys=[];rows=[]
for i in range(5):
 d=np.load(O/'02_Data'/f'Base_{i}.npz');v=(d['vertices']-org)@R;f=d['faces'];t=v[f[:,:3]];mn=t[:,:,:2].min(1);mx=t[:,:,:2].max(1);b=G.bounds;near=(mx[:,0]>=b[0])&(mn[:,0]<=b[2])&(mx[:,1]>=b[1])&(mn[:,1]<=b[3]);tt=t[near];n=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-20);earth=(tt[:,:,2].max(1)<.5)&(abs(n[:,2])>.65);g=shapely.intersection(shapely.polygons(tt[earth,:,:2]),G);basepolys.append(shapely.union_all(g));rows.append({'base':i,'candidate_faces':len(tt),'low_upfaces':int(earth.sum()),'overlap_ground_m2':shapely.union_all(g).area})
basecov=unary_union(basepolys)
qa={'significant_gap_polygons':[{'area_m2':p.area,'bounds':p.bounds} for p in ps],'existing_base_ground_coverage_m2':basecov.area,'base':rows};(D/'Existing_Base_Ground_Coverage_QA.json').write_text(json.dumps(qa,indent=2));(D/'Significant_Residual_Polygons.json').write_text(json.dumps({'geometry':shapely.geometry.mapping(G),'total_m2':G.area},indent=2));print(json.dumps(qa,indent=2))
