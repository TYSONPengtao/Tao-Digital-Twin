from pathlib import Path
import sys,json,collections,itertools
W=Path(__file__).parent;sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree
D=Path(sys.argv[1])if len(sys.argv)>1 else W/'v26_1';I=json.loads((D/'Geometry_Index.json').read_text('utf8'));G=collections.defaultdict(list)
for row in I:
 a=np.load(D/row['file']);t=np.array(a['v'],np.float64)[a['f']];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(cross,axis=1)/2;no=cross/np.maximum(area[:,None]*2,1e-30);axis=np.argmax(abs(no),axis=1);ok=(area>1e-7)&(np.max(abs(no),axis=1)>.99999999)
 for ax in range(3):
  indices=np.where(ok&(axis==ax))[0];sub=collections.defaultdict(list);dim=[j for j in range(3)if j!=ax]
  for k in indices:sub[(round(float(t[k,:,ax].mean()),4),int(no[k,ax]>0))].append(k)
  for (plane,sign),ix in sub.items():
   polys=[Polygon(q[:,dim])for q in t[ix]];p=unary_union(polys)
   if p.area>1e-6:G[ax,plane].append({'name':row['name'],'sign':sign,'p':p,'axis':ax,'plane':plane,'materials':row['materials']})
rows=[]
for ax in range(3):
 planes=sorted(k[1]for k in G if k[0]==ax)
 for j,z in enumerate(planes):
  group=G[ax,z];near=list(group)
  for zz in planes[j+1:]:
   if zz-z>.00051:break
   near+=G[ax,zz]
  if len(near)<2:continue
  tree=STRtree([p['p']for p in near]);seen=set()
  for ia,aa in enumerate(group):
   for ib in tree.query(aa['p']):
    ib=int(ib)
    if ib<=ia:continue
    bb=near[ib]
    if aa['name']==bb['name']:continue
    p=aa['p'].intersection(bb['p']);area=p.area
    if area>1e-5:rows.append({'a':aa['name'],'b':bb['name'],'axis':ax,'plane':z,'separation_m':abs(z-bb['plane']),'same_normal':aa['sign']==bb['sign'],'area_m2':area,'bounds_2d':list(p.bounds),'materials_a':aa['materials'],'materials_b':bb['materials']})
rows.sort(key=lambda r:r['area_m2'],reverse=True);(D/'Coplanar_Audit.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
print('COPLANAR',len(rows),'SAME_NORMAL',sum(r['same_normal']for r in rows),flush=True)
for r in [r for r in rows if r['same_normal']][:65]:print(r['a'],r['b'],r['axis'],r['plane'],round(r['area_m2'],5),r['bounds_2d'],flush=True)
