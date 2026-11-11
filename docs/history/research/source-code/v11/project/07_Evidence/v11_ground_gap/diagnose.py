import sys,json,time,hashlib,argparse
from pathlib import Path
W=Path(__file__).parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,shapely
from shapely.geometry import Polygon,box,mapping
from shapely.ops import unary_union
args=argparse.ArgumentParser();args.add_argument('--package',default='E:/jz/JIA/Rebuild_V11_Hybrid');args.add_argument('--output-dir',default=str(Path(__file__).parent));options=args.parse_args()
O=Path(options.package);D=Path(options.output_dir);D.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def polys(g):
 if g.geom_type=='Polygon':return [g]
 return [x for x in g.geoms if x.geom_type=='Polygon']
hd=read(O/'02_Data/Hole_Polygon.json');H=Polygon(hd['local']['outer'],hd['local']['holes']);I=read(O/'02_Data/Patch_Index.json')
R=H;proof=[];unions=[];started=time.time()
priority=[r for r in I if any(k in r['name'] for k in ['GROUND','TERRAIN','SLAB','FLOOR','PHOTO_RIM'])]
remaining=[r for r in I if r not in priority];order=priority+sorted(remaining,key=lambda r:r['triangles'])
for ii,r in enumerate(order):
 p=O/'02_Data'/r['file'];d=np.load(p);t=d['vertices'][d['faces']][:,:,:2];area=abs(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]))/2
 mask=area>1e-10
 # A polygon cannot intersect R unless its bounding box overlaps one of R's polygon boxes.
 lo=t.min(axis=1);hi=t.max(axis=1);bm=np.zeros(len(t),bool)
 components=polys(R)
 for q in components:
  x0,y0,x1,y1=q.bounds
  bm|=(hi[:,0]>=x0-1e-9)&(lo[:,0]<=x1+1e-9)&(hi[:,1]>=y0-1e-9)&(lo[:,1]<=y1+1e-9)
 sel=np.flatnonzero(mask&bm);pre=R.area
 if len(sel):
  pp=shapely.polygons(t[sel]);good=shapely.intersects(pp,R);pp=pp[good]
  if len(pp):
   u=shapely.union_all(pp);unions.append(u);R=R.difference(u)
 else:pp=[]
 proof.append({'name':r['name'],'file':r['file'],'sha256':sha(p),'total_triangles':len(t),'bbox_candidates':len(sel),'intersecting_candidates':len(pp),'residual_before_m2':pre,'residual_after_m2':R.area})
 if pre-R.area>1e-7 or ii%25==0:print(ii,r['name'],'selected',len(sel),'intersect',len(pp),'residual',R.area,'seconds',round(time.time()-started,1),flush=True)
 if ii==len(priority)-1:
  (D/'Ground_Only_Candidate.wkb').write_bytes(shapely.to_wkb(R));(D/'Ground_Only_Candidate.json').write_text(json.dumps({'area_m2':R.area,'geometry':mapping(R)},ensure_ascii=False,indent=2),encoding='utf-8')
(D/'Residual.wkb').write_bytes(shapely.to_wkb(R));(D/'Covered_In_Hole.wkb').write_bytes(shapely.to_wkb(H.difference(R)))
out={'status':'PASS' if R.area<1e-5 else 'DIAGNOSED','total_m2':R.area,'hole_area_m2':H.area,'geometry':mapping(R),'components':[{'area_m2':p.area,'bounds':list(p.bounds),'geometry':mapping(p)} for p in sorted(polys(R),key=lambda p:p.area,reverse=True) if p.area>1e-10],'tiny_residual_m2':sum(p.area for p in polys(R) if p.area<=1e-10),'method':'Sequential exact difference from H; every indexed NPZ tested; projection triangles use checker XY area cutoff >1e-10; candidate bbox tests are conservative; no residual polygon is dropped during coverage; geometry intersects current residual then exact triangle union.','all_indexed_nodes_checked':len(proof)==len(I),'checker_xy_triangle_area_cutoff_m2':1e-10,'coverage_pass_tolerance_m2':1e-5,'source_index_sha256':sha(O/'02_Data/Patch_Index.json'),'hole_polygon_sha256':sha(O/'02_Data/Hole_Polygon.json'),'residual_wkb_sha256':sha(D/'Residual.wkb'),'covered_in_hole_wkb_sha256':sha(D/'Covered_In_Hole.wkb'),'patch_proof':proof,'elapsed_seconds':time.time()-started}
(D/'Gaps.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print('FINAL',R.area,'components',len(out['components']),flush=True)
