"""Local storage roof mapping shared by preparation, builder and QA (metres)."""
import math
import numpy as np
S=np.array([.016029690898441355,.420800478890346,9.189301106683242])
N=np.array([-.027456583964376412,-.42431481621893957,-.3378428286056173])
BACK=np.array([[13.0393619537,-8.8],[13.9509000778,-8.8612480164],[16.3227519989,-9.3169326782],[17.222536087,-9.6731796265],[18.8243732452,-10.4479341507]])
POSTS=[(13.42,-14.65),(18.26,-15.60)]
def ridge(x):return -((N[0]-S[0])*x+N[2]-S[2])/(N[1]-S[1])
def north_boundary(x):
 # Smooth monotone Hermite trace, constrained to the source-derived foundation.
 x=float(x);xx=BACK[:,0];yy=BACK[:,1];ds=np.diff(yy)/np.diff(xx);mm=np.empty(len(xx));mm[0]=ds[0];mm[-1]=ds[-1]
 for k in range(1,len(xx)-1):
  a=xx[k]-xx[k-1];b=xx[k+1]-xx[k];mm[k]=(a+b)/(a/ds[k-1]+b/ds[k])
 k=max(0,min(len(xx)-2,int(np.searchsorted(xx,x)-1)));dx=xx[k+1]-xx[k];t=(x-xx[k])/dx
 return float((2*t**3-3*t*t+1)*yy[k]+(t**3-2*t*t+t)*dx*mm[k]+(-2*t**3+3*t*t)*yy[k+1]+(t**3-t*t)*dx*mm[k+1]-.050)
def south_edge(x):return -16.87+.126*(x-13.3)
def south_eave_z(x):return 3.055-.065*(x-13.3)
def roof_z(x,y):
 r=ridge(x)
 if y>=r:return float(np.dot([x,y,1],N))
 t=(r-y)/(r-south_edge(x));zr=float(np.dot([x,r,1],S));return zr+(south_eave_z(x)-zr)*t
def warp(p):
 x,y,z=map(float,p)
 if x<=11.68:return np.array([x,y,z])
 w=max(0.,min(1.,(x-11.68)/(13.30-11.68)));r=ridge(x);sf=-16.35+.012*(x-13.3);nf=-9.104-.30*(x-13.3)
 if y<r:
  t=max(0.,min(1.2,(r-y)/(r-sf)));nx=x-.48*t*max(0.,1-(x-13.3)/2.0)**2*w if x>12.9 else x
  ny=y+w*t*(south_edge(x)-sf);old=float(np.dot([x,y,1],S));nz=z+w*(roof_z(x,ny)-old)
 else:
  t=max(0.,min(1.2,(y-r)/(nf-r)));nx=x;ny=y+w*t*(north_boundary(x)+.21-nf);nz=z+w*N[1]*(ny-y)
 return np.array([nx,ny,nz])
def structure_warp(p):
 x,y,z=map(float,p)
 if x<13.13 or y>-8.60 or z<2.22:return np.array(p,float)
 # Existing rear room columns remain upright. Only their roof-level junction
 # blends into the refitted purlins; lower joinery is immobile.
 rear=[(13.6444,-9.8021),(15.7202,-10.2576),(18.2594,-10.8335)]
 if any(abs(x-a)<.115 and abs(y-b)<.22 for a,b in rear) and z<3.45:return np.array(p,float)
 w=max(0.,min(1.,(z-2.22)/.40));q=warp(p);return np.array(p,float)+(q-np.array(p))*w
def masonry_warp(p):
 x,y,z=map(float,p)
 if x<13.13 or y>-8.60 or z<2.22:return np.array(p,float)
 old=float(np.dot([x,y,1],S if y<ridge(x)else N));w=max(0.,min(1.,(z-2.22)/.40))
 return np.array([x,y,z+w*(roof_z(x,y)-old)])
