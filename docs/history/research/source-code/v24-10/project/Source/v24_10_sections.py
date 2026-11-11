import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs'),str(W/'geomlibs'),str(W/'v8_interior/plotlibs')]
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
D=W/'v24_10';d=np.load(D/'AsBuilt_All_LOCAL.npz');v=d['v'];f=d['f'];t=v[f];lo=t.min(1);hi=t.max(1)
mask=(hi[:,0]>10)&(lo[:,0]<23)&(hi[:,1]>-19)&(lo[:,1]<-7)&(hi[:,2]>-4)&(lo[:,2]<6);t=t[mask]
def section(t,z):
 q=[]
 for k in range(3):
  a=t[:,k];b=t[:,(k+1)%3];ok=(a[:,2]<=z)&(b[:,2]>z)|(a[:,2]>z)&(b[:,2]<=z)
  ids=np.where(ok)[0];p=a[ok]+(b[ok]-a[ok])*((z-a[ok,2])/(b[ok,2]-a[ok,2]))[:,None];q.extend(zip(ids,p[:,:2]))
 by={}
 for i,p in q:by.setdefault(int(i),[]).append(p)
 return np.array([pp for pp in by.values()if len(pp)==2])
fig,axs=plt.subplots(2,3,figsize=(18,12));zs=[-2.,-.8,0.5,1.8,2.6,3.5];out={}
for ax,z in zip(axs.ravel(),zs):
 s=section(t,z);out[str(z)]=s.tolist();ax.add_collection(LineCollection(s,colors='#171717',linewidths=.8))
 for n,col in [('BASE_SITE_V14_INNER_STORAGE_FLOOR_Geometry.npz','#d13822'),('BASE_SITE_V14_OUTER_STORAGE_FLOOR_Geometry.npz','#df8b13')]:
  d0=np.load(D/n);xy=d0['v'][:,:2];ax.scatter(xy[:,0],xy[:,1],s=10,c=col)
 ax.set(xlim=(10,23),ylim=(-19,-7),aspect='equal',title=f'Original 3dm horizontal section Z={z:.2f}m',xticks=np.arange(10,24),yticks=np.arange(-19,-6));ax.grid(alpha=.22);ax.set_xlabel('LOCAL X (m)');ax.set_ylabel('LOCAL Y (m)')
fig.tight_layout();fig.savefig(D/'AsBuilt_Sections.png',dpi=140)
(D/'AsBuilt_Section_Segments.json').write_text(json.dumps(out),encoding='utf8');print('SECTIONS',[(z,len(out[str(z)]))for z in zs])
