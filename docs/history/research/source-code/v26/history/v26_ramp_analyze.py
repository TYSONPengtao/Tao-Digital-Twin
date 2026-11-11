from pathlib import Path
import sys,json
W=Path(__file__).parent;D=W/'v26';sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]
import numpy as np
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};SI=json.loads((D/'Original_Source_Index.json').read_text('utf8'))
def top(a,limit=.55):
 t=a['v'][a['f']];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);return t[(n[:,2]>limit*np.linalg.norm(n,axis=1))]
def height(t,x,y):
 A=t[:,1,:2]-t[:,0,:2];B=t[:,2,:2]-t[:,0,:2];q=np.array([x,y])-t[:,0,:2];det=np.cross(A,B);safe=np.where(abs(det)>1e-10,det,1);u=np.cross(q,B)/safe;w=np.cross(A,q)/safe;ok=(abs(det)>1e-10)&(u>=-1e-6)&(w>=-1e-6)&(u+w<=1.000001);z=t[:,0,2]+u*(t[:,1,2]-t[:,0,2])+w*(t[:,2,2]-t[:,0,2]);return float(z[ok].max())if ok.any()else None
raw=[]
for r in SI['rows']:
 a=np.load(D/r['file']);t=top(a);t=t[(t[:,:,0].max(1)>-19)&(t[:,:,0].min(1)<-11)&(t[:,:,1].max(1)>-15)&(t[:,:,1].min(1)<-7)&(t[:,:,2].max(1)<.1)&(t[:,:,2].min(1)>-2)]
 if len(t):raw.extend(t)
raw=np.array(raw);nat=top(np.load(D/I['V24_31_Continuous_Gray_Road_And_Storage_Approach']['file']))
P0=np.array([-14.8813,-8.4793]);P1=np.array([-12.5895,-12.7096]);u=(P1-P0)/np.linalg.norm(P1-P0);inn=np.array([-u[1],u[0]])
for s in [.5,1.5,2.5,3.5,4.3]:
 for d in [-1.,-.5,0.,.3,.6,1.]:
  p=P0+u*s+inn*d;print('SAMPLE',s,d,np.round(p,3).tolist(),'original',height(raw,*p),'native',height(nat,*p))
print('RAMP_AREA',unary_union([Polygon(p[:,:2])for p in raw]).intersection(box(-18,-14.5,-11.8,-7.7)).area)
