import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W/'v8_interior/plotlibs')]
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
D=W/'v24_16';rows=json.loads((D/'Inventory.json').read_text());idx={r['name']:r for r in rows}
def data(n):return np.load(D/idx[n]['file'])
def section(d,axis,val,viewaxes,lo,hi):
 v=d['v'];t=v[d['f']];q=t[:,:,axis]-val;sel=(q.min(1)<-1e-7)&(q.max(1)>1e-7);t=t[sel];q=q[sel];out=[]
 for tri,dist in zip(t,q):
  p=[]
  for a,b in [(0,1),(1,2),(2,0)]:
   if dist[a]*dist[b]<0:p.append(tri[a]+(tri[b]-tri[a])*(-dist[a]/(dist[b]-dist[a])))
  if len(p)==2:
   p=np.array(p)[:,viewaxes]
   if np.all(p.max(0)>=lo)and np.all(p.min(0)<=hi):out.append(p)
 return np.array(out)
wall='SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry';roof='SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL_Geometry';corn='SITE_SOUTH_SCREENWALL_V12_STEPPED_MASONRY_UNDEREAVE_Geometry'
fig,axs=plt.subplots(1,3,figsize=(15,7));cross=[]
for ax,x in zip(axs,[3.5,7.,10.5]):
 for n,color in [(wall,'black'),('V24_11_Screenwall_Continuous_Stepped_Stone_Plinth','brown'),(roof,'red'),(corn,'blue'),('V24_09_Screenwall_Curved_Panel_Backings','orange')]:
  seg=section(data(n),0,x,[1,2],[-18,-1],[-15,6]);ax.add_collection(LineCollection(seg,colors=color,linewidths=1))
 ax.set(xlim=(-17.9,-15.8),ylim=(-.85,5.3),title=f'Screen X={x}',xlabel='Y',ylabel='Z');ax.set_aspect('equal');ax.grid()
 for z in [0,1,2,2.8,3.1,3.3]:
  s=section(data(wall),2,z,[0,1],[x-.001,-18],[x+.001,-15]);ys=[]
  for p in s:
   if p[:,0].min()<=x<=p[:,0].max()and abs(p[1,0]-p[0,0])>1e-9:ys.append(float(p[0,1]+(p[1,1]-p[0,1])*(x-p[0,0])/(p[1,0]-p[0,0])))
  cross.append({'x':x,'z':z,'wall_y_values':sorted(ys)})
fig.tight_layout();fig.savefig(D/'Screen_Crosssections_Before.png',dpi=150);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(14,10))
for ax,z in zip(axs,[1.0,2.60]):
 for n,color in [('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','black'),('SITE_V20_STORAGE_PHOTO_INTERIOR_LIMEWASH_Geometry','blue'),('SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry','brown'),('V24_11_Storage_Veranda_Column_1','red'),('V24_11_Storage_Veranda_Column_2','red'),('SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD_Geometry','gray'),('V24_14_Storage_West_Sealed_Gable','green')]:
  seg=section(data(n),2,z,[0,1],[12,-17.3],[19.2,-13]);ax.add_collection(LineCollection(seg,colors=color,linewidths=1.4))
 ax.plot([13.535,18.405],[-16.48,-16.48],'g--',label='roof eave');ax.set(xlim=(12.4,19),ylim=(-17.2,-13.5),title=f'Storage plan Z={z}',xlabel='X',ylabel='Y');ax.set_aspect('equal');ax.grid()
fig.tight_layout();fig.savefig(D/'Storage_Entry_Plan_Before.png',dpi=150);plt.close(fig)
(D/'Measured_Wall_Sections.json').write_text(json.dumps(cross,indent=2));print(json.dumps(cross,indent=2))
