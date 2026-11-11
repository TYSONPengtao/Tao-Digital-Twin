import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,manifold3d as mf
from v24_16_common import solid,cube,union
D=W/'v24_32';I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};cache={}
def src(n):
 if n not in cache:cache[n]=np.load(D/I[n]['file'])
 return cache[n]
def along(axis,q,terms):
 out=[];dims=[i for i in range(3)if i!=axis]
 for n,r in I.items():
  if not any(n.startswith(k)for k in terms):continue
  a=src(n);t=a['v'][a['f']];xy=t[:,:,dims];A=xy[:,1]-xy[:,0];B=xy[:,2]-xy[:,0];Q=np.asarray(q)-xy[:,0];det=A[:,0]*B[:,1]-A[:,1]*B[:,0];ok=abs(det)>1e-10;u=np.divide(Q[:,0]*B[:,1]-Q[:,1]*B[:,0],det,out=np.zeros_like(det),where=ok);w=np.divide(A[:,0]*Q[:,1]-A[:,1]*Q[:,0],det,out=np.zeros_like(det),where=ok);ok&=(u>=-1e-6)&(w>=-1e-6)&(u+w<=1.000001)
  x=t[:,0,axis]+u*(t[:,1,axis]-t[:,0,axis])+w*(t[:,2,axis]-t[:,0,axis]);vals=sorted(set(np.round(x[ok],6)))
  if vals:out.append((n,vals))
 return out
terms=['FACADE','PARTITIONS','HOUSE_V21_','HOUSE_V22_','KZ_','BEAM_','SLAB_','FLOOR_FASCIA','V24_31_F']
for q in [(8.55,0.),(7.6,0.),(8.55,.7),(7.6,.7),(8.55,1.2),(8.55,2.5),(7.6,3.3),(8.55,3.3),(8.55,4.5),(7.6,4.5)]:
 print('SIDE SECTION YZ',q,[(n,x)for n,x in along(0,q,terms)if min(x)<.4 or max(x)>12.6])
for q in [(6.0,1.),(6.,3.15),(6.,3.35),(6.,3.7),(6.,5.),(6.,6.85),(6.,7.1)]:print('STAIR FRONT/REAR XZ',q,along(1,q,terms))
for q in [(10.9,3.30),(10.9,3.45),(10.9,3.50),(10.9,4.0)]:print('BAY JOINT XZ',q,along(1,q,terms))
# Floor plans with actual section contours. Polygon JSON is drawn separately.
plans=[]
for fl,z in [(1,.65),(2,4.55),(3,8.15)]:
 for n in I:
  if (n.startswith(('PARTITIONS','FACADE','KZ_'))and f'_F{fl}_'in n)or n.startswith('STAIR_LANDING')or n.startswith(f'SLAB_JOINED_F{fl}_')or ('DOOR_'in n and f'_F{fl}'in n):
   try:
    a=src(n);m=solid(a['v'],a['f'],n);ps=m.slice(z).to_polygons();plans.append({'floor':fl,'name':n,'polygons':[p.tolist()for p in ps]})
   except Exception as e:print('PLAN_SKIP',n,str(e)[:100])
(D/'Section_Plans.json').write_text(json.dumps(plans),encoding='utf8')
