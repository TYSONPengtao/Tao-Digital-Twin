import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'np1'));import cv2,numpy as np
O=W/'v24_03_dimension_audit';sm=json.loads((O/'projection_summary.json').read_text());a=cv2.imread(str(O/'reference2_top.png'),0);b=cv2.imread(str(O/'current_site_top.png'),0)
sift=cv2.SIFT_create(nfeatures=16000,contrastThreshold=.018);ka,da=sift.detectAndCompute(cv2.GaussianBlur(a,(3,3),.8),None);kb,db=sift.detectAndCompute(cv2.GaussianBlur(b,(3,3),.8),None)
good=[x for x,y in cv2.BFMatcher().knnMatch(da,db,k=2) if x.distance<.72*y.distance];pa=np.float32([ka[m.queryIdx].pt for m in good]);pb=np.float32([kb[m.trainIdx].pt for m in good]);M,inl=cv2.estimateAffinePartial2D(pa,pb,method=cv2.RANSAC,ransacReprojThreshold=3,maxIters=20000)
assert M is not None and inl.sum()>=6,(len(good),None if inl is None else inl.sum())
def world(p,label):
 s=sm[label];center=np.array(s['bbox']).reshape(2,3).mean(0);return (p-np.array([800,800]))/np.array([s['pixels_per_m'],-s['pixels_per_m']])+center[:2]
ra=world(pa[inl[:,0]>0],'reference2');cb=world(pb[inl[:,0]>0],'current_site');u,sv,v=np.linalg.svd((ra-ra.mean(0)).T@(cb-cb.mean(0)));rot=v.T@u.T
if np.linalg.det(rot)<0:v[-1]*=-1;rot=v.T@u.T
trans=cb.mean(0)-rot@ra.mean(0);seed={'matches':len(good),'inliers':int(inl.sum()),'rot':rot.tolist(),'trans':trans.tolist(),'world_rms_m':float(np.sqrt(np.mean(np.sum((ra@rot.T+trans-cb)**2,axis=1))))};(O/'Registration_Seed.json').write_text(json.dumps(seed,indent=2));print(seed,flush=True)
