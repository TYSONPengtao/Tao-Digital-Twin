"""Collapse only indexed zero-area edges, without welding contacting native shells."""
from v26_2_common import *

def repair_indexed(v,f,mi,uv):
 vv=v.copy();ff=f.copy().astype(np.int64);mm=mi.copy();uu=uv.copy();repairs=[]
 for step in range(200):
  tt=vv[ff];ar=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)/2;bad=np.flatnonzero(ar<=1e-18)
  if not len(bad):break
  face=ff[bad[0]];edges0=[(int(face[i]),int(face[(i+1)%3]))for i in range(3)];edges0.sort(key=lambda e:np.linalg.norm(vv[e[0]]-vv[e[1]]));picked=None
  for i,j in edges0:
   length=float(np.linalg.norm(vv[i]-vv[j]));collinear=False
   if length>.002:
    err=0.
    for src,dst in[(i,j),(j,i)]:
     st=vv[ff[np.any(ff==src,axis=1)]];sn=np.cross(st[:,1]-st[:,0],st[:,2]-st[:,0]);sz=np.linalg.norm(sn,axis=1);good=sz>1e-18
     if good.any():err=max(err,float(np.max(abs(np.einsum('ij,ij->i',sn[good]/sz[good,None],vv[dst]-st[good,0])))))
    collinear=err<1e-8
    if not collinear:continue
   ni=set(ff[np.any(ff==i,axis=1)].ravel())-{i,j};nj=set(ff[np.any(ff==j,axis=1)].ravel())-{i,j}
   if len(ni&nj)!=2:continue
   picked=(i,j,length,collinear);break
  assert picked is not None,('No safe indexed edge collapse',step,tt[bad[0]].tolist())
  i,j,length,collinear=picked;ff[ff==j]=i;keep=np.array([len(set(q))==3 for q in ff]);ff=ff[keep];mm=mm[keep];uu=uu[keep];repairs.append({'kept_point_m':vv[i].tolist(),'discarded_point_m':vv[j].tolist(),'length_m':length,'plane_preserving_collinear':collinear})
 else:raise RuntimeError('Too many zero faces')
 used,rev=np.unique(ff.ravel(),return_inverse=True);vv=vv[used];ff=rev.reshape(-1,3);tt=vv[ff];ar=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)/2;ed=np.sort(np.concatenate([ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]]),axis=1);_,ct=np.unique(ed,axis=0,return_counts=True)
 assert ar.min()>1e-18 and np.all(ct==2) and len({tuple(sorted(q))for q in ff})==len(ff),(float(ar.min()),int((ct!=2).sum()))
 return vv,ff,mm,uu,{'local_collapses':repairs,'global_coordinate_welding':False,'minimum_triangle_area_m2':float(ar.min())}
