import ctypes as C
import numpy as np
import skp_api as su
def fill_holes(ents,g,material):
 su.bind('SUGeometryInputFaceAddInnerLoop',[su.Ref,su.SZ,su.PRef])
 rings=[g['outer']]+g['holes'];q=np.array([p for ring in rings for p in ring]);N=len(q);vs0=np.vstack([np.c_[q,np.full(N,g['z'])],np.c_[q,np.full(N,g['z']+g['height'])]])
 geom=su.new('SUGeometryInputCreate');vs=(su.Point*len(vs0))(*[su.Point(*[v/.0254 for v in p]) for p in vs0]);su.ck(su.SUGeometryInputSetVertices(geom,len(vs0),vs))
 def loop(indices):
  r=su.new('SULoopInputCreate')
  for i in indices:su.ck(su.SULoopInputAddVertexIndex(r,int(i)))
  return r
 for top in [False,True]:
  outer=list(range(len(rings[0])));outer=[i+N for i in outer] if top else outer[::-1];lp=loop(outer);face=su.SZ();su.ck(su.SUGeometryInputAddFace(geom,C.byref(lp),C.byref(face)));off=len(rings[0])
  for ring in rings[1:]:
   ids=list(range(off,off+len(ring)));ids=[i+N for i in ids] if top else ids[::-1];lp=loop(ids);su.ck(su.SUGeometryInputFaceAddInnerLoop(geom,face,C.byref(lp)));off+=len(ring)
 off=0
 for ring in rings:
  for j in range(len(ring)):
   i=off+j;k=off+(j+1)%len(ring);lp=loop([i,k,k+N,i+N]);face=su.SZ();su.ck(su.SUGeometryInputAddFace(geom,C.byref(lp),C.byref(face)))
  off+=len(ring)
 su.ck(su.SUEntitiesFill(ents,geom,True));su.ck(su.SUGeometryInputRelease(C.byref(geom)))
 n=su.count('SUEntitiesGetNumFaces',ents);arr=(su.Ref*n)();got=su.SZ();su.ck(su.SUEntitiesGetFaces(ents,n,arr,C.byref(got)))
 for f in arr:su.ck(su.SUFaceSetFrontMaterial(f,material));su.ck(su.SUFaceSetBackMaterial(f,material))
