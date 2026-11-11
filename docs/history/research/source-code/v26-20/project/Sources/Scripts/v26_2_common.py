from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from scipy.spatial import cKDTree
from v24_16_common import solid,cube,union,section
D=W/'v26_2';I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};REL={};CACHE={};GLOBAL_MATS=[]
def arr(n):return np.load(D/I[n]['file'])
def uv_project(v,f):
 t=v[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);axis=np.argmax(abs(no),axis=1);uv=np.zeros((len(f),3,2))
 for k,ds in [(0,[1,2]),(1,[0,2]),(2,[0,1])]:uv[axis==k]=t[axis==k][:,:,ds]
 return uv
def remap(a,v,f):
 old=a['v'][a['f']];tr=v[f];ids=cKDTree(old.mean(1)).query(tr.mean(1),k=min(24,len(old)))[1];ids=np.asarray(ids).reshape(len(f),-1);p=old[ids];A=p[:,:,1]-p[:,:,0];B=p[:,:,2]-p[:,:,0];Q=tr.mean(1)[:,None]-p[:,:,0];aa=np.einsum('nki,nki->nk',A,A);ab=np.einsum('nki,nki->nk',A,B);bb=np.einsum('nki,nki->nk',B,B);aq=np.einsum('nki,nki->nk',A,Q);bq=np.einsum('nki,nki->nk',B,Q);det=np.maximum(aa*bb-ab*ab,1e-25);s=(bb*aq-ab*bq)/det;t=(aa*bq-ab*aq)/det;pen=np.maximum(-s,0)+np.maximum(-t,0)+np.maximum(s+t-1,0);no=np.cross(A,B);dist=abs(np.einsum('nki,nki->nk',no,Q))/np.maximum(np.linalg.norm(no,axis=2),1e-25)+pen;pick=ids[np.arange(len(f)),dist.argmin(1)];return a['mi'][pick],bary_uv(tr,old[pick],a['uv'][pick])
def bary_uv(tr,old,uv):
 A=old[:,1]-old[:,0];B=old[:,2]-old[:,0];Q=tr-old[:,None,0];aa=np.einsum('ni,ni->n',A,A);ab=np.einsum('ni,ni->n',A,B);bb=np.einsum('ni,ni->n',B,B);aq=np.einsum('nki,ni->nk',Q,A);bq=np.einsum('nki,ni->nk',Q,B);det=np.maximum(aa*bb-ab*ab,1e-25);s=(bb[:,None]*aq-ab[:,None]*bq)/det[:,None];t=(aa[:,None]*bq-ab[:,None]*aq)/det[:,None];return uv[:,None,0]+s[:,:,None]*(uv[:,None,1]-uv[:,None,0])+t[:,:,None]*(uv[:,None,2]-uv[:,None,0])
def tracked(v,f,mats,mi=None,uv=None,name=''):
 v=np.array(v,dtype=np.float64,order='C',copy=True);f=np.array(f,dtype=np.uint64,order='C',copy=True);mi=np.zeros(len(f),int)if mi is None else np.asarray(mi);uv=uv_project(v,f)if uv is None else np.asarray(uv)
 rid=mf.Manifold.reserve_ids(1);me=mf.Mesh64(v,f,run_index=np.array([0,len(f)*3],np.uint64),run_original_id=np.array([rid],np.uint32),face_id=np.arange(len(f),dtype=np.uint64));m=mf.Manifold(me)
 if m.status()!=mf.Error.NoError or m.volume()<=0:
  good=solid(v,f,name).to_mesh64();vv=np.array(good.vert_properties[:,:3]);ff=np.array(good.tri_verts);mi,uv=remap({'v':v,'f':f,'mi':mi,'uv':uv},vv,ff);v=vv;f=ff.astype(np.uint64);me=mf.Mesh64(v,f,run_index=np.array([0,len(f)*3],np.uint64),run_original_id=np.array([rid],np.uint32),face_id=np.arange(len(f),dtype=np.uint64));m=mf.Manifold(me)
 assert m.status()==mf.Error.NoError and m.volume()>0,(name,m.status(),m.volume())
 REL[rid]={'name':name,'v':v,'f':f,'mi':mi,'uv':uv,'mats':mats}
 for mat in mats:
  if mat not in GLOBAL_MATS:GLOBAL_MATS.append(mat)
 return m
def load(n):
 if n not in CACHE:
  a=arr(n);CACHE[n]=tracked(a['v'],a['f'],I[n]['materials'],a['mi'],a['uv'],n)
 return CACHE[n]
def finish(m,mat,name='new geometry'):
 a=m.to_mesh64();return tracked(a.vert_properties[:,:3],a.tri_verts,[mat],name=name)
def clean(m):
 for k in range(3):
  a=m.to_mesh64();me=mf.Mesh64(np.array(a.vert_properties[:,:3]).astype(np.float32).astype(np.float64),np.array(a.tri_verts,dtype=np.uint64),run_index=np.array(a.run_index,dtype=np.uint64),run_original_id=np.array(a.run_original_id,dtype=np.uint32),face_id=np.array(a.face_id,dtype=np.uint64));m=mf.Manifold(me);assert m.status()==mf.Error.NoError,m.status();parts=m.decompose();keep=[p for p in parts if p.volume()>1e-10]
  if len(parts)==len(keep):return m
  m=union(keep)
 raise RuntimeError('Collapsed zero-volume geometry did not stabilize')
def export(n,m,reason='',**kw):
 m=clean(m);a=m.to_mesh64();v=np.array(a.vert_properties[:,:3]);f=np.array(a.tri_verts);mi=np.zeros(len(f),np.int32);uv=uv_project(v,f);ids=np.array(a.face_id);rs=a.run_index;provenance=[]
 for j,rid in enumerate(a.run_original_id):
  lo,hi=rs[j]//3,rs[j+1]//3
  if rid not in REL:continue
  r=REL[rid];ix=ids[lo:hi];assert ix.max(initial=0)<len(r['f']),(rid,ix.max(),len(r['f']));old=r['v'][r['f'][ix]];uv[lo:hi]=bary_uv(v[f[lo:hi]],old,r['uv'][ix]);mi[lo:hi]=[GLOBAL_MATS.index(r['mats'][i])for i in r['mi'][ix]];provenance.append({'source':r['name'],'triangles':int(hi-lo)})
 fn=n+'.npz';np.savez_compressed(D/fn,v=v,f=f,mi=mi,uv=uv);row={'name':n,'file':fn,'materials':list(GLOBAL_MATS),'triangles':len(f),'volume_m3':m.volume(),'closed_components':len(m.decompose()),'reason':reason,'provenance':provenance,**kw};return row,m
def extrude_tri(t,axis,end):
 v=np.vstack([t,t.copy()]);v[3:,axis]=end
 if np.max(abs(v[3:]-v[:3]))<1e-6:return None
 f=np.array([[0,2,1],[3,4,5],[0,1,4],[0,4,3],[1,2,5],[1,5,4],[2,0,3],[2,3,5]])
 try:return solid(v,f,'wall surface extension')
 except RuntimeError:return None
