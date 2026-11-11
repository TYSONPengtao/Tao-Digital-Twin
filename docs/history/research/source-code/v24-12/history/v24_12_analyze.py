import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'v8_interior/plotlibs'),str(W/'libs')]
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
D=W/'v24_12';names=json.loads((D/'Inventory.json').read_text(encoding='utf8'))
for r in names:print(r['name'],r['vertices'],np.round(r['bounds'],3).tolist())
fig,axs=plt.subplots(2,2,figsize=(16,12))
for n,c in [('SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry','#3256bb'),('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','#888888'),('SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','#b27a26'),('V24_10_Secondary_Screenwall_Closed_Panel_Band','#ff0000')]:
 d=np.load(D/(n+'.npz'));v=d['v'];f=d['f'];ed=np.unique(np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1),axis=0)
 for ax,(i,j)in zip(axs.flat,[(0,1),(0,2),(1,2),(0,2)]):
  ee=v[ed];mask=(ee[:,:,0].max(1)>10.79)&(ee[:,:,0].min(1)<19.1)&(ee[:,:,1].max(1)>-17.4)&(ee[:,:,1].min(1)<-8.4)
  if ax==axs[1,1]:mask &= (ee[:,:,0].min(1)<13.3)&(ee[:,:,1].max(1)<-16.2)
  if 'ROOF' in n and len(ed)>10000:mask &= np.arange(len(ed))%32==0
  ax.add_collection(LineCollection(ee[mask][:,:,[i,j]],colors=c,linewidths=.3));ax.autoscale();ax.set_aspect('equal');ax.grid(alpha=.3)
axs[0,0].set_title('XY');axs[0,1].set_title('XZ');axs[1,0].set_title('YZ');axs[1,1].set_title('Secondary XZ');fig.tight_layout();fig.savefig(D/'Geometry_Before.png',dpi=110)
d=np.load(D/'SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry.npz');v=d['v'];print('roof ridge slice')
for x in [12.8,13,13.3,14,15,16,17,18,18.7]:
 p=v[abs(v[:,0]-x)<.06];k=p[:,2].argmax();print(x,p[k].tolist(),'south',p[p[:,1].argmin()].tolist(),'north',p[p[:,1].argmax()].tolist())
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','V24_10_Secondary_Screenwall_Closed_Panel_Band','SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES_Geometry']:
 d=np.load(D/(n+'.npz'));v=d['v'];p=v[(v[:,0]>10.79)&(v[:,0]<13.35)&(v[:,1]<-16.2)&(v[:,1]>-17.4)];print(n);print(np.unique(np.round(p,4),axis=0).tolist() if 'WALL_0_'in n else '');
