from v26_2_common import *
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient

def recover_orthogonal(a,mats,name):
 """Recover original axis-aligned solids from signed source face coverage.

 Uses only planes already in the native mesh. No arbitrary replacement size,
 convex hull across an opening, or new glazing shape is introduced.
 """
 v=np.round(a['v'],5);t=v[a['f']];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);result=[]
 for mi,mat in enumerate(mats):
  ix=np.flatnonzero((a['mi']==mi)&(abs(n[:,0])>1e-10));tr=t[ix];no=n[ix]
  if not len(tr):continue
  ys=np.unique(tr[:,:,1]);zs=np.unique(tr[:,:,2]);xs=np.unique(tr[:,:,0]);cells=[]
  for y0,y1 in zip(ys,ys[1:]):
   if y1-y0<1e-6:continue
   for z0,z1 in zip(zs,zs[1:]):
    if z1-z0<1e-6:continue
    # Irrational offsets avoid native triangulation diagonals.
    y=y0+(y1-y0)*.4137;z=z0+(z1-z0)*.5723;cover=[]
    for q,nn in zip(tr,no):
     if Polygon(q[:,[1,2]]).buffer(1e-9).contains(__import__('shapely').geometry.Point(y,z)):cover.append((q[0,0],np.sign(nn[0])))
    for x0,x1 in zip(xs,xs[1:]):
     if x1-x0<1e-6:continue
     winding=sum(s for x,s in cover if x>(x0+x1)/2)
     if winding>.5:cells.append(cube([x0,y0,z0],[x1,y1,z1]))
  if cells:result.append(finish(union(cells),mat,name+' original '+mat+' recovered plane arrangement'))
 assert result,(name,'no closed cells')
 return union(result)
