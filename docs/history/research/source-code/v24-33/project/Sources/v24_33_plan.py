import json,numpy as np
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
W=Path(__file__).parent;D=W/'v24_33';ix=json.loads((D/'Geometry_Index.json').read_text('utf8'));fig,ax=plt.subplots(figsize=(16,18));names=[]
terms=['MASONRY','PERIMETER_JOINED','INSIDE_FINISH','STONE_GUARD','FACADE_CONTINUOUS_F1','COURTYARD_WEST_TILE_WALL_Geometry','White_Courtyard','SITE_V20_STORAGE_PHOTO']
for row in ix:
 n=row['name']
 if not any(t in n for t in terms):continue
 a=np.load(D/row['file']);t=a['v'][a['f']];ok=(t[:,:,2].min(1)<1.0)&(t[:,:,2].max(1)>1.0);t=t[ok];segs=[]
 for tr in t:
  q=[]
  for pa,pb in zip(tr,np.roll(tr,-1,axis=0)):
   if (pa[2]-1)*(pb[2]-1)<0:q.append((pa+(pb-pa)*(1-pa[2])/(pb[2]-pa[2]))[:2])
  if len(q)==2:segs.append(q)
 color='red' if 'GUARD' in n else 'orange' if 'White_Courtyard' in n else 'gray' if 'INSIDE' in n else None
 lc=LineCollection(segs,colors=color,linewidths=1.5,label=n);ax.add_collection(lc);names.append(n)
for x in range(-1,23):
 for y in range(-18,13):ax.text(x+.03,y+.04,f'{x},{y}',fontsize=6,color='#888888')
ax.set(xlim=(-1,22),ylim=(-18,12),aspect='equal');ax.set_xticks(np.arange(-1,23));ax.set_yticks(np.arange(-18,13));ax.grid(alpha=.3);ax.legend(loc='upper left',fontsize=7);fig.tight_layout();fig.savefig(D/'Wall_Plan_Z1.png',dpi=120)
