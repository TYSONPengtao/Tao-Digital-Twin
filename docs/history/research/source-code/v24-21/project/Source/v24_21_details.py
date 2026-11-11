"""Native exterior frieze from photo 025022; retain all original architecture."""
from pathlib import Path
import json,sys,math
W=Path(__file__).parent;sys.path.insert(0,str(W))
import v24_16_common as base
base.D=W/'v24_21';base.INDEX={r['name']:r for r in json.loads((base.D/'Inventory.json').read_text())};base.OUT={'objects':[],'proof':{}}
from v24_16_common import *
from shapely.geometry import LineString

records=json.loads((W/'v19/Facade_Segments.json').read_text())['brick'];edges=[]
for r in records:
 a=np.array(r['a']);b=np.array(r['b']);L=np.linalg.norm(b-a)
 if L<.34:continue
 cuts=[0.,1.]
 if min(a[1],b[1])<-16 and max(a[0],b[0])>=3.25 and min(a[0],b[0])<=10.8:
  for x in [3.25,10.8]:
   if abs(b[0]-a[0])>1e-8 and 0<(x-a[0])/(b[0]-a[0])<1:cuts.append((x-a[0])/(b[0]-a[0]))
 for u,v in zip(sorted(cuts)[:-1],sorted(cuts)[1:]):
  mid=a+(b-a)*(u+v)/2
  if r['node'].endswith('_0')and 3.249<mid[0]<10.801 and mid[1]<-16:continue
  edges.append({'a':a+(b-a)*u,'b':a+(b-a)*v,'za':r['za']+(r['zb']-r['za'])*u,'zb':r['za']+(r['zb']-r['za'])*v,'normal':np.array(r['normal']),'node':r['node']})

def key(p):return tuple(np.round(p,5))
adj={}
for i,e in enumerate(edges):
 for end in ['a','b']:adj.setdefault(key(e[end]),[]).append(i)
# Close only the small seam between the two adjoining outer-wall elements.
ends=[(p,ii[0])for p,ii in adj.items()if len(ii)==1]
for j,(p,i)in enumerate(ends):
 cand=[(np.linalg.norm(np.array(p)-q),q,k)for q,k in ends[j+1:]if edges[i]['node']!=edges[k]['node']]
 if not cand:continue
 dist,q,k=min(cand,key=lambda a:a[0])
 if dist<.45:
  za=edges[i]['za']if key(edges[i]['a'])==p else edges[i]['zb'];zb=edges[k]['za']if key(edges[k]['a'])==q else edges[k]['zb'];no=edges[i]['normal']+edges[k]['normal'];no/=np.linalg.norm(no)
  edges.append({'a':np.array(p),'b':np.array(q),'za':za,'zb':zb,'normal':no,'node':'CORNER_LINK'});n=len(edges)-1;adj[p].append(n);adj[q].append(n)

unused=set(range(len(edges)));routes=[]
while unused:
 starts=[p for p,ii in adj.items()if sum(i in unused for i in ii)==1];p=min(starts)if starts else key(edges[min(unused)]['a']);pts=[];zs=[];norm=[];node=[]
 while True:
  ids=[i for i in adj[p]if i in unused]
  if not ids:break
  i=ids[0];unused.remove(i);e=edges[i];forward=key(e['a'])==p;q=key(e['b']if forward else e['a']);z0,z1=(e['za'],e['zb'])if forward else(e['zb'],e['za'])
  if not pts:pts.append(np.array(p));zs.append(z0)
  pts.append(np.array(q));zs.append(z1);norm.append(e['normal']);node.append(e['node']);p=q
 if len(pts)>1:routes.append((np.array(pts),np.array(zs),np.array(norm),node))

