from pathlib import Path
import bpy,types,json,math,heapq,time,numpy as np
from mathutils import Vector
W=Path(__file__).parent;D=W/'v24_36';O=Path('E:/jz/JIA/Rebuild_V24_36');P=O/'Blender/Architecture_Complete_V24_36.blend';bpy.ops.wm.open_mainfile(filepath=str(P));m=types.ModuleType('physics');exec(bpy.data.texts['V24_21_碰撞控制.py'].as_string(),m.__dict__);a=np.load(D/'Final_Collision.npz');world=m.World(a['v'].tolist(),a['f'].tolist());p=np.load(D/'Roam_Ground_Grid.npz')['p'];ids={};valid={};tests=0;start=time.perf_counter()
for i,q in enumerate(p):ids.setdefault((int(q[0]),int(q[1])),[]).append(i)
def closest(q):
 d=np.linalg.norm(p[:,:2]-q,axis=1);cand=np.flatnonzero(d<d.min()+.01);return int(cand[np.argmin(p[cand,2])])
def edge(u,v):
 global tests
 if (u,v)in valid:return valid[u,v]
 w=m.Walker(world,p[u]);d=Vector(p[v]-p[u]);d.z=0;steps=math.ceil(d.length/.09);d/=steps;yes=True
 if not w.grounded or not world.clear(w.p):yes=False
 if yes:
  for _ in range(steps):
   if not w._horizontal(d):yes=False;break
 yes &=abs(w.p.z-p[v,2])<.35;valid[u,v]=yes;tests+=1;return yes
def route(start,end):
 s=closest(start);e=closest(end);queue=[(0,s)];dist={s:0};prev={};closed=set()
 while queue:
  _,u=heapq.heappop(queue)
  if u in closed:continue
  if u==e:break
  closed.add(u)
  if len(closed)>7000:return None
  x,y=map(int,p[u,:2])
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
   for v in ids.get((x+dx,y+dy),[]):
    dz=abs(p[u,2]-p[v,2]);dd=math.hypot(dx,dy)
    if dz>.65*dd:continue
    cost=dist[u]+dd+dz*2
    if cost<dist.get(v,1e20)and edge(u,v):dist[v]=cost;prev[v]=u;heapq.heappush(queue,(cost+np.linalg.norm(p[v,:2]-p[e,:2]),v))
 if e not in dist:return None
 v=e;path=[v]
 while v!=s:v=prev[v];path.append(v)
 path=path[::-1];return path
routes=[]
for name,waypoints in [('PTJIA6_North_Road', [(-25, 12), (-45, 15), (-58, 18), (-67, 24), (-77, 40), (-83, 65), (-84, 80), (-80, 100), (-84, 120), (-88, 135), (-100, 144), (-110, 146)]), ('PTJIA6_Central_Field', [(-390, 5), (-405, 12), (-420, 0)]), ('PTJIA6_Far_West_Field', [(-615, -150), (-600, -145), (-590, -160)])]:
 path=[]
 for a,b in zip(waypoints,waypoints[1:]):
  got=route(a,b)
  if got is None:raise RuntimeError(('No supported human path',name,a,b,tests))
  path+=got if not path else got[1:]
 points=p[path];L=float(np.linalg.norm(np.diff(points[:,:2],axis=0),axis=1).sum());routes.append({'name':name,'points':points.tolist(),'length_xy_m':L,'route_validation':'swept human capsule on every graph edge, not just height samples'});print('ROUTE_PLANNED',name,len(points),round(L,2),'edge_tests',tests,'seconds',time.perf_counter()-start,flush=True)
(D/'Planned_Routes.json').write_text(json.dumps(routes,indent=2));print('ACTUAL_ROUTES_DONE',time.perf_counter()-start,flush=True)
