exec(open('work/v21_house/inspect_house.py',encoding='utf-8-sig').read().split('for r in I:')[0])
for n in ['FACADE_CONTINUOUS_F3','PARTITIONS_JOINED_F3']:
 d=np.load(B/'02_Data'/next(r['file'] for r in I if r['name']==n));v=d['vertices'];f=d['faces'];t=v[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ll=np.linalg.norm(no,axis=1);cc=t.mean(1)
 for a,sg in [(1,1),(0,1),(0,-1)]:
  good=(no[:,a]*sg>ll*.995);vv=cc[good,a];aa=ll[good]/2;di={}
  for plane,area in zip(np.round(vv,4),aa):di[float(plane)]=di.get(float(plane),0)+float(area)
  print(n,a,sg,sorted(di.items(),key=lambda x:-x[1])[:12])
