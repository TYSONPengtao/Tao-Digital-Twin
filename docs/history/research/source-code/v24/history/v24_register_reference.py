import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import cv2,numpy as np
from scipy.spatial import cKDTree
O=W/'v24_03_dimension_audit';sm=json.loads((O/'projection_summary.json').read_text())
a=cv2.imread(str(O/'reference2_top.png'),0);b=cv2.imread(str(O/'current_site_top.png'),0)
sift=cv2.SIFT_create(nfeatures=16000,contrastThreshold=.018);ka,da=sift.detectAndCompute(cv2.GaussianBlur(a,(3,3),.8),None);kb,db=sift.detectAndCompute(cv2.GaussianBlur(b,(3,3),.8),None)
matches=cv2.BFMatcher().knnMatch(da,db,k=2);good=[x for x,y in matches if x.distance<.72*y.distance];pa=np.float32([ka[m.queryIdx].pt for m in good]);pb=np.float32([kb[m.trainIdx].pt for m in good]);M,inl=cv2.estimateAffinePartial2D(pa,pb,method=cv2.RANSAC,ransacReprojThreshold=3,maxIters=20000)
assert M is not None and inl.sum()>12,(len(good),None if inl is None else inl.sum())
def pixel_world(p,label):
 s=sm[label];bounds=np.array(s['bbox']).reshape(2,3);center=bounds.mean(0);return (p-np.array([800,800]))/np.array([s['pixels_per_m'],-s['pixels_per_m']])+center[:2]
ra=pixel_world(pa[inl[:,0]>0],'reference2');cb=pixel_world(pb[inl[:,0]>0],'current_site');u,sv,v=np.linalg.svd((ra-ra.mean(0)).T@(cb-cb.mean(0)));rot=v.T@u.T
if np.linalg.det(rot)<0:v[-1]*=-1;rot=v.T@u.T
trans=cb.mean(0)-rot@ra.mean(0);ref=np.load(O/'reference2_points.npz')['p'].astype(float);cur=np.load(O/'current_site_points.npz')['p'].astype(float)
rng=np.random.default_rng(24);cs=cur[rng.choice(len(cur),min(120000,len(cur)),False)];rs=ref[rng.choice(len(ref),min(70000,len(ref)),False)];tree=cKDTree(cs);T=np.eye(4);T[:2,:2]=rot;T[:2,3]=trans;T[2,3]=np.median(cur[:,2])-np.median(ref[:,2]);iterations=[]
for j in range(40):
 p=rs@T[:3,:3].T+T[:3,3];d,ind=tree.query(p,workers=4);cut=min(1.,float(np.quantile(d,.62)));mask=d<cut
 if mask.sum()<100:break
 x=p[mask];y=cs[ind[mask]];xc=x.mean(0);yc=y.mean(0);u,sv,v=np.linalg.svd((x-xc).T@(y-yc));r=v.T@u.T
 if np.linalg.det(r)<0:v[-1]*=-1;r=v.T@u.T
 t=yc-r@xc;D=np.eye(4);D[:3,:3]=r;D[:3,3]=t;T=D@T;iterations.append({'iteration':j,'rms_m':float(np.sqrt(np.mean(d[mask]**2))),'pairs':int(mask.sum()),'trim_limit_m':cut})
 if np.linalg.norm(t)<.0002 and np.linalg.norm(r-np.eye(3))<.00002:break
local=np.array(json.loads(Path('E:/jz/JIA/Rebuild_V23/02_Data/Coordinate.json').read_text())['local_to_survey']);C=np.linalg.inv(local)@T;aligned=ref@C[:3,:3].T+C[:3,3];np.savez_compressed(O/'reference2_LOCAL_points.npz',p=aligned.astype('float32'))
report={'status':'PASS_SITE_REFERENCE_REGISTRATION','reference':'E:/jz/实景三维场景模型2.3dm','method':'SIFT RANSAC on original textured point projections, rigid metric 3D ICP using stable overlapping site context; no scale fit','sift_matches':len(good),'sift_inliers':int(inl.sum()),'sift_world_rms_m':float(np.sqrt(np.mean(np.sum((ra@rot.T+trans-cb)**2,axis=1)))),'reference_to_JIA_survey':T.tolist(),'reference_to_model_LOCAL':C.tolist(),'icp_history':iterations,'aligned_reference_bbox_LOCAL':[aligned.min(0).tolist(),aligned.max(0).tolist()],'scale':1.0,'limitations':'Photogrammetric registration, not independently surveyed control; nearest-point residual does not prove hidden structure dimensions.'}
(O/'V24_03_Dimension_Audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k not in ['icp_history']},ensure_ascii=False),flush=True);print('FINAL ICP',iterations[-1],flush=True)
