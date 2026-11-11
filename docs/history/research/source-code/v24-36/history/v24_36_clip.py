from pathlib import Path
import sys,json,time
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,shapely
from shapely.geometry import shape,mapping,box
D=W/'v24_36';O=D/'Missing_Exterior';O.mkdir(exist_ok=True);T=np.array(json.loads((D/'PTJIA6_Registration.json').read_text())['source_to_model_LOCAL']);index=json.loads((D/'Geometry_Index.json').read_text());start=time.perf_counter()
def projected(v,f):
 t=np.round(v[f,:2],6);area=np.abs(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]));t=t[area>1e-9];pp=shapely.polygons(t);pieces=[]
 for i in range(0,len(pp),7000):pieces.append(shapely.union_all(pp[i:i+7000]))
 return shapely.union_all(pieces)
coveragefile=D/'Existing_Coverage.geojson'
if coveragefile.exists():mask=shape(json.loads(coveragefile.read_text()))
else:
 pieces=[shape(json.loads((W/'v14/Merge_Boundary_LOCAL.json').read_text()))]
 for r in index:
  if r['name']=='V24_21_Navigation_Collision':continue
  a=np.load(D/r['file']);p=projected(a['v'],a['f']);pieces.append(p);print('COVERAGE',r['name'],round(p.area,3),flush=True)
 mask=shapely.union_all(pieces).buffer(0);coveragefile.write_text(json.dumps(mapping(mask)))
# A 5 mm seam avoids coincident source faces; the original mesh is immutable.
mask=mask.buffer(.005);shapely.prepare(mask);rows=[];skipped=[];triangles=0;cuts=0;area_out=0
def polys(g):return [g]if g.geom_type=='Polygon'else[q for q in getattr(g,'geoms',[])if q.geom_type=='Polygon']
for j,r in enumerate(json.loads((D/'Decoded_L99_Index.json').read_text())):
 if not r['triangles']:skipped.append({'node':r['node'],'reason':'empty source leaf'});continue
 a=np.load(D/r['file']);v=a['v']@T[:3,:3].T+T[:3,3];f=a['f'];uv=a['uv'];mi=a['mi'];t=v[f];bb=box(*v[:,:2].min(0),*v[:,:2].max(0))
 if shapely.covers(mask,bb):skipped.append({'node':r['node'],'reason':'existing coverage'});continue
 ar=np.abs(np.cross(t[:,1,:2]-t[:,0,:2],t[:,2,:2]-t[:,0,:2]));valid=ar>1e-10;pp=shapely.polygons(t[:,:,:2]);covers=shapely.covers(mask,pp);hits=shapely.intersects(mask,pp);keep=~hits;keep[~valid]=~shapely.contains_xy(mask,t[~valid].mean(1)[:,0],t[~valid].mean(1)[:,1]);partial=np.flatnonzero(hits&~covers&valid)
 vv=[t[keep].reshape(-1,3)];uu=[uv[keep]];mm=[mi[keep]];cutarea=0
 for i in partial:
  g=pp[i].difference(mask);at=t[i];inv=np.linalg.inv(np.vstack([at[:,:2].T,np.ones(3)]))
  for p in polys(g):
   if p.area<1e-10:continue
   for tri in shapely.constrained_delaunay_triangles(p).geoms:
    xy=np.array(tri.exterior.coords[:-1]);weights=np.c_[xy,np.ones(3)]@inv.T;q=weights@at;quv=weights@uv[i]
    if np.dot(np.cross(q[1]-q[0],q[2]-q[0]),np.cross(at[1]-at[0],at[2]-at[0]))<0:q=q[::-1];quv=quv[::-1]
    vv.append(q);uu.append(quv[None]);mm.append(np.array([mi[i]],np.int32));cutarea+=tri.area
 if not any(len(x)for x in vv):skipped.append({'node':r['node'],'reason':'existing exact footprint'});continue
 vv=np.concatenate(vv);uu=np.concatenate(uu);mm=np.concatenate(mm);ff=np.arange(len(vv),dtype=np.int32).reshape(-1,3);tr=vv[ff];valid3=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1)>1e-10;vv=tr[valid3].reshape(-1,3);uu=uu[valid3];mm=mm[valid3];ff=np.arange(len(vv),dtype=np.int32).reshape(-1,3)
 # Weld geometry coordinates only. UV remains face-corner data to retain seams.
 vv,iv=np.unique(vv,axis=0,return_inverse=True);ff=iv[ff].astype(np.int32);dest=O/(Path(r['node']).stem+'.npz');np.savez_compressed(dest,v=vv,f=ff,uv=uu,mi=mm);triangles+=len(ff);cuts+=len(partial);area_out+=float(ar[keep].sum()/2+cutarea)
 rows.append({**r,'file':str(dest.relative_to(D)),'vertices':len(vv),'triangles':len(ff),'bounds':[vv.min(0).tolist(),vv.max(0).tolist()],'source_triangles':r['triangles'],'uncut_triangles':int(keep.sum()),'clipped_source_triangles':len(partial)})
 if j%50==0:print('CLIP',j,'/',2117,'retained',len(rows),'triangles',triangles,flush=True)
(D/'Missing_Exterior_Index.json').write_text(json.dumps(rows,indent=2));report={'source_leaf_count':2117,'nonempty_source_leaves':2116,'source_triangles':6032331,'added_tiles':len(rows),'added_triangles':triangles,'clipped_source_triangles':cuts,'existing_protected_footprint_m2':mask.area,'added_projected_triangle_area_m2':area_out,'seam_clearance_m':.005,'skipped':skipped,'method':'non-overlapping finest OSGB leaf frontier; exact projected triangle subtraction outside existing native context and central reconstruction, original JPEG bytes and barycentric UV preservation','seconds':time.perf_counter()-start};(D/'Clip_Report.json').write_text(json.dumps(report,indent=2));print('CLIP_DONE',{k:v for k,v in report.items()if k!='skipped'},flush=True)
