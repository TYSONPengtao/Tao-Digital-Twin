from pathlib import Path
import json,numpy as np
D=Path(__file__).parent/'v24_20'
INDEX={r['name']:r for r in json.loads((D/'Inventory.json').read_text())}
def source(n):return np.load(D/INDEX[n]['file'])
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from shapely.geometry import Polygon
fig,ax=plt.subplots(figsize=(14,9));rows=[]
for n,r in INDEX.items():
 if not r.get('file')or not any(k in n for k in ['PARTITION','FACADE_CONTINUOUS_F1','HOUSE_V20_F1','DOOR_BATH_F1','DOOR_KITCHEN_F1','STAIR_F1','STAIR_LANDING_F1']):continue
 d=source(n);v=d['v'];f=d['f'];z=1.
 if v[:,2].min()>z or v[:,2].max()<z:continue
 seg=[]
 for t in v[f]:
  pp=[]
  for a,b in zip(t,np.roll(t,-1,axis=0)):
   if(a[2]-z)*(b[2]-z)<0:pp.append(a+(b-a)*(z-a[2])/(b[2]-a[2]))
  if len(pp)==2:seg.append(np.array(pp)[:,:2])
 col='#b22920'if n.startswith('DOOR')else'#98a2b0'if n.startswith('STAIR')else'#222'
 ax.add_collection(LineCollection(seg,colors=col,linewidths=2 if n.startswith('DOOR') else 1.2))
 if n.startswith('DOOR')and'FRAME'in n:
  p=(v.min(0)+v.max(0))/2;ax.annotate(n.replace('DOOR_','').replace('__FRAME_Geometry',''),p[:2],xytext=(12,12),textcoords='offset points',fontsize=9,color=col);rows.append({'name':n,'center':p.tolist()})
ax.set(xlim=(-.5,13.6),ylim=(6.5,10.4),aspect='equal',xlabel='X / m',ylabel='Y / m',title='V24.19 native ground-floor rear room / stair plan at Z=1.0m');ax.grid(alpha=.2);fig.tight_layout();fig.savefig(D/'F1_Before_Plan.png',dpi=150);(D/'F1_Door_Positions.json').write_text(json.dumps(rows,indent=2));print('PLAN_SAVED',flush=True)
