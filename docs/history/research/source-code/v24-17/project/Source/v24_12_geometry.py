"""Level roof datums. Post skew is a plan relationship, not a roof warp."""
import math
import numpy as np
from v24_11_geometry import north_boundary,roof_z as old_roof_z,ridge as old_ridge
AXIS=.10589
RIDGE_Z=4.35
EAVE_Z=3.03
W=13.25767994
E=18.86485291
def ridge(x):return -12.15+AXIS*(x-15.8)
def front(x):return -16.87+AXIS*(x-13.3)
SLOPE=(RIDGE_Z-EAVE_Z)/(ridge(13.3)-front(13.3))
def roof_z(x,y):return RIDGE_Z+SLOPE*(y-ridge(x))if y<=ridge(x)else RIDGE_Z-.4243148162*(y-ridge(x))
def rear(x):return north_boundary(x)+.38
ANCHOR=np.array([11.74668980,-11.85272980,4.26571989])
ANCHOR2=np.array([11.90052986,-12.05187988,4.19794989])
RW=np.array([W,ridge(W),RIDGE_Z])
H=np.array([13.97961044,rear(13.97961044),roof_z(13.97961044,rear(13.97961044))])
def plane(points):return np.linalg.solve(np.c_[np.array(points)[:,:2],np.ones(3)],np.array(points)[:,2])
ADAPTERS=[([ANCHOR,ANCHOR2,RW],plane([ANCHOR,ANCHOR2,RW])),([ANCHOR,RW,H],plane([ANCHOR,RW,H]))]
def inside_triangle(x,y,tri):
 a,b,c=np.array(tri)[:,:2];q=np.array([x,y]);M=np.c_[b-a,c-a]
 u,v=np.linalg.solve(M,q-a);return u>=-1e-7 and v>=-1e-7 and u+v<=1+1e-7
def surface_z(x,y):
 if x<W:
  for tri,p in ADAPTERS:
   if inside_triangle(x,y,tri):return float(np.dot([x,y,1],p))
 return roof_z(x,y)
def masonry(p):
 x,y,z=map(float,p)
 if x<13.13 or y>-8.65 or z<2.22:return np.array(p,float)
 w=max(0.,min(1.,(z-2.22)/.40));r=old_ridge(x);a=-16.048;bb=north_boundary(x)-.30
 t=max(0.,min(1.,(y-a)/(r-a)))if y<r else max(0.,min(1.,(bb-y)/(bb-r)))
 ny=y+w*t*(ridge(x)-r)
 return np.array([x,ny,z+w*(roof_z(x,ny)-old_roof_z(x,y))])
def timber(p):
 x,y,z=map(float,p)
 if x<13.13 or y>-8.60 or z<2.45:return np.array(p,float)
 # Keep plan coordinates of all existing joinery and vertical interior posts.
 w=max(0.,min(1.,(z-2.45)/.38))
 return np.array([x,y,z+w*(roof_z(x,y)-old_roof_z(x,y))])
