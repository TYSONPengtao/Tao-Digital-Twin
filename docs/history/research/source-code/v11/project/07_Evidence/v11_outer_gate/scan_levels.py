# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import sys,math,json
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/'np1')]
import numpy as np
path=Path(r'E:/jz/JIA/Rebuild/05_Intermediate/Reality_Geometry.npz');a=np.load(path);p=a['points'].copy();ns=a['normals'].copy();angle=math.radians(19.65);R=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]]);p[:,:2]=(p[:,:2]-[-3.45191261,-3.90043098])@R;p[:,2]-=TAO_PRIVATE_SITE_002;ns[:,:2]=ns[:,:2]@R
rows=[]
for x,y in [(-14.65,-8.37),(-12.88,-12.7275),(-14.97732095,-8.32565608),(-12.50186517,-12.8632154),(-13.6,-10.5),(-15.41,-8.27),(-17.72,-7.95),(-19.7,-5.84)]:
 for r in [.20,.45]:
  sel=np.linalg.norm(p[:,:2]-[x,y],axis=1)<r;q=p[sel];n=ns[sel]
  row=dict(x=x,y=y,r=r,n=len(q),z_quantiles=np.quantile(q[:,2],[0,.05,.25,.5,.75,.95,.99,1]).tolist() if len(q) else None,near_vertical_count=int((abs(n[:,2])<.3).sum()),near_vertical_z_quantiles=np.quantile(q[abs(n[:,2])<.3,2],[0,.1,.5,.9,1]).tolist() if (abs(n[:,2])<.3).any() else None,ground_z_quantiles=np.quantile(q[(abs(n[:,2])>.75)&(q[:,2]<1.2),2],[.05,.25,.5,.95]).tolist() if ((abs(n[:,2])>.75)&(q[:,2]<1.2)).any() else None)
  rows.append(row)
  print(json.dumps(row))
(Path(__file__).parent/'Gate_Scan_Levels.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
