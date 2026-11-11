import sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
O=Path(__file__).parent;D=Path(r'E:/jz/JIA/Rebuild_V10_Hybrid/02_Data')
C=json.loads((D/'Coordinate.json').read_text());a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1.]])
alltri=[]
for i in range(5):
    data=np.load(D/f'Base_{i}.npz');v=(data['vertices']-np.array(C['origin']))@R;f=data['faces'];tri=v[f[:,:3]];alltri.append(tri)
sys.path.insert(0,str(W/'v6_reality_inventory'))
from nearest_photo_projection import PhotoProjector
paths=list(Path(r'E:/jz/JIA/Productions/Production_OBJ (2)/Data').rglob('*.obj'))
M=np.linalg.inv(np.array(C['local_to_survey']))
projector=PhotoProjector.from_objs(paths,coordinate_transform=M)
t=projector.triangles;ct=t.mean(1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(n,axis=1);nn=n/np.maximum(length[:,None],1e-12)
scope=(ct[:,0]>12.8)&(ct[:,0]<15.5)&(ct[:,1]>-12)&(ct[:,1]<-2.4)&(ct[:,2]>-4)&(ct[:,2]<4)
vertical=scope&(np.abs(nn[:,0])>.50)&(np.abs(nn[:,2])<.50)
rows=[];edges=np.arange(12.8,15.501,.05)
for yy in np.arange(-11.5,-2.5,1):
 for label,z0,z1 in [('upper_gray_brick',-.4,2.2),('stone_retaining',-4,-.4)]:
    mask=vertical&(abs(ct[:,1]-yy)<.50)&(ct[:,2]>z0)&(ct[:,2]<z1);weights=length[mask]/2;h,_=np.histogram(ct[mask,0],edges,weights=weights);order=np.argsort(-h)
    peaks=[dict(x_center_m=float((edges[j]+edges[j+1])/2),mesh_area_m2=float(h[j])) for j in order[:8] if h[j]>0]
    rows.append(dict(y_center_local_m=float(yy),z_range=[z0,z1],label=label,triangle_count=int(mask.sum()),area_m2=float(weights.sum()),largest_x_area_bins=peaks))
near=t[scope];np.savez_compressed(O/'Registered_Kitchen_Wall_Section_LOCAL.npz',vertices=near.reshape(-1,3),faces=np.arange(len(near)*3).reshape(-1,3))
(O/'Registered_Mesh_Section_QA.json').write_text(json.dumps(dict(coordinate=C,source_objs=[str(p) for p in paths],source_triangles=len(t),source='Original JIA Production_OBJ (2) full photographed building source; local transformed with existing scene calibration',normals_filter='abs(nx)>.50 & abs(nz)<.50',rows=rows),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([dict(y=r['y_center_local_m'],label=r['label'],count=r['triangle_count'],peaks=r['largest_x_area_bins'][:3]) for r in rows],ensure_ascii=False,indent=2))
