from pathlib import Path
import sys,json,heapq,math
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import numpy as np,shapely
from shapely.geometry import shape
D=W/'v24_34';p=np.load(D/'Roam_Ground_Grid.npz')['p'];ids={}
for i,q in enumerate(p):ids.setdefault((int(q[0]),int(q[1])),[]).append(i)
mask=shape(json.loads((D/'Existing_Coverage.geojson').read_text()));new=~shapely.contains_xy(mask,p[:,0],p[:,1])
def closest(q):
 d=np.linalg.norm(p[:,:2]-q,axis=1);cand=np.flatnonzero(d<d.min()+.01);return int(cand[np.argmin(p[cand,2])])
def route(start,end):
 s=closest(start);e=closest(end);queue=[(0,s)];dist={s:0};prev={};closed=set()
 while queue:
  _,u=heapq.heappop(queue)
  if u in closed:continue
  if u==e:break
  closed.add(u);x,y=map(int,p[u,:2])
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
   for v in ids.get((x+dx,y+dy),[]):
    dz=abs(p[u,2]-p[v,2]);dd=math.hypot(dx,dy)
    if dz>.65*dd:continue
    cost=dist[u]+dd+dz*2
    if cost<dist.get(v,1e20):dist[v]=cost;prev[v]=u;heapq.heappush(queue,(cost+np.linalg.norm(p[v,:2]-p[e,:2]),v))
 if e not in dist:return None
 v=e;path=[v]
 while v!=s:v=prev[v];path.append(v)
 path=path[::-1];return {'points':p[path].tolist(),'new_points':int(new[path].sum()),'existing_points':int((~new[path]).sum()),'length_xy_m':sum(np.linalg.norm(p[b,:2]-p[a,:2])for a,b in zip(path,path[1:]))}
routes=[];failed=[]
for name,waypoints in [('Existing_West_Road',[(-25,9),(-24,-7),(-10,-20)]),('Existing_East_Road',[(10,-20),(26,-19),(45,-25)]),('Lower_Road_Across_MB7_Seam',[(45,-25),(27,-29),(5,-34),(-10,-39),(-28,-46),(-44,-47),(-55,-43)]),('Added_Southern_Field',[(27,-59),(31,-68)])]:
 ps=[];nr=0;er=0;L=0
 for a,b in zip(waypoints,waypoints[1:]):
  r=route(a,b)
  if r is None:failed.append((name,a,b,p[closest(a)].tolist(),p[closest(b)].tolist()));continue
  ps+=r['points']if not ps else r['points'][1:];nr+=r['new_points'];er+=r['existing_points'];L+=r['length_xy_m']
 routes.append({'name':name,'points':ps,'new_points':nr,'existing_points':er,'length_xy_m':L})
(D/'Planned_Routes.json').write_text(json.dumps(routes,indent=2));print([(r['name'],len(r['points']),r['length_xy_m'],r['new_points'])for r in routes]);print('FAILED',failed)
assert not failed,failed
