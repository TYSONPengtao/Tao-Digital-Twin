"""Photo 002312: place the kitchen's east posts just inside the bent outer wall."""
from v24_20_common import *
from shapely.geometry import LineString
YS=np.array([-11.24,-8.26,-5.94,-2.96]);OLDX=13.060106;RIDGE=11.7625;BASE=-.2
contours=load('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry').slice(1.).to_polygons()
def inner_wall(y):
 hits=[]
 def collect(g):
  if g.is_empty:return
  if g.geom_type=='Point':hits.append(g.x)
  elif g.geom_type=='LineString':hits.extend(p[0]for p in g.coords)
  elif hasattr(g,'geoms'):
   for q in g.geoms:collect(q)
 for p in contours:collect(LineString(np.r_[p,p[:1]]).intersection(LineString([(12.5,y),(15.,y)])))
 return min(x for x in hits if x>12.5)
inner=np.array([inner_wall(float(y))for y in YS]);NEWX=inner-.125;DX=NEWX-OLDX
def shift(y):return float(np.interp(y,YS,DX))
def deform_frames(m):
 parts=[]
 for c in m.decompose():
  d=c.to_mesh64();v=np.array(d.vert_properties[:,:3]);f=np.array(d.tri_verts);lo=v.min(0);hi=v.max(0);mid=(lo+hi)/2
  if hi[0]<=RIDGE+.01:parts.append(c);continue
  delta=shift(float(YS[np.argmin(abs(YS-mid[1]))]))
  if lo[0]>12.65 and hi[0]-lo[0]<.5 and hi[1]-lo[1]<.5:
   v[:,0]+=delta
   if hi[2]<-.19:pass
   elif lo[2]<-.15 and hi[2]>1.8:
    top=hi[2];mask=v[:,2]>BASE;v[mask,2]=BASE+(v[mask,2]-BASE)*(top-.488*delta-BASE)/(top-BASE)
   else:v[:,2]-=.488*delta
  else:
   w=np.clip((v[:,0]-RIDGE)/(OLDX-RIDGE),0,1);dd=w*delta;v[:,0]+=dd;v[:,2]-=.488*dd
  parts.append(solid(v,f))
 return union(parts)

def deform_roof_timber(n):
 parts=[]
 for c in load(n).decompose():
  d=c.to_mesh64();v=np.array(d.vert_properties[:,:3]);f=np.array(d.tri_verts);lo=v.min(0);hi=v.max(0);mid=(lo+hi)/2
  if hi[0]<=RIDGE+.01:parts.append(c);continue
  if 'PURLINS'in n and lo[0]>RIDGE+.55 and hi[1]-lo[1]>2:
   r=(hi[0]-lo[0])/2;xc=mid[0];w=np.clip((xc-RIDGE)/(OLDX-RIDGE),0,1);ys=sorted(set([float(lo[1]),float(hi[1])]+[float(y)for y in YS if lo[1]<y<hi[1]]));z=mid[2];pts=[[xc+shift(y)*w,y,z-.488*shift(y)*w]for y in ys];rr=[rod(a,b,r,24)for a,b in zip(pts[:-1],pts[1:])];rr += [mf.Manifold.sphere(r,24).translate(p)for p in pts[1:-1]];parts.append(union(rr));continue
  weight=np.clip((v[:,0]-RIDGE)/(OLDX-RIDGE),0,1);dd=np.array([shift(y)for y in v[:,1]])*weight;v[:,0]+=dd;v[:,2]-=.488*dd;parts.append(solid(v,f))
 return union(parts)
