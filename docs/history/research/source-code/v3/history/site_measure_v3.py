# Public archival copy: private site constants replaced by TAO_PRIVATE_SITE_* markers.
# Original SHA-256 and original line numbers are recorded in manifest.json.
raise RuntimeError("Restore private site constants from the local original before execution; see manifest.json")
import sys,math,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
from scipy.signal import find_peaks
a=np.load(r'E:\jz\JIA\Rebuild\05_Intermediate\Reality_Geometry.npz');p=a['points'];n=a['normals'];areas=a['areas'];theta=math.radians(19.65);r=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);p[:,:2]=(p[:,:2]-[-3.45191261,-3.90043098])@r;p[:,2]-=TAO_PRIVATE_SITE_002;n[:,:2]=n[:,:2]@r
for name,bounds in [('Kitchen',(5.5,-12,14,-1.6)),('Gate',(3.5,-13,9.7,-10.5)),('Screen',(2,-18,12,-15)),('SWGate',(-16,-14.5,-11,-7.5)),('TimberFront',(5,-11.4,9,-2.6))]:
 select=(p[:,0]>bounds[0])&(p[:,0]<bounds[2])&(p[:,1]>bounds[1])&(p[:,1]<bounds[3])&(p[:,2]>-.2)&(p[:,2]<2.8)
 q=p[select];nn=n[select];ar=areas[select];print(name)
 for axis in [0,1]:
  s=(abs(nn[:,axis])>.85)&(abs(nn[:,2])<.25);bins=np.arange(bounds[axis],bounds[axis+2]+.1,.04);h,bb=np.histogram(q[s,axis],bins=bins,weights=ar[s]);peaks=find_peaks(h,distance=5)[0];order=peaks[np.argsort(h[peaks])[::-1]][:10];print(axis,[(round(bb[j]+.02,2),round(h[j],2)) for j in order])
 print('z95',np.quantile(q[:,2],[.5,.9,.95,.99]).round(3).tolist())
for x in np.arange(3.9,9.2,.5):
 s=(abs(p[:,0]-x)<.22)&(abs(p[:,1])<.20)&(p[:,2]>2.2)&(p[:,2]<3.85)
 if s.sum()>10:print('ARCH',round(x,2),np.quantile(p[s,2],[.02,.1,.5,.9]).round(3).tolist())
