import json
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
D=Path(__file__).parent/'v24_22'
data=json.loads((D/'Wall_Contours_Before.json').read_text())
for kind in ['sections','plans']:
 fig,axes=plt.subplots(2,3,figsize=(16,11)) if kind=='sections' else plt.subplots(1,3,figsize=(15,10))
 for ax,(level,items) in zip(axes.flat,data[kind].items()):
  for i,(name,polys) in enumerate(items.items()):
   for p in polys:
    p=np.array(p);p=np.r_[p,p[:1]];ax.plot(p[:,0],p[:,1],color=f'C{i}',label=str(i))
  if kind=='sections':ax.set(xlim=(7.2,14.5),ylim=(-.6,5.),title='Y='+level)
  else:ax.set(xlim=(7.5,14.5),ylim=(-12.2,-2.3),title='Z='+level)
  ax.set_aspect('equal');ax.grid(True)
 fig.savefig(D/('Wall_'+kind+'_Before.png'),dpi=130);plt.close(fig)
