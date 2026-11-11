from pathlib import Path
import sys,json,hashlib
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
from v24_16_common import solid,cube
D=Path(__file__).parent
I={r['name']:r for r in json.loads((W/'v26_1/Geometry_Index.json').read_text('utf8'))}
J={r['name']:r for r in json.loads((W/'v26_7/Final/Geometry_Index.json').read_text('utf8'))}
aa=np.load(W/'v26_7/Final'/J['V26_3_House_Connected_Walls_And_Stairs']['file']); house=solid(aa['v'],aa['f'],'current house')
out={'current_sha256':'ae36eb7abde8241465d4d6707fa19c8a9ccd74aaebc025565f2843ee9be5711e','flights':[],'rays':[],'cutsections':[]}
def tops(a):
 t=a['v'][a['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(no,axis=1)/2; normal=no/np.maximum(2*area[:,None],1e-20);sel=(normal[:,2]>.999)&(area>1e-7)
 vals={}
 for i in np.flatnonzero(sel):
  k=round(float(t[i,:,2].mean()),5)
  if k not in vals: vals[k]={'z':k,'lo':t[i].min(0),'hi':t[i].max(0),'area':0}
  q=vals[k];q['lo']=np.minimum(q['lo'],t[i].min(0));q['hi']=np.maximum(q['hi'],t[i].max(0));q['area']+=area[i]
 return [{'z':k,'lo':q['lo'].tolist(),'hi':q['hi'].tolist(),'area':float(q['area'])} for k,q in sorted(vals.items())]
for n,r in I.items():
 if not n.startswith(('STAIR_F','STAIR_LANDING')):continue
 a=np.load(W/'v26_1'/r['file']);m=solid(a['v'],a['f'],n);q={'name':n,'bounds':[a['v'].min(0).tolist(),a['v'].max(0).tolist()],'upfaces':tops(a)};out['flights'].append(q)
 print(n)
 for t in q['upfaces']:print('  ',t)
for x in [4.2,5.1,5.25,5.6,6.3,7.4,7.85,8.2]:
 for y in [7.42,7.43,7.48,7.5,7.52,7.55,7.8,8.23,8.3,8.4,8.48,8.5,8.52,8.54,8.55,8.56,8.58,8.6,8.62,8.65,8.7,8.8,9.2,9.5,9.57,9.6,9.65,9.67,9.68]:
  hits=house.ray_cast([x,y,7.20],[x,y,-.46]);z=[{'z':float(h.position[2]),'normal':list(h.normal)}for h in hits]
  out['rays'].append({'x':x,'y':y,'hits':z})
for x in [5.6,6.3,7.4]:
 # A 2 mm thin solid section, preserved source world geometry.
 sec=house^cube([x-.001,7.42,-.5],[x+.001,9.68,7.20]);a=sec.to_mesh64();out['cutsections'].append({'x':x,'vertices':a.vert_properties[:,:3].tolist(),'faces':a.tri_verts.tolist(),'volume_m3':sec.volume()})
(D/'Stair_Rootcause_Raw.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
print('DONE',len(out['rays']))
