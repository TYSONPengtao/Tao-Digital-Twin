# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
from pathlib import Path
import sys,json,math
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
D=W/'v24_36';pairs=json.loads((D/'Landmarks_3D.json').read_text());a=np.array([p['source']for p in pairs]);b=np.array([p['target']for p in pairs]);rng=np.random.default_rng(34)
def fit(x,y,scale=True):
 xc=x.mean(0);yc=y.mean(0);X=x-xc;Y=y-yc;u,s,v=np.linalg.svd(X.T@Y);r=v.T@u.T
 if np.linalg.det(r)<0:v[-1]*=-1;r=v.T@u.T
 k=float(np.sum((X@r.T)*Y)/np.sum(X*X)) if scale else 1.;t=yc-k*r@xc;T=np.eye(4);T[:3,:3]=k*r;T[:3,3]=t;return T
best=np.zeros(len(a),bool)
for _ in range(4000):
 ids=rng.choice(len(a),4,False);T=fit(a[ids],b[ids]);e=np.linalg.norm(a@T[:3,:3].T+T[:3,3]-b,axis=1);m=e<.40
 if m.sum()>best.sum():best=m
assert best.sum()>=15,int(best.sum())
T=fit(a[best],b[best]);e=np.linalg.norm(a@T[:3,:3].T+T[:3,3]-b,axis=1);keep=e<.4;T=fit(a[keep],b[keep]);initial=T.copy()
cloud=np.load(D/'Registration_Clouds.npz');rv,rf,cv,cf=[cloud[k]for k in ['rv','rf','cv','cf']]
def samples(v,f,count):
 tri=v[f];no=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(no,axis=1);no/=np.maximum(area[:,None],1e-12);ids=rng.choice(len(f),count,p=area/area.sum());w=rng.random((count,3));w=-np.log(np.maximum(w,1e-10));w/=w.sum(1)[:,None];return (tri[ids]*w[:,:,None]).sum(1),no[ids]
rp,rn=samples(rv,rf,100000);cp,cn=samples(cv,cf,350000);tree=cKDTree(cp);history=[]
# Rigid point-to-plane refinement leaves the feature-established metric scale fixed.
for it in range(40):
 x=rp@T[:3,:3].T+T[:3,3];d,ix=tree.query(x,workers=6);n=cn[ix];rot=T[:3,:3]/np.cbrt(np.linalg.det(T[:3,:3]));sn=rn@rot.T
 cut=.65 if it<8 else .4;mask=(d<cut)&(np.abs((n*sn).sum(1))>.85);xx=x[mask];nn=n[mask];yy=cp[ix[mask]];res=((yy-xx)*nn).sum(1);weights=np.minimum(1.,.10/np.maximum(abs(res),1e-6));A=np.c_[np.cross(xx,nn),nn];v=np.linalg.lstsq(A*weights[:,None],res*weights,rcond=None)[0];C=np.eye(4);C[:3,:3]=Rotation.from_rotvec(v[:3]).as_matrix();C[:3,3]=v[3:];T=C@T;history.append({'iteration':it,'pairs':int(mask.sum()),'point_plane_rms':float(np.sqrt(np.mean(res**2))),'nearest_rms':float(np.sqrt(np.mean(d[mask]**2)))})
 if np.linalg.norm(v)<1e-6:break
ee=np.linalg.norm(a@T[:3,:3].T+T[:3,3]-b,axis=1);seed=np.array(json.loads((D/'Coordinate_Seed.json').read_text())['seed_source_to_local']);final=T@seed;scale=float(np.cbrt(np.linalg.det(T[:3,:3])))
r={'status':'REGISTERED_PHOTOGRAMMETRIC_OVERLAP','method':'geographic seed, SIFT RANSAC, robust 3D similarity from shared textured surfaces; fixed-scale point-to-plane ICP on overlapping original site context','source':'D:/AJAVIS01/ContextCapture/CASES/新建工程/Productions/Production_PTJIA6/Scene/Data/Model','source_srs':'ENU:TAO_PRIVATE_SITE_004,TAO_PRIVATE_SITE_023','source_origin':[0,0,0],'source_to_model_LOCAL':final.tolist(),'seed_to_model_correction':T.tolist(),'feature_initial_correction':initial.tolist(),'feature_scale':scale,'landmarks':len(a),'landmark_inliers':int(keep.sum()),'inlier_bbox_target':[b[keep].min(0).tolist(),b[keep].max(0).tolist()],'inlier_rms_m':float(np.sqrt(np.mean(ee[keep]**2))),'inlier_p95_m':float(np.quantile(ee[keep],.95)),'icp':history,'datum_note':'The CC altitude datum differs from the current local model. Alignment uses actual shared roofs/roads, not an independently surveyed control network. Existing native coordinates are unchanged.'}
(D/'PTJIA6_Registration.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['icp','source_to_model_LOCAL','seed_to_model_correction','feature_initial_correction']},indent=2));print('ICP_FINAL',history[-1])
