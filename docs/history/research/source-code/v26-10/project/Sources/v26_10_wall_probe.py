from v26_2_common import *
from shapely.geometry import LineString,box
D=W/'v26_10';D.mkdir(exist_ok=True);FD=W/'v26_9/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};r=J['V26_3_House_Connected_Walls_And_Stairs'];a=np.load(FD/r['file']);house=solid(a['v'],a['f']);out=[]
for fl,z in [(1,.8),(2,4.7),(3,8.3)]:
 loops=house.slice(z).to_polygons()
 for cx in [0.,2.2,3.9,9.1,10.8,13.]:
  roi=box(cx-.65,6.65,cx+.65,7.95);segments=[]
  for loop in loops:
   line=LineString(np.vstack([loop,loop[0]]));q=line.intersection(roi)
   for g in (q.geoms if hasattr(q,'geoms')else[q]):
    if g.is_empty:continue
    segments.append(np.array(g.coords).tolist())
  probes=[]
  for y in [6.7,7.02,7.12,7.18,7.22,7.28,7.38,7.48,7.58]:
   h=house.ray_cast([cx-.45,y,z],[cx+.45,y,z]);probes.append({'axis':'X','y':y,'hits':[(q.position[0],q.normal[0])for q in h]})
  for x in [cx-.45,cx-.32,cx-.24,cx-.18,cx-.12,cx+.12,cx+.18,cx+.24,cx+.32,cx+.45]:
   h=house.ray_cast([x,6.8,z],[x,7.8,z]);probes.append({'axis':'Y','x':x,'hits':[(q.position[1],q.normal[1])for q in h]})
  out.append({'floor':fl,'z':z,'corner_x':cx,'segments':segments,'probes':probes})
(D/'Wall_Intersection_Sections_Before.json').write_text(json.dumps(out,indent=2),'utf8')
for r in out:
 if r['floor']==1 and r['corner_x']in[3.9,9.1,10.8]:print(json.dumps(r))
try:
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axs=plt.subplots(3,4,figsize=(16,11),layout='constrained')
 for ax,r in zip(axs.ravel(),[q for q in out if q['corner_x']in[0.,3.9,9.1,13.]]):
  for seg in r['segments']:
   p=np.array(seg);ax.plot(p[:,0],p[:,1],color='#334956',lw=2)
  ax.axvline(r['corner_x'],color='lightgray');ax.axhline(7.3,color='lightgray');ax.set_aspect('equal');ax.set_xlim(r['corner_x']-.65,r['corner_x']+.65);ax.set_ylim(6.65,7.95);ax.set_title(f"F{r['floor']} X{r['corner_x']}");ax.grid(alpha=.2)
 fig.savefig(D/'Wall_Sections_Before.png',dpi=135)
except ImportError as e:print('PLOT_UNAVAILABLE',str(e))
