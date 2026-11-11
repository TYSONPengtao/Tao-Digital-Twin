import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,manifold3d as mf
D=W/'v24_12';d=np.load(D/'SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry.npz')
def probe(v,f,label):
 v,ix=np.unique(np.round(v,6),axis=0,return_inverse=True);f=ix[f];tt=v[f];f=f[np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)>1e-13];m=mf.Manifold(mf.Mesh64(np.ascontiguousarray(v),np.array(f,dtype=np.uint64,order='C')))
 ed=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);ee,cnt=np.unique(ed,axis=0,return_counts=True);bad=ee[cnt!=2]
 print(label,m.status(),m.volume(),'boundary',int((cnt==1).sum()),'non2',int((cnt!=2).sum()));print('BAD',v[bad].tolist()if len(bad)<40 else len(bad))
 return m
for i in range(3):probe(d['v'],d['f'][d['mi']==i],str(i))
probe(d['v'],d['f'],'whole')
v,ix=np.unique(np.round(d['v'],6),axis=0,return_inverse=True);f=ix[d['f']];sf=np.sort(f,axis=1);u,inv,cnt=np.unique(sf,axis=0,return_inverse=True,return_counts=True);print('repeated triangles',np.unique(cnt,return_counts=True));f=f[cnt[inv]==1];probe(v,f,'no internal paired triangles')
