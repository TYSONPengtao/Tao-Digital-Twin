from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import cv2,numpy as np
D=W/'v24_34';a=cv2.imread(str(D/'MB7_Geographic_Seed_Top.png'),0);b=cv2.imread(str(D/'Existing_Context_Top.png'),0)
sift=cv2.SIFT_create(nfeatures=50000,contrastThreshold=.008)
a=cv2.GaussianBlur(cv2.createCLAHE(2.,(8,8)).apply(a),(3,3),.7);b=cv2.GaussianBlur(cv2.createCLAHE(2.,(8,8)).apply(b),(3,3),.7)
ka,da=sift.detectAndCompute(a,None);kb,db=sift.detectAndCompute(b,None)
good=[x for x,y in cv2.BFMatcher().knnMatch(da,db,k=2) if x.distance<.9*y.distance]
pa=np.float32([ka[m.queryIdx].pt for m in good]);pb=np.float32([kb[m.trainIdx].pt for m in good])
M,inl=cv2.estimateAffinePartial2D(pa,pb,method=cv2.RANSAC,ransacReprojThreshold=4,maxIters=100000)
assert M is not None and inl.sum()>12,(len(good),None if inl is None else int(inl.sum()))
def world(p):return (p-np.array([1280,1280]))*np.array([156/2560,-156/2560])+np.array([7,0])
mask=inl[:,0]>0;ra=world(pa[mask]);cb=world(pb[mask]);r={'matches':len(good),'inliers':int(mask.sum()),'affine_pixel':M.tolist(),'source_xy':ra.tolist(),'target_xy':cb.tolist(),'pixel_residual_m':float(np.sqrt(np.mean(np.sum((cv2.transform(pa[mask,None],M)[:,0]-pb[mask])**2,axis=1))))*156/2560}
(D/'SIFT_Matches.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items() if k not in ['source_xy','target_xy']})
canvas=cv2.drawMatches(cv2.imread(str(D/'MB7_Geographic_Seed_Top.png')),ka,cv2.imread(str(D/'Existing_Context_Top.png')),kb,[good[i]for i in np.flatnonzero(mask)[::max(1,int(mask.sum())//70)]],None,flags=2)
cv2.imwrite(str(D/'Registration_Matches.jpg'),canvas)