meta=[];backs=[];cornices=[];frames=[]
for ri,(pts,zs,norm,nodes)in enumerate(routes):
 ds=np.linalg.norm(np.diff(pts,axis=0),axis=1);ss=np.r_[0,np.cumsum(ds)];L=ss[-1]
 if L<.35:continue
 miter=[]
 for i in range(len(pts)):
  n=norm[0]if i==0 else norm[-1]if i==len(pts)-1 else(norm[i-1]+norm[i])/max(.4,1+np.dot(norm[i-1],norm[i]));miter.append(n)
 miter=np.array(miter)
 def pos(s,d,z):
  i=min(len(ds)-1,max(0,int(np.searchsorted(ss,s,side='right')-1)));t=np.clip((s-ss[i])/ds[i],0,1);xy=pts[i]*(1-t)+pts[i+1]*t+(miter[i]*(1-t)+miter[i+1]*t)*d;crest=zs[i]*(1-t)+zs[i+1]*t;return [*xy,crest+z]
 stations=sorted(set(ss.tolist()+np.arange(0,L,.065).tolist()+[float(L)]))
 def sweep(profile):
  V=[pos(s,d,z)for s in stations for d,z in profile];F=[];N=len(profile)
  for i in range(len(stations)-1):
   for j in range(N):J=(j+1)%N;a=i*N+j;b=i*N+J;c=(i+1)*N+J;d=(i+1)*N+j;F.extend([[a,b,c],[a,c,d]])
  # Fan caps (all supplied sections are convex).
  for j in range(1,N-1):F.append([0,j+1,j]);off=(len(stations)-1)*N;F.append([off,off+j,off+j+1])
  return solid(V,F)
 backs.append(sweep([(-.008,-.495),(.037,-.495),(.037,-.140),(-.008,-.140)]))
 for z0,z1,d in [(-.535,-.501,.035),(-.500,-.478,.050),(-.145,-.109,.047),(-.109,-.072,.062),(-.072,-.027,.079),(-.027,.014,.095)]:cornices.append(sweep([(-.008,z0),(d,z0),(d,z1),(-.008,z1)]))
 def stepped(a,b,z0,z1,c=.030):return[(a+c,z0),(b-c,z0),(b-c,z0+c),(b,z0+c),(b,z1-c),(b-c,z1-c),(b-c,z1),(a+c,z1),(a+c,z1-c),(a,z1-c),(a,z0+c),(a+c,z0+c)]
 def ring(a,b,z0,z1,w,depth):
  oo=stepped(a,b,z0,z1);ii=stepped(a+w,b-w,z0+w,z1-w);A=[];B=[]
  for p,q,c,d in zip(oo,oo[1:]+oo[:1],ii,ii[1:]+ii[:1]):
   k=max(1,math.ceil(abs(q[0]-p[0])/.065))
   for j in range(k):t=j/k;A.append(np.array(p)*(1-t)+np.array(q)*t);B.append(np.array(c)*(1-t)+np.array(d)*t)
  N=len(A);V=[pos(s,dep,z)for rr,dep in[(A,.031),(B,.031),(A,depth),(B,depth)]for s,z in rr];F=[]
  for j in range(N):
   J=(j+1)%N
   for f in [(j,J,N+J,N+j),(2*N+j,3*N+j,3*N+J,2*N+J),(j,2*N+j,2*N+J,J),(N+j,N+J,3*N+J,3*N+j)]:F.extend([[f[0],f[1],f[2]],[f[0],f[2],f[3]]])
  return solid(V,F)
 spans=[];s=.085;i=0
 while s<L-.16:
  width=1.50 if i%2==0 else .34;b=min(s+width,L-.085)
  if b-s<.18:break
  frames.append(ring(s,b,-.462,-.173,.014,.055));frames.append(ring(s+.027,b-.027,-.435,-.200,.006,.048));spans.append([float(s),float(b)]);s=b+.060;i+=1
 meta.append({'route':ri,'length_m':float(L),'points_xy':pts.tolist(),'crest_z':zs.tolist(),'outward_normals':norm.tolist(),'panel_spans_m':spans,'panels':len(spans),'retained_special_screenwall':True})

put('V24_21_Exterior_Continuous_White_Frieze',union(backs),'M_V24_21_Exterior_Aged_Lime',True)
put('V24_21_Exterior_Stepped_Cornices',compose(cornices)if 'compose'in globals()else mf.Manifold.compose(cornices),'M_V24_21_Exterior_Gray_Trim',True)
put('V24_21_Exterior_Long_Short_Stepped_Frames',mf.Manifold.compose(frames),'M_V24_21_Exterior_Gray_Trim',True)
OUT['proof']={'reference':'屏幕截图 2026-10-19 025022.jpg','exterior_routes':meta,'panels':sum(r['panels']for r in meta),'band_height_m':.355,'actual_relief_depth_m':.055,'backing_contact_depth_m':.008,'old_architecture_and_ceramic_coping_retained':True,'image_not_edited':True,'dimension_status':'Photo fitted detail on the retained wall route, not a new field survey.'}
write();print('V21_FRIEZE',len(meta),'routes',OUT['proof']['panels'],'panels',flush=True)
