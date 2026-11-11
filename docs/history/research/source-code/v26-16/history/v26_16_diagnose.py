from v26_2_common import *
from shapely.geometry import Polygon,box as box2
from shapely.ops import unary_union
D=W/'v26_16';I=D/'Input';J=json.loads((I/'Source_Index.json').read_text('utf8'));ix={r['name']:r for r in J['objects']};HN='V26_3_House_Connected_Walls_And_Stairs';r=ix[HN];a=np.load(I/r['file']);h=solid(a['v'],a['f']);tr=a['v'][a['f']];cn=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);area=np.linalg.norm(cn,axis=1)/2;cn/=np.maximum(area[:,None]*2,1e-30);c=tr.mean(1)
def sliced(m,z):
 pos=[];neg=[]
 for p in m.slice(z).to_polygons():
  p=np.asarray(p);sgn=np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1]);(pos if sgn>0 else neg).append(Polygon(p))
 return unary_union(pos).difference(unary_union(neg))
rows=[]
for z in[-.151,-.149,.20,.74,.76,1.4,2.15,2.99,3.06,3.14,3.16,3.25,3.319]:
 p=sliced(h,z).intersection(box2(3.4,1.65,4.3,2.5));rows.append({'z_m':z,'geometry':p.__geo_interface__});print('SECTION',z,p.wkt,flush=True)
(D/'Inner_Left_Jamb_Sections.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),'utf8')
from collections import defaultdict
planes=defaultdict(list);mask=(c[:,0]>3.6)&(c[:,0]<4.15)&(c[:,1]>1.8)&(c[:,1]<2.45)&(c[:,2]>-.16)&(c[:,2]<3.33)
for k in np.flatnonzero(mask):
 ax=int(np.argmax(abs(cn[k])));key=(ax,round(float(c[k,ax]),6),int(np.sign(cn[k,ax])),r['materials'][int(a['mi'][k])]);planes[key].append(k)
pp=[]
for key,ids in planes.items():
 tt=tr[ids];q={'plane':key,'area_m2':float(area[ids].sum()),'bounds_m':[tt.min((0,1)).tolist(),tt.max((0,1)).tolist()]};pp.append(q)
 if q['area_m2']>.0001:print('PLANE',q,flush=True)
(D/'Inner_Left_Jamb_Faces.json').write_text(json.dumps(pp,ensure_ascii=False,indent=2),'utf8')
