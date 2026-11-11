import sys,json,itertools
from pathlib import Path
import numpy as np
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'));from scipy.spatial import cKDTree
O=W/'v24_03_dimension_audit';sm=json.loads((O/'projection_summary.json').read_text());row=json.loads((O/'Feature_Sweep.json').read_text())[0]
ref=np.load(O/'reference2_points.npz')['p'].astype(float);cur=np.load(O/'current_site_points.npz')['p'].astype(float)
def world(p,label):
 s=sm[label];center=np.array(s['bbox']).reshape(2,3).mean(0);return (np.array(p)-[800,800])/[s['pixels_per_m'],-s['pixels_per_m']]+center[:2]
def landmarks(p,label,pixels):
 xy=world(pixels,label);tree=cKDTree(p[:,:2]);arr=[]
 for a in xy:
  ii=tree.query_ball_point(a,.20)
  if len(ii)<2:ii=np.atleast_1d(tree.query(a,k=8)[1])
  z=np.sort(p[ii,2]);arr.append([*a,float(np.median(z[-max(1,len(z)//4):]))])
 return np.array(arr)
A=landmarks(ref,'reference2',row['pairs_reference']);B=landmarks(cur,'current_site',row['pairs_current'])
def fit(a,b,scale=False):
 ac=a.mean(0);bc=b.mean(0);u,sv,v=np.linalg.svd((a-ac).T@(b-bc));r=v.T@u.T
 if np.linalg.det(r)<0:v[-1]*=-1;r=v.T@u.T
 s=sv.sum()/np.sum((a-ac)**2)if scale else 1.;t=bc-s*r@ac;return r,t,s
candidates=[]
for ids in itertools.combinations(range(len(A)),3):
 a=A[list(ids)];b=B[list(ids)]
 if np.linalg.norm(np.cross(a[1]-a[0],a[2]-a[0]))<25:continue
 for scale in [False,True]:
  r,t,s=fit(a,b,scale);d=np.linalg.norm(A@(s*r).T+t-B,axis=1);mask=d<.65;candidates.append((int(mask.sum()),float(-np.median(d)),scale,mask))
best=max(candidates,key=lambda c:c[:2]);mask=best[3];r,t,s=fit(A[mask],B[mask],best[2]);d=np.linalg.norm(A@(s*r).T+t-B,axis=1);T=np.eye(4);T[:3,:3]=s*r;T[:3,3]=t
seed={'method':'SIFT matching across northern roofs and southern site, top-surface heights from original meshes; 3D landmark RANSAC','inliers':int(mask.sum()),'landmarks':len(A),'fitted_scale':s,'matrix':T.tolist(),'pair_residuals_m':d.tolist(),'reference_points':A.tolist(),'current_points':B.tolist(),'inlier_rms_m':float(np.sqrt(np.mean(d[mask]**2)))};(O/'Registration_3D_Seed.json').write_text(json.dumps(seed,indent=2));print(json.dumps(seed,indent=2))
