from v26_2_common import *

def repair_native(v,f,mi,uv):
 vv=v.copy();ff=f.copy();mm=mi.copy();uu=uv.copy();repairs=[];sourceverts=set()
 vv,vi=np.unique(vv,axis=0,return_inverse=True);ff=vi[ff]
 keep=np.array([len(set(q))==3 for q in ff]);ff=ff[keep];mm=mm[keep];uu=uu[keep]
 for step in range(200):
  tt=vv[ff];ar=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)/2;bad=np.flatnonzero(ar<=1e-18)
  if not len(bad):break
  face=ff[bad[0]];edges0=[(int(face[i]),int(face[(i+1)%3]))for i in range(3)];edges0.sort(key=lambda e:np.linalg.norm(vv[e[0]]-vv[e[1]]))
  picked=None
  for i,j in edges0:
   length=float(np.linalg.norm(vv[i]-vv[j]))
   pure_collinear=False
   if length>.002:
    plane_error=0.
    for src,dst in[(i,j),(j,i)]:
     st=vv[ff[np.any(ff==src,axis=1)]];sn=np.cross(st[:,1]-st[:,0],st[:,2]-st[:,0]);sz=np.linalg.norm(sn,axis=1);good=sz>1e-18
     if good.any():plane_error=max(plane_error,float(np.max(abs(np.einsum('ij,ij->i',sn[good]/sz[good,None],vv[dst]-st[good,0])))))
    pure_collinear=plane_error<1e-8
    if not pure_collinear:continue
   ni=set(ff[np.any(ff==i,axis=1)].ravel())-{i,j};nj=set(ff[np.any(ff==j,axis=1)].ravel())-{i,j}
   if len(ni&nj)!=2:continue
   picked=(i,j,length,pure_collinear);break
  assert picked is not None,('No safe local zero-face edge collapse',step,tt[bad[0]].tolist())
  i,j,length,pure_collinear=picked
  if tuple(vv[j])in sourceverts and tuple(vv[i])not in sourceverts:i,j=j,i
  ff[ff==j]=i;keep=np.array([len(set(q))==3 for q in ff]);ff=ff[keep];mm=mm[keep];uu=uu[keep];repairs.append({'kept_point_m':vv[i].tolist(),'discarded_point_m':vv[j].tolist(),'edge_length_m':length,'plane_preserving_collinear':pure_collinear})
 else:raise RuntimeError('Too many collapsed boundary edges')
 vv,vi=np.unique(vv,axis=0,return_inverse=True);ff=vi[ff]
 from collections import defaultdict
 groups=defaultdict(list)
 for i,face in enumerate(ff):groups[tuple(sorted(face))].append(i)
 keep=np.ones(len(ff),bool);internal_removed=[]
 for ids in groups.values():
  if len(ids)==1:continue
  assert len(ids)==2
  t0,t1=vv[ff[ids[0]]],vv[ff[ids[1]]];n0=np.cross(t0[1]-t0[0],t0[2]-t0[0]);n1=np.cross(t1[1]-t1[0],t1[2]-t1[0]);assert n0@n1<0,('Same-facing repeated surface',ids)
  keep[ids]=False;internal_removed+=ids
 ff=ff[keep];mm=mm[keep];uu=uu[keep]
 used,rev=np.unique(ff.ravel(),return_inverse=True);vv=vv[used];ff=rev.reshape(-1,3);ss=solid(vv,ff,'Final native local edge collapse');tt=vv[ff];nn=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);ar=np.linalg.norm(nn,axis=1)/2;ed=np.sort(np.concatenate([ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]]),axis=1);_,ct=np.unique(ed,axis=0,return_counts=True)
 assert ar.min()>1e-18 and np.all(ct==2) and len({tuple(sorted(q))for q in ff})==len(ff),{'minimum_area':float(ar.min()),'bad_edge_count':int((ct!=2).sum()),'duplicate_triangles':len(ff)-len({tuple(sorted(q))for q in ff}),'repairs':repairs}
 return vv,ff,mm,uu,{'edge_repairs':repairs,'opposite_internal_faces_removed':internal_removed,'minimum_triangle_area_m2':float(ar.min())}
