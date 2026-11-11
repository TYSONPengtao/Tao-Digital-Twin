import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
D=W/'v24_16';INDEX={r['name']:r for r in json.loads((D/'Inventory.json').read_text())};OUT={'objects':[],'proof':{}}
WOOD='M_V24_15_Traditional_Storage_Wood';WHITE='M_V24_11_Plain_White_Limewash';TRIM='M_V24_11_Screenwall_Crisp_Soffit_Stone';CERAMIC='M_V24_09_Screenwall_Ceramic_0'
def solid(v,f,n=''):
 v=np.asarray(v);f=np.asarray(f);m=mf.Manifold(mf.Mesh64(np.array(v,dtype=np.float64,order='C'),np.array(f,dtype=np.uint64,order='C')))
 if m.status()==mf.Error.NoError and m.volume()>0:return m
 # Construction helpers can supply mixed cap windings. Orient each closed
 # indexed component; do not weld or alter its topology or dimensions.
 edges={}
 for i,face in enumerate(f):
  for a,b in zip(face,np.roll(face,-1)):
   key=(int(min(a,b)),int(max(a,b)));edges.setdefault(key,[]).append((i,a<b))
 if all(len(e)==2 for e in edges.values()):
  adj=[[]for _ in f]
  for (a,sa),(b,sb)in edges.values():adj[a].append((b,sa==sb));adj[b].append((a,sa==sb))
  flip={};groups=[]
  for start in range(len(f)):
   if start in flip:continue
   flip[start]=False;stack=[start];part=[]
   while stack:
    a=stack.pop();part.append(a)
    for b,same in adj[a]:
     if b not in flip:flip[b]=flip[a]^same;stack.append(b)
   groups.append(part)
  ff=f.copy()
  for i,yes in flip.items():
   if yes:ff[i]=ff[i][::-1]
  for g in groups:
   t=v[ff[g]];vol=np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6
   if vol<0:ff[g]=ff[g][:,::-1]
  m=mf.Manifold(mf.Mesh64(np.array(v,dtype=np.float64,order='C'),np.array(ff,dtype=np.uint64,order='C')))
  if m.status()==mf.Error.NoError and m.volume()>0:return m
 for dec in [9,8,7,6,5]:
  vv,ix=np.unique(np.round(v,dec),axis=0,return_inverse=True);ff=ix[f];t=vv[ff];ok=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-13;ff=ff[ok];m=mf.Manifold(mf.Mesh64(np.array(vv,dtype=np.float64,order='C'),np.array(ff,dtype=np.uint64,order='C')))
  if m.status()==mf.Error.NoError and m.volume()>0:return m
 raise RuntimeError((n,m.status(),m.volume()))
def source(n):return np.load(D/INDEX[n]['file'])
def load(n):
 a=source(n);return solid(a['v'],a['f'],n)
def cube(lo,hi):return mf.Manifold.cube(np.array(hi)-lo).translate(lo)
def union(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def put(n,m,mat=WOOD,new=False,axis='X',transfer=False):
 assert m.status()==mf.Error.NoError and m.volume()>0,(n,m.status());a=m.to_mesh64();v=np.asarray(a.vert_properties[:,:3]);f=np.asarray(a.tri_verts);solid(v.astype(np.float32).astype(np.float64),f,n+' saved');OUT['objects'].append({'name':n,'new':new,'material':mat,'axis':axis,'v':v.tolist(),'f':f.tolist(),'volume_m3':m.volume(),'bodies':len(m.decompose()),'transfer':transfer});print(n,round(m.volume(),6),len(m.decompose()),flush=True)
def rod(a,b,r,sides=16):
 a=np.array(a,float);b=np.array(b,float);z=(b-a)/np.linalg.norm(b-a);x=np.cross(z,[0.,0.,1.])
 if np.linalg.norm(x)<1e-8:x=np.array([1.,0.,0.])
 x/=np.linalg.norm(x);y=np.cross(z,x);return mf.Manifold.cylinder(float(np.linalg.norm(b-a)),r,r,sides).transform(np.c_[x,y,z,a])
def beam(a,b,w,d):
 a=np.array(a,float);b=np.array(b,float);z=(b-a)/np.linalg.norm(b-a);x=np.cross(z,[0.,0.,1.])
 if np.linalg.norm(x)<1e-8:x=np.array([1.,0.,0.])
 x/=np.linalg.norm(x);y=np.cross(z,x);return mf.Manifold.cube([w,d,float(np.linalg.norm(b-a))],True).transform(np.c_[x,y,z,(a+b)/2])
def section(poly,thick):return mf.CrossSection([np.array(orient(Polygon(poly),1).exterior.coords)[:-1]]).extrude(thick)
def vertical_profile(poly,a,b,width):
 a=np.array(a,float);b=np.array(b,float);u=(b-a)/np.linalg.norm(b-a);lat=np.array([-u[1],u[0]]);m=section(poly,width);return m.transform(np.array([[u[0],0,lat[0],a[0]-lat[0]*width/2],[u[1],0,lat[1],a[1]-lat[1]*width/2],[0,1,0,0]],float))
def fy(x):return -14.295+(x-13.60)*.009
def write():
 (D/'Prepared_Geometry.json').write_text(json.dumps(OUT,ensure_ascii=False,separators=(',',':')),encoding='utf8')
