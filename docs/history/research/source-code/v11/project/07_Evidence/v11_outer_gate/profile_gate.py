# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import sys, json, math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/'np1')]
import numpy as np
O=Path(r'E:/jz/JIA/Rebuild_V10_Hybrid');S=json.loads((O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf8'))
for e in S['elements']:
 if 'SW_GATE' in e['name']:
  print('SCENE', e['name'],str(e)[:2200])
a=np.load(r'E:/jz/JIA/Rebuild/05_Intermediate/Reality_Geometry.npz');p=a['points'].copy();ns=a['normals'].copy();t=math.radians(19.65);R=np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]]);p[:,:2]=(p[:,:2]-[-3.45191261,-3.90043098])@R;p[:,2]-=TAO_PRIVATE_SITE_002;ns[:,:2]=ns[:,:2]@R
A=np.array([-14.65,-8.37]);B=np.array([-12.88,-12.7275]);u=(B-A)/np.linalg.norm(B-A);n=np.array([-u[1],u[0]]);s=(p[:,:2]-A)@u;q=(p[:,:2]-A)@n
rows=[]
for ss in np.linspace(0,np.linalg.norm(B-A),13):
 sel=(abs(s-ss)<.16)&(abs(q)<.10);z=p[sel,2];g=(abs(s-ss)<.22)&(q>.12)&(q<.6)&(abs(ns[:,2])>.65)&(p[:,2]<0);zz=p[g,2]
 row=dict(s=float(ss),z=np.quantile(z,[0,.1,.5,.9,.95,1]).tolist() if len(z) else [],n=len(z),interior_ground_z=np.quantile(zz,[.1,.5,.9]).tolist() if len(zz) else [],ground_count=len(zz));rows.append(row);print(json.dumps(row))
(Path(__file__).parent/'Gate_Scan_Profile.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
