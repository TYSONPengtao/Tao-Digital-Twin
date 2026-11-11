from v22_common import *
for n,r in I.items():
 if not any(w in n for w in ['COLUMN','CLASSIC','CAPITAL']):continue
 d=np.load(B/'02_Data'/r['file']);v=d['vertices'];a=v.min(0);b=v.max(0)
 if a[1]<.3 and b[1]<.6:print(n,np.round([a,b],4).tolist())
