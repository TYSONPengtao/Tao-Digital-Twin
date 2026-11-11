import sys,json
from pathlib import Path
import numpy as np
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'))
from scipy.spatial import cKDTree
O=W/'v24_03_dimension_audit';seed=json.loads((O/'Registration_Seed.json').read_text());ref=np.load(O/'reference2_points.npz')['p'].astype(float);cur=np.load(O/'current_site_points.npz')['p'].astype(float)
rng=np.random.default_rng(24);cs=cur[rng.choice(len(cur),min(120000,len(cur)),False)];rs=ref[rng.choice(len(ref),min(70000,len(ref)),False)];tree=cKDTree(cs);T=np.eye(4);T[:2,:2]=seed['rot'];T[:2,3]=seed['trans'];T[2,3]=seed.get('z_offset',float(np.median(cur[:,2])-np.median(ref[:,2])));history=[]
seed3=json.loads((O/'Registration_3D_Seed.json').read_text());T=np.array(seed3['matrix']);print('3D FEATURE INITIALIZER',seed3['inliers'],seed3['inlier_rms_m'],flush=True)
for j in range(45):
 p=rs@T[:3,:3].T+T[:3,3];d,ind=tree.query(p,workers=4);cut=min(1.5 if j<10 else .7,float(np.quantile(d,.60)));mask=d<cut
 if mask.sum()<100:break
 x=p[mask];y=cs[ind[mask]];xc=x.mean(0);yc=y.mean(0);u,sv,v=np.linalg.svd((x-xc).T@(y-yc));r=v.T@u.T
 if np.linalg.det(r)<0:v[-1]*=-1;r=v.T@u.T
 t=yc-r@xc;D=np.eye(4);D[:3,:3]=r;D[:3,3]=t;T=D@T;history.append({'iteration':j,'rms_m':float(np.sqrt(np.mean(d[mask]**2))),'pairs':int(mask.sum()),'trim_limit_m':cut})
 if np.linalg.norm(t)<.0002 and np.linalg.norm(r-np.eye(3))<.00002:break
local=np.array(json.loads(Path('E:/jz/JIA/Rebuild_V23/02_Data/Coordinate.json').read_text())['local_to_survey']);C=np.linalg.inv(local)@T;aligned=ref@C[:3,:3].T+C[:3,3];np.savez_compressed(O/'reference2_LOCAL_points.npz',p=aligned.astype('float32'))
report={'status':'PASS_SITE_REFERENCE_REGISTRATION','reference':'E:/jz/实景三维场景模型2.3dm','method':'Nine distributed texture/height feature landmarks, similarity RANSAC then full-context 3D ICP; fixed feature-derived scale during ICP','texture_feature_inliers':seed3['inliers'],'texture_landmark_rms_m':seed3['inlier_rms_m'],'reference_to_JIA_survey':T.tolist(),'reference_to_model_LOCAL':C.tolist(),'icp_history':history,'scale':seed3['fitted_scale'],'limitations':'Photogrammetric registration, not independent survey control. Nearest-point residual does not prove hidden construction dimensions.'};(O/'V24_03_Dimension_Audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('FINAL ICP',history[-1],flush=True)
