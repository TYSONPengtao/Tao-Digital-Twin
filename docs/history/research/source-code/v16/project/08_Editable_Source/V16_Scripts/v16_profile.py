import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','libs','geomlibs']]
import numpy as np
from PIL import Image,ImageDraw
B=Path(r'E:/jz/JIA/Rebuild_V15');I=json.loads((B/'02_Data/Native_Readback_Index_V15.json').read_text(encoding='utf8'))
tt=[]
for r in I:
 if not r['name'].startswith('SITE_V14_ORIGINAL_EXTERIOR'):continue
 d=np.load(B/'02_Data'/r['file']);t=d['vertices'][d['faces']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);good=abs(no[:,2])>.7*np.linalg.norm(no,axis=1);tt.extend(t[good])
t=np.array(tt);lo=t[:,:,:2].min(1);hi=t[:,:,:2].max(1)
def query(p,prior):
 ix=np.where(np.all(lo<=p+1e-8,axis=1)&np.all(hi>=p-1e-8,axis=1))[0]
 if not len(ix):return None
 q=t[ix];A=q[:,0,:2];u=q[:,1,:2]-A;v=q[:,2,:2]-A;w=np.array(p)-A;den=u[:,0]*v[:,1]-u[:,1]*v[:,0];aa=(w[:,0]*v[:,1]-w[:,1]*v[:,0])/den;bb=(u[:,0]*w[:,1]-u[:,1]*w[:,0])/den;z=q[:,0,2]+aa*(q[:,1,2]-q[:,0,2])+bb*(q[:,2,2]-q[:,0,2]);good=(aa>=-1e-6)&(bb>=-1e-6)&(aa+bb<=1+1e-6)&(z>prior-2)&(z<prior+1.5);z=z[good]
 return None if not len(z) else float(z[np.argmin(abs(z-(prior+.02)))])
result=[]
for c in [0,1]:
 p=np.array(json.loads((W/'v16'/f'SITE_PERIMETER_JOINED_RETAINING_WALL_{c}_centerline.json').read_text(encoding='utf8')));u=np.diff(p[:,:2],axis=0);u/=np.linalg.norm(u,axis=1)[:,None];nn=np.c_[-u[:,1],u[:,0]];offs=[]
 for j in range(len(p)):
  n=nn[0] if j==0 else nn[-1] if j==len(p)-1 else (nn[j-1]+nn[j])/2
  if 0<j<len(p)-1:n/=np.dot(n,nn[j])
  offs.append(n)
 offs=np.array(offs);pr=[]
 for j,(pt,n) in enumerate(zip(p,offs)):
  zz=[query(pt[:2]+n*d,pt[2]) for d in [.55,.8,1.05,1.35,1.65]]
  road=float(np.median([z for z in zz if z is not None])) if any(z is not None for z in zz) else None
  pr.append({'xy':pt[:2].tolist(),'base':float(pt[2]),'samples':zz,'road_z':road,'offset':n.tolist()})
 result.append({'chain':c,'profile':pr});valid=[r for r in pr if r['road_z'] is not None];print('PROFILE',c,'valid',len(valid),'of',len(pr),'roadminmax',min(r['road_z'] for r in valid),max(r['road_z'] for r in valid),'base-minus-road',np.quantile([r['base']-r['road_z'] for r in valid],[0,.5,1]).tolist());print('SAMPLES',json.dumps([pr[j] for j in np.linspace(0,len(pr)-1,7,dtype=int)]))
(W/'v16/Drain_Profiles.json').write_text(json.dumps(result,indent=2),encoding='utf8')
