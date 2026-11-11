from v26_2_common import *
from collections import defaultdict
a=np.load(W/'v26_7_column_audit/final_candidate/V26_3_House_Connected_Walls_And_Stairs.npz');v=a['v'];f=a['f'];t=v[f];groups=defaultdict(list)
for i,q in enumerate(t):groups[tuple(sorted(map(tuple,q)))].append(i)
for ids in groups.values():
 if len(ids)<2:continue
 print('DUP',ids)
 for i in ids:print(i,t[i].tolist(),np.cross(t[i,1]-t[i,0],t[i,2]-t[i,0]).tolist())
uv,rev=np.unique(v,axis=0,return_inverse=True);ff=rev[f];ed=np.sort(np.concatenate([ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]]),axis=1);ee,ct=np.unique(ed,axis=0,return_counts=True)
for e,n in zip(ee[ct!=2],ct[ct!=2]):print('BADGE',n,uv[e].tolist())
