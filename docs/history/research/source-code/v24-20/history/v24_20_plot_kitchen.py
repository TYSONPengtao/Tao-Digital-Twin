import json,numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).parent/'v24_20';a=json.loads((D/'Layout_Data.json').read_text());fig,ax=plt.subplots(figsize=(8,11))
for key,color,alpha in [('SITE_KITCHEN_STONE_FLOOR_Geometry','#bfd5db',.6),('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','#555',.6),('old_post_footprints','#a65526',1)]:
 for q in a[key]:
  p=np.array(q);ax.fill(p[:,0],p[:,1],color=color,alpha=alpha)
  if 'FLOOR'in key:
   for x,y in p:ax.text(x,y,f'{x:.2f},{y:.2f}',fontsize=7)
ax.set(xlim=(7.8,14.8),ylim=(-12.5,-1.8),aspect='equal',xlabel='X / m',ylabel='Y / m',title='Kitchen floor, masonry and original post feet');ax.grid(alpha=.2);fig.tight_layout();fig.savefig(D/'Kitchen_Before_Plan.png',dpi=150)
