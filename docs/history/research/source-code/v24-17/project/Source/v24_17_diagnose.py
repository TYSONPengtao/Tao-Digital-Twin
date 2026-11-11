import sys,json,collections
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
D=W/'v24_17';idx=json.loads((D/'Inventory.json').read_text());out=[];seen={};counts=collections.Counter()
for r in idx:
 if not r['file']:continue
 n=r['name']
 if not any(k in n.upper()for k in ['STORAGE','KITCHEN','SECONDARY']):continue
 a=np.load(D/r['file']);v=a['v'];f=a['f'];t=v[f];ar=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2
 for j in np.where(ar>1e-8)[0]:
  tri=np.round(t[j],5);tri=tri[np.lexsort((tri[:,2],tri[:,1],tri[:,0]))];key=tri.tobytes()
  if key in seen:counts[(seen[key][0],n)]+=1
  else:seen[key]=(n,j)
for pair,count in counts.most_common():out.append({'objects':pair,'exact_duplicate_triangles_at_10um':count})
(D/'Duplicate_Faces_Before.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
# Exact roof planes and closed-part bounds identify the marked junction bits.
for r in idx:
 n=r['name']
 if not r['file']or not any(k in n for k in ['KITCHEN_GABLE_ROOF','KITCHEN_ROOF','DIAGONAL_VALLEY','KITCHEN_CONNECTED','KITCHEN_TIMBER','KITCHEN_GABLE','KITCHEN_RIDGE']):continue
 a=np.load(D/r['file']);v=a['v'];f=a['f'];t=v[f];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(normal,axis=1)/2;normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-15);q=(normal[:,2]>.5)&(area>.1);parts=[]
 for ii in np.where(q)[0]:parts.append({'centroid':t[ii].mean(0).tolist(),'normal':normal[ii].tolist(),'area':float(area[ii]),'vertices':t[ii].tolist()})
 print('PLANES',n,parts[:12])
