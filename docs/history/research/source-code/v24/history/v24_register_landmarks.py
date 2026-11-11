import json,numpy as np
from pathlib import Path
O=Path(__file__).parent/'v24_03_dimension_audit';sm=json.loads((O/'projection_summary.json').read_text())
def world(p,label):
 s=sm[label];center=np.array(s['bbox']).reshape(2,3).mean(0);return (np.array(p)-[800,800])/[s['pixels_per_m'],-s['pixels_per_m']]+center[:2]
pa=[[664,352],[879,332],[687,625]];pb=[[338,315],[558,312],[355,609]];ra=world(pa,'reference2');cb=world(pb,'current_site');u,sv,v=np.linalg.svd((ra-ra.mean(0)).T@(cb-cb.mean(0)));rot=v.T@u.T;trans=cb.mean(0)-rot@ra.mean(0)
ref=np.load(O/'reference2_points.npz')['p'];cur=np.load(O/'current_site_points.npz')['p'];dz=[]
for a,b in zip(ra,cb):
 z1=ref[np.linalg.norm(ref[:,:2]-a,axis=1)<.8,2];z2=cur[np.linalg.norm(cur[:,:2]-b,axis=1)<.8,2];dz.append(float(np.quantile(z2,.8)-np.quantile(z1,.8)))
seed={'matches':3,'inliers':3,'rot':rot.tolist(),'trans':trans.tolist(),'z_offset':float(np.median(dz)),'world_rms_m':float(np.sqrt(np.mean(np.sum((ra@rot.T+trans-cb)**2,axis=1)))),'method':'Three corresponding northern courtyard roof corners, manually identified on original textured point projections; initializer only, refined with 3D context ICP','reference_pixels':pa,'current_pixels':pb,'individual_dz_m':dz};(O/'Registration_Seed.json').write_text(json.dumps(seed,indent=2));print(seed)
