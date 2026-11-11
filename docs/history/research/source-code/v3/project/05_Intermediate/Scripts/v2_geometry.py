import math
import numpy as np,rhino3dm as rh,mapbox_earcut
TYPES={'prism_holes','lathe','polyhedron','terrain'}
def data(g):
 typ=g['type']
 if typ in ['polyhedron','terrain']:
  v=np.array(g['vertices'],float);fs=[]
  for f in g['faces']:
   if len(set(f))!=len(f):continue
   if len(f)==3 and np.linalg.norm(np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]]))<1e-12:continue
   if len(f)==4:
    pp=v[f];n=np.cross(pp[1]-pp[0],pp[2]-pp[0]);n/=np.linalg.norm(n)+1e-30
    if abs(np.dot(pp[3]-pp[0],n))>1e-7:fs.extend([[f[0],f[1],f[2]],[f[0],f[2],f[3]]]);continue
   fs.append(f)
  return v,fs,None,None
 if typ=='prism_holes':
  rings=[g['outer']]+g['holes'];q=np.array([p for ring in rings for p in ring],float);ends=np.cumsum([len(ring) for ring in rings]).astype(np.uint32);tri=mapbox_earcut.triangulate_float64(q,ends).reshape(-1,3);N=len(q);z=g['z'];h=g['height'];v=np.vstack([np.c_[q,np.full(N,z)],np.c_[q,np.full(N,z+h)]]);f=[t[::-1].tolist() for t in tri]+[(t+N).tolist() for t in tri];offset=0
  for ring in rings:
   m=len(ring)
   f.extend([[offset+i,offset+(i+1)%m,offset+(i+1)%m+N,offset+i+N] for i in range(m)]);offset+=m
  # Node cap bridges at profile vertices when aligned holes create collinear edges.
  from collections import Counter
  edges=Counter(tuple(sorted((a,b))) for face in f for a,b in zip(face,face[1:]+face[:1]))
  if any(n!=2 for n in edges.values()):
   nv=v.tolist();newfaces=[]
   for face in f:
    if len(face)!=3:newfaces.append(face);continue
    offset=N if face[0]>=N else 0;boundary=[];extra=False
    for a,b in zip(face,face[1:]+face[:1]):
     aa=v[a,:2];bb=v[b,:2];d=bb-aa;ll=np.dot(d,d);rel=q-aa;tt=rel@d/ll;cross=rel[:,0]*d[1]-rel[:,1]*d[0];ids=np.where((tt>1e-8)&(tt<1-1e-8)&(abs(cross)<1e-9))[0];ids=ids[np.argsort(tt[ids])];boundary.append(a);boundary.extend((ids+offset).tolist());extra|=len(ids)>0
    if extra:
     center=len(nv);nv.append(v[face].mean(0).tolist());newfaces.extend([[center,a,b] for a,b in zip(boundary,boundary[1:]+boundary[:1])])
    else:newfaces.append(face)
   v=np.array(nv);f=newfaces
  return v,f,None,None
 if typ=='lathe':
  profile=g['profile'];N=g.get('segments',128);fl=g.get('flutes',0);v=[];f=[]
  for r,z in profile:
   for i in range(N):
    t=2*math.pi*i/N;rad=r-.006*(.5+.5*math.cos(fl*t)) if fl else r;v.append([rad*math.cos(t),rad*math.sin(t),z])
  for j in range(len(profile)-1):
   f.extend([[j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i] for i in range(N)])
  f+=[list(range(N-1,-1,-1)),list(range((len(profile)-1)*N,len(profile)*N))]
  return np.array(v),f,None,None
 raise ValueError(typ)
def native(g):
 if g['type']=='prism_holes':
  def curve(ring):return rh.PolylineCurve([rh.Point3d(x,y,0) for x,y in ring+[ring[0]]])
  ex=rh.Extrusion.Create(curve(g['outer']),g['height'],True)
  if ex is None:raise ValueError('Extrusion failed '+str(g))
  for hole in g['holes']:assert ex.AddInnerProfile(curve(hole))
  ex.Transform(rh.Transform.Translation(0,0,g['z']));return ex
 if g['type']=='lathe' and not g.get('flutes'):
  curve=rh.PolylineCurve([rh.Point3d(r,0,z) for r,z in g['profile']]);axis=rh.Line(rh.Point3d(0,0,0),rh.Point3d(0,0,1));rev=rh.RevSurface.Create(curve,axis,0,2*math.pi);return rh.Brep.CreateFromRevSurface(rev,True,True)
 v,f,_,_=data(g);m=rh.Mesh()
 for a in v:m.Vertices.Add(*a)
 for face in f:
  if len(face)<=4:m.Faces.AddFace(*face)
  else:
   p=v[face,:2];tri=mapbox_earcut.triangulate_float64(p,np.array([len(p)],np.uint32)).reshape(-1,3)
   sign=np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])
   for t in tri:m.Faces.AddFace(*[face[i] for i in (t[::-1] if sign<0 else t)])
 m.Normals.ComputeNormals();m.Compact();b=rh.Brep.CreateFromMesh(m,True)
 if b is None:raise ValueError('Brep construction failed '+g['type'])
 return b
