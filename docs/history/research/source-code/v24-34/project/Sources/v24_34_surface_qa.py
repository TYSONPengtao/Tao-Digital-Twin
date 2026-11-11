from pathlib import Path
import sys,json,hashlib
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import numpy as np,shapely
from shapely.geometry import shape
D=W/'v24_34';O=Path('E:/jz/JIA/Rebuild_V24_34');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_34.blend';mask=shape(json.loads((D/'Existing_Coverage.geojson').read_text()));shapely.prepare(mask);checks=[];overlap=0.;outside=0.;parts=[];triangles=0;invalid=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('CHECK',n,bool(p),kw,flush=True)
for r in json.loads((D/'Final_Exterior_Index.json').read_text()):
 a=np.load(D/r['file']);v=a['v'].astype(np.float32).astype(float);f=a['f'];t=v[f,:2];ar=abs(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]));polys=shapely.polygons(t[ar>1e-9]);hit=shapely.intersects(mask,polys);overlap+=float(shapely.area(shapely.intersection(polys[hit],mask)).sum());outside+=float(ar.sum()/2);triangles+=len(f)
 # Exact union is calculated per tile and then globally, without counting
 # two roof/ground elevations twice in the coverage area.
 pieces=[shapely.union_all(polys[i:i+7000])for i in range(0,len(polys),7000)];parts.append(shapely.union_all(pieces))
coverage=shapely.union_all(parts);(D/'Added_Coverage.geojson').write_text(json.dumps(shapely.geometry.mapping(coverage)))
ck('Added exterior does not overlay existing native or context footprint',overlap<1e-5,overlap_projected_area_m2=overlap)
ck('Added exterior actually expands site coverage',coverage.area>1000,added_ground_projection_m2=coverage.area,existing_ground_projection_m2=mask.area)
rows=json.loads((D/'Missing_Exterior_Index.json').read_text());names={r['node']for r in rows};inv=json.loads((D/'OSGB_Inventory.json').read_text());links={x['name']:x['links']for x in inv['files']};ancestor=[]
for n in names:
 stack=list(links.get(n,[]));visited=set()
 while stack:
  q=stack.pop()
  if q in visited:continue
  visited.add(q)
  if q in names:ancestor.append((n,q))
  stack.extend(links.get(q,[]))
ck('No overlapping OSGB parent and child LOD are imported',not ancestor,ancestor_conflicts=ancestor)
ck('Every added tile is from the finest original non-overlapping frontier',names<=set(json.loads((D/'Frontier_27.json').read_text())),added_tiles=len(names),added_triangles=triangles)
reg=json.loads((D/'MB7_Registration.json').read_text());ck('Registration uses spatially distributed shared source features',reg['landmark_inliers']>=30 and reg['inlier_rms_m']<.2 and np.linalg.norm(np.array(reg['inlier_bbox_target'][1])-reg['inlier_bbox_target'][0])>40,landmarks=reg['landmark_inliers'],rms_m=reg['inlier_rms_m'],p95_m=reg['inlier_p95_m'],feature_scale=reg['feature_scale'])
clip=json.loads((D/'Clip_Report.json').read_text());ck('Only the missing part is retained',triangles<clip['source_triangles']*.5 and clip['seam_clearance_m']>=.005,retained_triangles=triangles,source_triangles=clip['source_triangles'])
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[r for r in checks if not r['pass']];(R/'V24_34_Surface_QA.json').write_text(json.dumps({'status':'PASS_MISSING_EXTERIOR_ONLY_AND_NO_LOD_DUPLICATES'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail},indent=2));print('SURFACE_QA',len(checks),'FAIL',len(fail),flush=True)
