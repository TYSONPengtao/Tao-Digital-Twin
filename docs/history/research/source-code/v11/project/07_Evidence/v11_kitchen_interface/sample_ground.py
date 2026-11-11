import sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
from scipy.spatial import cKDTree
O=Path(__file__).parent;D=Path(r'E:/jz/JIA/Rebuild_V10_Hybrid/02_Data')
C=json.loads((D/'Coordinate.json').read_text());a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1.]])
ground=[]
for i in range(5):
    data=np.load(D/f'Base_{i}.npz');v=(data['vertices']-np.array(C['origin']))@R;f=data['faces']
    tri=v[f[:,:3]];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(n,axis=1);nn=n/np.maximum(length[:,None],1e-12)
    ct=tri.mean(1);good=(np.abs(nn[:,2])>.65)&(ct[:,2]<-.45)&(ct[:,2]>-5)&(ct[:,0]>7)&(ct[:,0]<17)&(ct[:,1]>-13)&(ct[:,1]<1)
    ground.extend(ct[good].tolist())
g=np.array(ground);tree=cKDTree(g[:,:2]);rows=[]
for x,y in [[13.6,float(y)] for y in np.linspace(-11.7,-2.6,10)]+[[float(x),-2.35] for x in np.linspace(7.7,13.35,7)]:
    d,ids=tree.query([x,y],k=8);q=g[ids];z=float(np.median(q[:,2]));rows.append(dict(point_local_m=[x,y],distance_xy_m=float(d[0]),median_ground_z_local_m=z,neighbors=q.tolist()))
(O/'Ground_Samples_ReadOnly.json').write_text(json.dumps(dict(rows=rows,source='Original source Base NPZ existing scans transformed ENU to local; surface normals abs Z>.65, centroid Z below courtyard. Candidate ground, not a field survey.'),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{k:v for k,v in r.items() if k!='neighbors'} for r in rows],ensure_ascii=False,indent=2))
