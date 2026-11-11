import sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'libs'));sys.path.insert(0,str(Path(__file__).parent/'np1'))
import numpy as np
def find_peaks(h,distance=12,prominence=1):
 candidates=[i for i in range(1,len(h)-1) if h[i]>h[i-1] and h[i]>=h[i+1] and h[i]>prominence]
 kept=[]
 for i in sorted(candidates,key=lambda i:h[i],reverse=True):
  if all(abs(i-j)>=distance for j in kept):kept.append(i)
 return np.array(kept,dtype=int),{}
from PIL import Image,ImageDraw
out=Path(r'E:\jz\JIA\Rebuild');points=[];normals=[];areas=[]
for p in Path(r'E:\jz\JIA\Productions\Production_OBJ (2)\Data').rglob('*.obj'):
 v=[];f=[]
 for l in p.open():
  if l.startswith('v '):v.append([float(x) for x in l.split()[1:4]])
  elif l.startswith('f '):f.append([int(x.split('/')[0])-1 for x in l.split()[1:4]])
 v=np.array(v);f=np.array(f);t=v[f];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);a=np.linalg.norm(n,axis=1);n/=a[:,None]+1e-30;points.append(t.mean(1));normals.append(n);areas.append(a/2)
p=np.concatenate(points);n=np.concatenate(normals);a=np.concatenate(areas)
np.savez_compressed(out/'05_Intermediate/Reality_Geometry.npz',points=p,normals=n,areas=a)
roi=(p[:,0]>-10)&(p[:,0]<12)&(p[:,1]>-6)&(p[:,1]<12);q=p[roi];nn=n[roi];aa=a[roi]
print('ROI Z quantiles',np.quantile(q[:,2],[0,.01,.1,.5,.8,.9,.95,.99,1]),flush=True)
vertical=(abs(nn[:,2])<.2)&(q[:,2]>1307)
angles=np.mod(np.arctan2(nn[vertical,1],nn[vertical,0])*180/np.pi,90)
hist,bins=np.histogram(angles,bins=np.arange(0,90,.1),weights=aa[vertical]);theta=(bins[hist.argmax()]+.05)*np.pi/180
R=np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]]);local=q[:,:2]@R
print('DOMINANT AXIS deg',theta*180/np.pi,flush=True)
for i in [0,1]:
 coords=local[vertical,i]; h,b=np.histogram(coords,bins=np.arange(-15,18,.025),weights=aa[vertical]); peaks=find_peaks(h,distance=12,prominence=1)[0];order=peaks[np.argsort(h[peaks])[::-1]];print('wall modes',i,[(round(b[j]+.0125,3),round(h[j],2)) for j in order[:14]],flush=True)
for z in np.arange(1304,1320,.25):
 ar=aa[(q[:,2]>=z)&(q[:,2]<z+.25)&(abs(nn[:,2])>.7)].sum()
 if ar>3:print('horizontal area',round(z,2),round(ar,2),flush=True)
np.savez_compressed(out/'05_Intermediate/Registration_ROI.npz',local=local,z=q[:,2],normals=nn,areas=aa)
