from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import numpy as np,shapely
from shapely.geometry import shape,Polygon
D=W/'v24_36';mask=shape(json.loads((D/'Existing_Coverage.geojson').read_text()));parts=[mask]if mask.geom_type=='Polygon'else list(mask.geoms);filled=shapely.union_all([Polygon(p.exterior)for p in parts]);print('MASK',mask.geom_type,'parts',len(parts),'area',mask.area,'filled',filled.area,'hull',mask.convex_hull.area)
a=np.load(D/'FINAL_Model_L22_0003232210.npz');t=a['v'][a['f']];pos=np.array([26,-13.5,4.4]);fw=np.array([13.8,-7.5,1.5])-pos;fw/=np.linalg.norm(fw);right=np.cross(fw,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,fw)
for x,y in [(1150,450),(1170,500)]:
 d=fw+right*(2*x/1500-1)*36/70+up*(1-2*y/1100)*26.4/70;d/=np.linalg.norm(d);e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0];h=np.cross(np.broadcast_to(d,e2.shape),e2);det=(e1*h).sum(1);good=abs(det)>1e-12;inv=np.where(good,1/np.where(good,det,1),0);s=pos-t[:,0];u=(s*h).sum(1)*inv;q=np.cross(s,e1);v=(q*d).sum(1)*inv;tt=(e2*q).sum(1)*inv;valid=good&(u>=0)&(v>=0)&(u+v<=1)&(tt>0);ds=np.where(valid,tt,np.inf);i=ds.argmin();p=pos+d*ds[i];print('BAD_RAY',x,y,p.tolist(),'FILLED_CONTAINS',filled.covers(shapely.Point(p[:2])),'HULL_CONTAINS',mask.convex_hull.covers(shapely.Point(p[:2])))
(D/'Filled_Current_Outline.geojson').write_text(json.dumps(shapely.geometry.mapping(filled)))
