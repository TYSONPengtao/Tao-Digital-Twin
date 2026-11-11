from v26_2_common import *
from shapely.geometry import Polygon,box,mapping,GeometryCollection
D=W/'v26_19';J=json.loads((D/'Input/Source_Index.json').read_text('utf8'));r=next(r for r in J['objects']if r['name']=='V26_3_House_Connected_Walls_And_Stairs');a=np.load(D/'Input'/r['file']);m=solid(a['v'],a['f']);t=a['v'][a['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ar=np.linalg.norm(no,axis=1)/2;no/=np.maximum(2*ar[:,None],1e-30)
def plan(z):
 p=GeometryCollection()
 for ring in m.slice(z).to_polygons():p=p.symmetric_difference(Polygon(ring))
 return p
samples=[]
for fl,z in[(1,3.05),(2,6.65),(3,9.95)]:
 for dz in[-.02,.02,.20,.269]:
  q=plan(z+dz).intersection(box(-.25,7.0,11.,7.7));row={'floor':fl,'z':z+dz,'plan':mapping(q)};samples.append(row)
  if fl==3:print('F3_PLAN',z+dz,str(mapping(q))[:6500],flush=True)
from collections import defaultdict
g=defaultdict(list);mask=(t[:,:,0].max(1)>-.21)&(t[:,:,0].min(1)<.4)&(t[:,:,1].max(1)>7.05)&(t[:,:,1].min(1)<7.7)&(t[:,:,2].max(1)>9.90)&(t[:,:,2].min(1)<10.23)
for i in np.flatnonzero(mask):g[(tuple(np.round(no[i],4)),round(float(no[i]@t[i,0]),5),r['materials'][a['mi'][i]])].append(int(i))
for k,ids in sorted(g.items(),key=lambda q:-ar[q[1]].sum()):
 if ar[ids].sum()>.000001:print('WEST_PLANE',k,float(ar[ids].sum()),[t[ids].min((0,1)).tolist(),t[ids].max((0,1)).tolist()],flush=True)
(D/'Structure_Sections.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2),'utf8')
