import sys
from pathlib import Path
W=Path(r'C:\Users\PENG\Documents\Codex\2026-10-07\files-pasted-by-the-user-rhino\work');sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W/'v6_reality_inventory')]
import numpy as np
from scipy.spatial import cKDTree
from nearest_photo_projection import closest_on_triangles
D=W/'v8_terrain_clear/contact_gap';s=np.load(D/'Ground_Support_And_Donor_Indices.npz');t=s['base3_support_triangles'];q=np.array([[13.703621795620965,-4.78538482786986]]);b=t.copy();b[:,:,2]=0;tree=cKDTree(t[:,:,:2].mean(1));_,ids=tree.query(q,k=32);ids=ids.ravel();qq=np.repeat(np.c_[q,[0]],32,axis=0);_,ww,dd=closest_on_triangles(qq,b[ids]);zz=(ww*t[ids,:,2]).sum(1)
for i in np.argsort(dd)[:10]:print(dd[i],zz[i],ids[i],t[ids[i]])
