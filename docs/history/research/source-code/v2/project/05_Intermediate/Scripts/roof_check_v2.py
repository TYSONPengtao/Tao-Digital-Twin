import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
O=Path(r'E:\jz\JIA\Rebuild_V2');S=json.loads((O/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));a=np.load(r'E:\jz\JIA\Rebuild\05_Intermediate\Reality_Geometry.npz');p=a['points'];t=math.radians(19.65);R=np.array([[math.cos(t),-math.sin(t)],[math.sin(t),math.cos(t)]]);p[:,:2]=(p[:,:2]-S['coordinate']['origin'][:2])@R;p[:,2]-=S['coordinate']['origin'][2]
sel=(p[:,0]>3.1)&(p[:,0]<13.8)&(p[:,1]>.6)&(p[:,1]<10.6)&(p[:,2]>10.25)&(abs(a['normals'][:,2])>.4);q=p[sel];g=next(e for e in S['elements'] if e['name']=='ROOF_MAIN_JOINED')['parts'][0]['geometry'];v=np.array(g['vertices']);pred=np.full(len(q),np.nan)
for ff in g['faces'][:4]:
 p3=v[ff]
 for j in range(1,len(ff)-1):
  tri=p3[[0,j,j+1]];inv=np.linalg.inv(np.c_[tri[:,:2],np.ones(3)]);b=np.c_[q[:,:2],np.ones(len(q))]@inv;inside=(b>=-1e-5).all(1);pred[inside]=b[inside]@tri[:,2]
res=np.abs(q[:,2]-pred);res=res[np.isfinite(res)];j={'main_roof_face_samples':len(res),'median_m':float(np.median(res)),'p90_m':float(np.quantile(res,.9)),'p95_m':float(np.quantile(res,.95)),'maximum_m':float(res.max()),'method':'Vertical surface distance to linked OBJ2 centroids; registration has no independent control; not an accuracy certification'}
print(j);(O/'09_Report/Roof_Reality_Comparison.json').write_text(json.dumps(j,indent=2),encoding='utf-8')
for name,(x0,y0,x1,y1) in {'UTILITY':(.15,7,2.9,9.5),'METAL':(.4,1.8,2.9,6.0)}.items():
 qq=p[(p[:,0]>x0)&(p[:,0]<x1)&(p[:,1]>y0)&(p[:,1]<y1)&(p[:,2]>9)&(abs(a['normals'][:,2])>.5)];print(name,np.round(np.quantile(qq[:,2],[.1,.5,.9]),3))
