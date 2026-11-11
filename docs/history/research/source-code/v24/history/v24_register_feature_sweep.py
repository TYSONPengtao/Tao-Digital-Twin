import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'np1'));import cv2,numpy as np
O=W/'v24_03_dimension_audit';a=cv2.imread(str(O/'reference2_top.png'),0);b=cv2.imread(str(O/'current_site_top.png'),0);rows=[]
for sigma in [1.5,3.,5.,8.]:
 aa=cv2.GaussianBlur(a,(0,0),sigma);bb=cv2.GaussianBlur(b,(0,0),sigma);s=cv2.SIFT_create(nfeatures=30000,contrastThreshold=.007,edgeThreshold=18);ka,da=s.detectAndCompute(aa,None);kb,db=s.detectAndCompute(bb,None)
 for ratio in [.78,.86,.92]:
  cand=[x for x,y in cv2.BFMatcher().knnMatch(da,db,k=2)if x.distance<ratio*y.distance];cand.sort(key=lambda x:x.distance);seen=set();good=[]
  for m in cand:
   if m.trainIdx not in seen:seen.add(m.trainIdx);good.append(m)
  pa=np.float32([ka[m.queryIdx].pt for m in good]);pb=np.float32([kb[m.trainIdx].pt for m in good]);M,mask=cv2.estimateAffinePartial2D(pa,pb,method=cv2.RANSAC,ransacReprojThreshold=5,maxIters=40000,confidence=.999)
  if M is None:continue
  take=mask[:,0]>0;x=pa[take];y=pb[take];span=np.ptp(x,axis=0);r={'sigma':sigma,'ratio':ratio,'matches':len(good),'inliers':int(take.sum()),'span_pixels':span.tolist(),'matrix':M.tolist(),'pixel_scale':float(np.linalg.norm(M[:,0])),'world_scale':float(np.linalg.norm(M[:,0])*16.30738/16.92546),'pairs_reference':x.tolist(),'pairs_current':y.tolist()};rows.append(r)
rows.sort(key=lambda r:r['inliers']*min(r['span_pixels'])/max(1,abs(r['world_scale']-1)*3),reverse=True);(O/'Feature_Sweep.json').write_text(json.dumps(rows,indent=2));print(json.dumps([{k:v for k,v in r.items()if not k.startswith('pairs')}for r in rows[:5]],indent=2))
