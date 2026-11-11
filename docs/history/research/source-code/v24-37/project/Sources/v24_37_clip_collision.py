from pathlib import Path
import sys,json,time
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,shapely
from shapely.geometry import shape
D=W/'v24_37';O=Path('E:/jz/JIA/Rebuild_V24_37');R=O/'Reports';ci=json.loads((R/'V24_37_Collision_Index.json').read_text());a=np.load(D/'Raw_Collision.npz');v=a['v'];f=a['f'];nb=ci['architectural_triangles_preserved'];nv=ci['architectural_vertices_preserved'];mask=shape(json.loads((D/'Final_Scan_Retention.geojson').read_text()));shapely.prepare(mask);vs=[];fs=[];offset=0;clipped=0;dropped=0;start=time.perf_counter()
def polys(g):return[g]if g.geom_type=='Polygon'else[q for q in getattr(g,'geoms',[])if q.geom_type=='Polygon']
for k in range(nb,len(f),50000):
 t=v[f[k:k+50000]].astype(float);ar=np.abs(np.cross(t[:,1,:2]-t[:,0,:2],t[:,2,:2]-t[:,0,:2]));valid=ar>1e-9;pp=shapely.polygons(t[:,:,:2]);covers=shapely.covers(mask,pp);hits=shapely.intersects(mask,pp);keep=covers;keep[~valid]=shapely.contains_xy(mask,t[~valid].mean(1)[:,0],t[~valid].mean(1)[:,1]);partial=np.flatnonzero(hits&~covers&valid);vv=[t[keep].reshape(-1,3)];dropped+=int((~hits).sum());clipped+=len(partial)
 for i in partial:
  at=t[i];inv=np.linalg.inv(np.vstack([at[:,:2].T,np.ones(3)]))
  for p in polys(pp[i].intersection(mask)):
   if p.area<1e-9:continue
   for tr in shapely.constrained_delaunay_triangles(p).geoms:
    xy=np.array(tr.exterior.coords[:-1]);q=np.c_[xy,np.ones(3)]@inv.T@at
    if np.dot(np.cross(q[1]-q[0],q[2]-q[0]),np.cross(at[1]-at[0],at[2]-at[0]))<0:q=q[::-1]
    vv.append(q)
 if any(len(x)for x in vv):
  vv=np.concatenate(vv).reshape(-1,3,3).astype(np.float32);sel=np.linalg.norm(np.cross(vv[:,1]-vv[:,0],vv[:,2]-vv[:,0]),axis=1)>1e-8;vv=vv[sel].reshape(-1,3);vs.append(vv);fs.append(np.arange(offset,offset+len(vv),dtype=np.int32).reshape(-1,3));offset+=len(vv)
photo_v=np.concatenate(vs);photo_v,iv=np.unique(photo_v,axis=0,return_inverse=True);photo_f=iv[np.concatenate(fs)].astype(np.int32);vv=np.concatenate([v[:nv],photo_v]);ff=np.concatenate([f[:nb],photo_f+nv]);np.savez_compressed(D/'Final_Collision.npz',v=vv,f=ff);ci.update(all_triangles=len(ff),vertices=len(vv),boundary_clipped_faces=clipped,boundary_dropped_faces=dropped,boundary_clip_pending=False,all_bounds=[vv.min(0).tolist(),vv.max(0).tolist()]);(R/'V24_37_Collision_Index.json').write_text(json.dumps(ci,indent=2));print('COLLISION_CLIP_DONE',len(ff),clipped,dropped,'seconds',time.perf_counter()-start,flush=True)
