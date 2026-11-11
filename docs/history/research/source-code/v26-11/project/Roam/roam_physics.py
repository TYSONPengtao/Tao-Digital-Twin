"""Blender-only, human-sized capsule movement on the model's real triangles."""
import math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HEIGHT=1.65
RADIUS=.215
STEP_HEIGHT=.255
GRAVITY=9.81
JUMP_SPEED=3.45
WALK_SPEED=1.85
RUN_SPEED=3.10
WALKABLE=.64
SKIN=.003

class World:
 def __init__(self,vertices,triangles):
  self.bvh=BVHTree.FromPolygons(vertices,triangles,all_triangles=True,epsilon=.00001)
  self.bottom=min(v[2]for v in vertices)-2.;self.top=max(v[2]for v in vertices)+2.
 def down(self,xy,top,bottom):
  start=Vector((xy[0],xy[1],top))
  for _ in range(12):
   hit,no,index,dist=self.bvh.ray_cast(start,Vector((0,0,-1)),max(.00001,start.z-bottom))
   if hit is None:return None
   if no.z>=WALKABLE:return hit.z
   start=hit-Vector((0,0,.0005))
   if start.z<bottom:return None
  return None
 def ground(self,p,up=STEP_HEIGHT+.015,down=.32):
  # Small support footprint, rather than a ray which misses tread edges.
  values=[]
  reach=RADIUS+.012
  ring=[(reach*math.cos(k*math.tau/8),reach*math.sin(k*math.tau/8))for k in range(8)]
  for x,y in [(0,0)]+ring:
   z=self.down((p.x+x,p.y+y),p.z+up,p.z-down)
   if z is not None:values.append(z)
  if not values:return None
  z=max(values)
  # Seat the lowest capsule sphere against the actual sloped scan triangles.
  # Sparse foot rays alone leave small terrain ridges intersecting the sphere.
  for _ in range(3):
   centre=Vector((p.x,p.y,z+RADIUS));raise_by=0.
   for loc,no,index,d in self.bvh.find_nearest_range(centre,RADIUS-SKIN+.0003):
    if no.z>=WALKABLE and loc.z<=z+STEP_HEIGHT:
     raise_by=max(raise_by,max(0.,(RADIUS-SKIN+.0004-d)/no.z))
   if raise_by<.00005:break
   z+=min(.10,raise_by)
  return z
 def clear(self,p,radius=RADIUS):
  # Six overlapping spheres give a capsule; ranges catch thin walls even if
  # a nearer floor triangle is present. The analytic foot plane stays at p.z.
  count=7
  for i in range(count):
   h=radius+(HEIGHT-2*radius)*i/(count-1);centre=p+Vector((0,0,h))
   for loc,no,index,d in self.bvh.find_nearest_range(centre,radius-SKIN):
    if no.z>=WALKABLE and loc.z<=p.z+.008:continue
    if d<radius-SKIN:return False
  return True
 def camera(self,target,desired):
  delta=desired-target;L=delta.length
  if L<.02:return desired.copy()
  direction=delta/L;distance=L
  right=direction.cross(Vector((0,0,1))).normalized()
  for offset in [Vector((0,0,0)),right*.10,-right*.10,Vector((0,0,.10)),Vector((0,0,-.10))]:
   hit,no,index,d=self.bvh.ray_cast(target+offset,direction,L)
   if hit is not None:distance=min(distance,max(.12,d-.15))
  return target+direction*distance

class Walker:
 def __init__(self,world,position):
  self.world=world;self.p=Vector(position);self.vz=0.;self.grounded=False;self.travel=0.;self.last_wall=False
  self.last_safe=None;self.recoveries=0;self.edge_stops=0
  self.place(position)
 def place(self,position):
  self.p=Vector(position);z=self.world.ground(self.p,up=.40,down=1.5)
  if z is not None:self.p.z=z;self.grounded=True
  else:
   z=self.world.down(self.p,self.world.top,self.world.bottom)
   if z is not None:self.p.z=z;self.grounded=True
   elif self.last_safe is not None:self.p=self.last_safe.copy();self.grounded=True
   else:self.grounded=False
  self.vz=0.
  if self.grounded and self.world.clear(self.p):self.last_safe=self.p.copy()
 def recover(self):
  if self.last_safe is not None:
   self.p=self.last_safe.copy();self.vz=0.;self.grounded=True;self.recoveries+=1
 def _horizontal(self,d):
  trial=self.p+d;z=None
  if self.grounded:
   z=self.world.ground(trial)
   if z is not None and -.321<=z-self.p.z<=STEP_HEIGHT+.016:trial.z=z
   else:
    # Finite scans and genuine holes have no support. Stop at the edge;
    # never introduce a flat invisible floor through the site or stairwell.
    self.edge_stops+=1;return False
  elif self.last_safe is not None:
   # A jump can cross a short opening only while real landing support exists.
   landing=self.world.ground(trial,up=max(.75,self.last_safe.z-trial.z+.75),down=max(1.05,trial.z-self.last_safe.z+1.05))
   if landing is None:self.edge_stops+=1;return False
  if not self.world.clear(trial):return False
  moved=(trial-self.p).length;self.p=trial;self.travel+=moved
  if self.grounded:self.last_safe=self.p.copy()
  if self.grounded and z is None:self.grounded=False;self.vz=0
  return True
 def update(self,direction,seconds,jump=False,run=False):
  dt=min(.10,max(0.,seconds));steps=max(1,math.ceil(dt/(1/120)));dt/=steps
  direction=Vector((direction[0],direction[1],0))
  if direction.length>1:direction.normalize()
  if jump and self.grounded:self.grounded=False;self.vz=JUMP_SPEED
  self.last_wall=False
  for _ in range(steps):
   delta=direction*((RUN_SPEED if run else WALK_SPEED)*dt)
   if delta.length>1e-8:
    if not self._horizontal(delta):
     self.last_wall=True
     # Slide against a wall, preserving the free component of diagonal input.
     if abs(delta.x)>1e-9:self._horizontal(Vector((delta.x,0,0)))
     if abs(delta.y)>1e-9:self._horizontal(Vector((0,delta.y,0)))
   if not self.grounded:
    self.vz-=GRAVITY*dt;trial=self.p+Vector((0,0,self.vz*dt))
    if self.vz<=0:
     z=self.world.ground(self.p,up=.018,down=max(.08,self.p.z-trial.z+.025))
     if z is not None and trial.z<=z+.004 and z<=self.p.z+.020:
      trial.z=z
      if self.world.clear(trial):self.p=trial;self.vz=0.;self.grounded=True;self.last_safe=self.p.copy();continue
    if self.world.clear(trial):self.p=trial
    elif self.vz>0:self.vz=0.
    else:
     z=self.world.ground(self.p,up=.025,down=.12)
     if z is not None:self.p.z=z;self.vz=0.;self.grounded=True
   if self.last_safe is not None and (not all(math.isfinite(x)for x in self.p)or self.p.z<self.last_safe.z-.80):self.recover()
  return self.p.copy()
