from pathlib import Path
import sys,json
W=Path(__file__).parent;D=W/'v26';FD=D/'Final';O=Path('E:/jz/JIA/Rebuild_V26');R=O/'Reports';sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]
import numpy as np,shapely
from shapely.geometry import shape,Polygon
from shapely.ops import unary_union
prepared='--prepared'in sys.argv
I={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};pr=json.loads((D/'Prepared_Ramp.json').read_text('utf8'))['proof'];region=shape(pr['region']);checks=[]
if prepared:FD=D;I={r['name']:r for r in json.loads((D/'Prepared_Ramp.json').read_text('utf8'))['objects']}
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw,flush=True)
def top(n):
 a=np.load(FD/I[n]['file']);t=a['v'][a['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ok=no[:,2]>.55*np.linalg.norm(no,axis=1);return t[ok]
photo=top('V26_Original_Site_Entrance_Ramp_0');road=top('V24_31_Continuous_Gray_Road_And_Storage_Approach');lo=np.array(region.bounds[:2])-.02;hi=np.array(region.bounds[2:])+.02
road=road[(road[:,:,0].max(1)>lo[0])&(road[:,:,0].min(1)<hi[0])&(road[:,:,1].max(1)>lo[1])&(road[:,:,1].min(1)<hi[1])]
pp=unary_union(shapely.polygons(photo[:,:,:2]));rp=unary_union(shapely.polygons(road[:,:,:2]));overlap=pp.intersection(rp).area;gap=region.difference(pp).area
ck('Recovered photo ramp continuously covers its intended footprint',gap<3e-5,missing_coverage_m2=gap,recovered_area_m2=pp.area)
ck('Recovered ramp and synthetic road have no positive-area duplicate top surface',overlap<5e-5,overlap_m2=overlap)
def heights(t,xy):
 A=t[:,1,:2]-t[:,0,:2];B=t[:,2,:2]-t[:,0,:2];Q=np.array(xy)-t[:,0,:2];det=np.cross(A,B);safe=np.where(abs(det)>1e-12,det,1);u=np.cross(Q,B)/safe;w=np.cross(A,Q)/safe;ok=(abs(det)>1e-12)&(u>=-1e-5)&(w>=-1e-5)&(u+w<=1.00001)
 if not ok.any():return None
 z=t[:,0,2]+u*(t[:,1,2]-t[:,0,2])+w*(t[:,2,2]-t[:,0,2]);return float(z[ok].max())
samples=[];miss=[];coords=np.array(region.exterior.coords)
for A,B in zip(coords,coords[1:]):
 for t in np.linspace(0,1,max(2,int(np.ceil(np.linalg.norm(B-A)/.04))+1)):
  q=A+(B-A)*t;z0=heights(photo,q);z1=heights(road,q)
  if z0 is not None and z1 is not None:samples.append({'xy_m':q.tolist(),'photo_z_m':z0,'road_z_m':z1,'difference_m':abs(z1-z0)})
  else:miss.append(q.tolist())
maximum=max((r['difference_m']for r in samples),default=999);ck('Actual saved ramp-to-road seam remains within 5 mm',maximum<.005 and len(samples)>100,samples=len(samples),maximum_seam_height_difference_m=maximum,unsampled_boundary_points=len(miss))
if 'SITE_V14_ORIGINAL_EXTERIOR_0_Geometry'in I:
 src=top('SITE_V14_ORIGINAL_EXTERIOR_0_Geometry');src=src[(src[:,:,0].max(1)>lo[0])&(src[:,:,0].min(1)<hi[0])&(src[:,:,1].max(1)>lo[1])&(src[:,:,1].min(1)<hi[1])];srcp=unary_union(shapely.polygons(src[:,:,:2]));overlap0=srcp.intersection(pp).area;ck('Existing original site and recovered ramp have one photo surface owner',overlap0<5e-5,overlap_m2=overlap0)
fail=[r for r in checks if not r['pass']];h=json.loads((R/'V26_Build.json').read_text('utf8'))['sha256'];((D/'Prepared_Ramp_Surface_QA.json')if prepared else(R/'V26_Ramp_Surface_QA.json')).write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':None if prepared else h,'prepared_geometry_only':prepared,'checks':checks,'failures':fail,'seam_samples':samples,'unsampled_boundary_xy':miss},ensure_ascii=False,indent=2),encoding='utf8');print('SURFACE_VERIFY_DONE',len(checks),'FAIL',len(fail),flush=True)
