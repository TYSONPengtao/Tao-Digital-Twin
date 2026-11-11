# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import sys,math,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1')]
import numpy as np
a=np.load(r'E:\jz\JIA\Rebuild\05_Intermediate\Reality_Geometry.npz');p=a['points'];t=math.radians(19.65);R=np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]]);p[:,:2]=(p[:,:2]-[-3.45191261,-3.90043098])@R;p[:,2]-=TAO_PRIVATE_SITE_002
for x,y in [(-14.65,-8.37),(-12.88,-12.7275),(-13.6,-10.5),(-15,-11),(-17,-11),(-13,-14),(-11,-10),(0,-10),(6,-12),(6,-3)]:
 q=p[(np.linalg.norm(p[:,:2]-[x,y],axis=1)<.65)&(abs(a['normals'][:,2])>.75)&(p[:,2]<1.2)]
 print(x,y,len(q),np.quantile(q[:,2],[0,.05,.25,.5,.75,.95,1]).round(3).tolist() if len(q) else [])
