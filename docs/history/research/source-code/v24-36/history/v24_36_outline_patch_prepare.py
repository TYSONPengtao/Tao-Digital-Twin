from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import numpy as np,shapely
from shapely.geometry import shape
D=W/'v24_36';oldmask=shape(json.loads((D/'Existing_Coverage.geojson').read_text()));filled=shape(json.loads((D/'Filled_Current_Outline.geojson').read_text()));mask=filled.buffer(.005);gap=filled.difference(oldmask).buffer(.006);shapely.prepare(mask);lo=np.array(mask.bounds[:2]);hi=np.array(mask.bounds[2:]);changes=[];remove=[]
def cut(v,f,uv=None,mi=None):
 t=v[f];low=t[:,:,:2].min(1);high=t[:,:,:2].max(1);near=(high[:,0]>lo[0])&(low[:,0]<hi[0])&(high[:,1]>lo[1])&(low[:,1]<hi[1]);ids=np.flatnonzero(near);hits=np.zeros(len(f),bool);covers=np.zeros(len(f),bool);polys=shapely.polygons(t[ids,:,:2]);hits[ids]=shapely.intersects(mask,polys);covers[ids]=shapely.covers(mask,polys);valid=abs(np.cross(t[:,1,:2]-t[:,0,:2],t[:,2,:2]-t[:,0,:2]))>1e-11;keep=~hits;keep[~valid]=~shapely.contains_xy(mask,t[~valid].mean(1)[:,0],t[~valid].mean(1)[:,1]);ff=[f[keep]];uout=[uv[keep]]if uv is not None else None;mout=[mi[keep]]if mi is not None else None;add=[];n=len(v);lookup={int(k):p for k,p in zip(ids,polys)}
 for i in np.flatnonzero(hits&~covers&valid):
  g=lookup[int(i)].difference(mask);parts=[g]if g.geom_type=='Polygon'else[q for q in getattr(g,'geoms',[])if q.geom_type=='Polygon'];a=t[i];inv=np.linalg.inv(np.vstack([a[:,:2].T,np.ones(3)]))
  for p in parts:
   if p.area<1e-10:continue
   for tri in shapely.constrained_delaunay_triangles(p).geoms:
    xy=np.array(tri.exterior.coords[:-1]);bc=np.c_[xy,np.ones(3)]@inv.T;q=bc@a;quv=bc@uv[i]if uv is not None else None
    if np.dot(np.cross(q[1]-q[0],q[2]-q[0]),np.cross(a[1]-a[0],a[2]-a[0]))<0:q=q[::-1];quv=quv[::-1]if quv is not None else None
    if np.linalg.norm(np.cross(q[1]-q[0],q[2]-q[0]))<1e-10:continue
    ff.append(np.array([[n,n+1,n+2]],np.int32));n+=3;add.append(q)
    if uout is not None:uout.append(quv[None])
    if mout is not None:mout.append(np.array([mi[i]],np.int32))
 vv=np.concatenate([v]+add);return vv,np.concatenate(ff),None if uout is None else np.concatenate(uout),None if mout is None else np.concatenate(mout),int(hits.sum())
rows=json.loads((D/'Final_Exterior_Index.json').read_text());source={r['node']:r for r in json.loads((D/'Missing_Exterior_Index.json').read_text())};newrows=[]
for r in rows:
 a=np.load(D/r['file']);v=a['v'];f=a['f'];bb=shapely.box(*v[:,:2].min(0),*v[:,:2].max(0))
 if not bb.intersects(gap):newrows.append(r);continue
 vv,ff,uv,mi,hits=cut(v,f,a['uv'],a['mi'])
 if not hits:newrows.append(r);continue
 if not len(ff):remove.append(r['name']);continue
 fn='PATCH_'+Path(r['source_node']).stem+'.npz';np.savez_compressed(D/fn,v=vv,f=ff,uv=uv,mi=mi);q={**r,'file':fn,'vertices':len(vv),'triangles':len(ff)};newrows.append(q);changes.append(q);print('OUTLINE_PATCH',r['name'],len(f),'->',len(ff),flush=True)
(D/'Final_Exterior_Index.json').write_text(json.dumps(newrows,indent=2));newsrc=[{**source[r['source_node']],'file':r['file'],'vertices':r['vertices'],'triangles':r['triangles']}for r in newrows];(D/'Missing_Exterior_Index.json').write_text(json.dumps(newsrc,indent=2));(D/'Existing_Coverage_Before_Filling_Gaps.geojson').write_text(json.dumps(shapely.geometry.mapping(oldmask)));(D/'Existing_Coverage.geojson').write_text(json.dumps(shapely.geometry.mapping(filled)))
a=np.load(D/'Final_Collision.npz');ci=json.loads(Path('E:/jz/JIA/Rebuild_V24_36/Reports/V24_36_Collision_Index.json').read_text());base=ci['previous_complete_model_triangles'];v,f,_,_,hits=cut(a['v'].astype(float),a['f'][base:]);f=np.concatenate([a['f'][:base],f]);np.savez_compressed(D/'Final_Collision.npz',v=v.astype(np.float32),f=f.astype(np.int32));(D/'Outline_Patch.json').write_text(json.dumps({'changed':changes,'remove':remove,'filled_internal_gap_area_m2':filled.area-oldmask.area,'new_triangles':sum(r['triangles']for r in newrows),'collision_triangles':len(f),'collision_trim_candidates':hits,'preserved_prior_collision_triangles':base},indent=2));print('PATCH_PREP_DONE',len(changes),len(remove),'GAP',filled.area-oldmask.area,flush=True)
