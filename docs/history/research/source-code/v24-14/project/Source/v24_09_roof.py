"""Screen-wall four-corner forked roof, native closed mesh construction."""
import bpy,bmesh,math,json
from mathutils import Vector
from pathlib import Path
from v24_03_junction_blender import _mesh,_closed_stats
X0=2.95;X1=11.10;CY=-16.9;HY=.74;JL=3.25;JR=10.80
def old_h(x,y):
 u=abs((x-7.025)/4.075);v=abs((y-CY)/HY)
 return 3.88-.25*v**1.4+.65*u**4+.12*u**5*v**2
def h(x,y):
 u=abs((x-7.025)/4.075);v=abs((y-CY)/HY);u0=(7.025-JL)/4.075;t=max(0,min(1,(u-u0)/(1-u0)));s=t*t*(3-2*t)
 z=old_h(x,y)-.46*s*(1-v**1.6)+.10*s*v**3
 # The two hip ridges rise smoothly from the actual fork node. Constrain
 # their support surface too, avoiding a loose W-shaped roll over a low fan.
 if t>0:
  xe,xj=(X0,JL)if x<7.025 else(X1,JR);start=old_h(xj,CY);end=old_h(xe,CY+HY)+.10;target=start+(end-start)*t*t;raw=old_h(x,CY+HY*t)-.46*s*(1-t**1.6)+.10*s*t**3
  z+=(target-raw)*math.exp(-((v-t)/.20)**2)
 return z
class Batch:
 def __init__(self):self.v=[];self.f=[];self.mi=[];self.parts=0
 def add(self,V,F,mat=0):
  k=len(self.v);self.v.extend(tuple(p)for p in V);self.f.extend([tuple(k+i for i in f)for f in F]);self.mi.extend([mat]*len(F));self.parts+=1
 def rod(self,points,r=.02,segs=10,closed=False,radii=None,mat=0):
  pts=[Vector(p)for p in points]
  if closed and (pts[0]-pts[-1]).length<1e-8:pts.pop()
  V=[];F=[];n=len(pts)
  for j,p in enumerate(pts):
   t=(pts[(j+1)%n]-pts[(j-1)%n])if closed else pts[min(j+1,n-1)]-pts[max(j-1,0)];t.normalize();a=t.cross(Vector((0,1,0)))
   if a.length<.1:a=t.cross(Vector((1,0,0)))
   a.normalize();b=t.cross(a).normalized();rr=r if radii is None else radii[j]
   for k in range(segs):V.append(tuple(p+rr*(a*math.cos(2*math.pi*k/segs)+b*math.sin(2*math.pi*k/segs))))
  for j in range(n if closed else n-1):
   J=(j+1)%n
   for k in range(segs):F.append((j*segs+k,j*segs+(k+1)%segs,J*segs+(k+1)%segs,J*segs+k))
  if not closed:F.extend([tuple(range(segs-1,-1,-1)),tuple((n-1)*segs+k for k in range(segs))])
  self.add(V,F,mat)
 def object(self,col,name,mats,replace=True,weld=False,smooth=False):
  ob=_mesh(bpy,col,name+'_TEMP'if replace else name,self.v,self.f,mats[0]);ob.data.materials.clear()
  for m in mats:ob.data.materials.append(m)
  for p,i in zip(ob.data.polygons,self.mi):p.material_index=i;p.use_smooth=smooth
  if weld:
   bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
  if replace:
   dst=bpy.data.objects[name];old=dst.data;dst.data=ob.data;bpy.data.objects.remove(ob,do_unlink=True)
   if not old.users:bpy.data.meshes.remove(old)
   ob=dst
  ob['V24_09_Closed_Parts']=self.parts;return ob
def patch(batch,xs,ys,zfn,thick,mat=0):
 nx,ny=len(xs),len(ys);top=[(x,y,zfn(x,y))for x in xs for y in ys];N=len(top);V=top+[(x,y,z-thick)for x,y,z in top];F=[]
 for i in range(nx-1):
  for j in range(ny-1):
   a=i*ny+j;b=a+ny;F.extend([(a,b,b+1),(a,b+1,a+1),(a+N,b+1+N,b+N),(a+N,a+1+N,b+1+N)])
 ring=list(range(ny))+[(i+1)*ny-1 for i in range(1,nx)]+list(range((nx-1)*ny+ny-2,(nx-1)*ny-1,-1))+[i*ny for i in range(nx-2,0,-1)]
 for a,b in zip(ring,ring[1:]+ring[:1]):F.append((a,a+N,b+N,b))
 batch.add(V,F,mat)
def cover(batch,axis,c,a,b,mat=0):
 V=[];F=[];n=13;segs=4
 for j in range(segs):
  s=a+(b-a)*j/(segs-1);x,y=(c,s)if axis=='Y'else(s,c);eps=.0001
  dz=((h(x,y+eps)-h(x,y-eps))if axis=='Y'else(h(x+eps,y)-h(x-eps,y)))/(2*eps);t=Vector((0,1,dz))if axis=='Y'else Vector((1,0,dz));t.normalize();lat=Vector((1,0,0))if axis=='Y'else Vector((0,1,0));normal=t.cross(lat)
  if normal.z<0:normal=-normal
  normal.normalize();p=Vector((x,y,h(x,y)-.002))
  for r in[.051,.041]:
   for k in range(n):an=k*math.pi/(n-1);V.append(tuple(p+r*(lat*math.cos(an)+normal*math.sin(an))))
 for j in range(segs-1):
  A=j*2*n;B=(j+1)*2*n
  for k in range(n-1):F.extend([(A+k,A+k+1,B+k+1,B+k),(A+n+k,B+n+k,B+n+k+1,A+n+k+1)])
  F.extend([(A,B,B+n,A+n),(A+n-1,A+2*n-1,B+2*n-1,B+n-1)])
 for j in[0,segs-1]:
  A=j*2*n
  for k in range(n-1):F.append((A+k,A+n+k,A+n+k+1,A+k+1))
 batch.add(V,F,mat)
def ring(rect,nx=128,ny=32):
 x,y,X,Y=rect;return [(x+(X-x)*i/nx,y)for i in range(nx)]+[(X,y+(Y-y)*i/ny)for i in range(ny)]+[(X-(X-x)*i/nx,Y)for i in range(nx)]+[(x,Y-(Y-y)*i/ny)for i in range(ny)]
def cornice():
 # A single continuous solid: curved top, stepped underside and curved caps.
 b=Batch();outer=[3.01,-17.54,11.04,-16.26];mid=[3.10,-17.40,10.95,-16.40];inner=[3.20,-17.23,10.85,-16.57];N=len(ring(outer));rings=[(outer,0),(outer,.035),(mid,.035),(mid,.085),(inner,.085),(inner,.145)];V=[];F=[]
 for rect,d in rings:V.extend((x,y,h(x,y)-.075-d)for x,y in ring(rect))
 for j in range(len(rings)-1):
  for k in range(N):F.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
 # The cap grids share their boundary coordinates with the lofted rings.
 for rect,d,up in[(outer,0,True),(inner,.145,False)]:
  x,y,X,Y=rect;off=len(V);nx=129;ny=33;V.extend((x+(X-x)*i/128,y+(Y-y)*j/32,h(x+(X-x)*i/128,y+(Y-y)*j/32)-.075-d)for i in range(nx)for j in range(ny))
  for i in range(nx-1):
   for j in range(ny-1):
    a=off+i*ny+j;f=(a,a+ny,a+ny+1,a+1);F.append(f if up else f[::-1])
 b.add(V,F);return b
def build_roof(col,mats,trim,work):
 changed=[];counts={};prefix='SITE_SOUTH_SCREENWALL_'
 def put(s,b,mm=mats,weld=False,smooth=False):
  n=prefix+s+'_Geometry';o=b.object(col,n,mm,True,weld,smooth);changed.append(n);counts[n]={'parts':b.parts,**_closed_stats(o)};return o
 shell=Batch();patch(shell,[X0+(X1-X0)*i/120 for i in range(121)],[CY-HY+2*HY*i/24 for i in range(25)],lambda x,y:h(x,y)-.025,.050);put('CURVED_TILE_SHELL',shell,mats[:1])
 tiles=Batch();rows=[X0+.072+(X1-X0-.144)*i/49 for i in range(50)];course_count=0
 for i,x in enumerate(rows):
  v=(JL-x)/(JL-X0)if x<JL else(x-JR)/(X1-JR)if x>JR else 0;v=max(0,min(1,v));start=HY*v+.040
  for side in[-1,1]:
   if HY-start<.065:continue
   n=max(1,math.ceil((HY-start)/.25))
   for j in range(n):
    a=CY+side*(start+(HY-start)*j/n);b=CY+side*(start+(HY-start)*(j+1)/n);a,b=sorted((a,b));cover(tiles,'Y',x,a+.0015,b-.0015,(i*11+j*3+(1 if side>0 else 0))%len(mats));course_count+=1
    cx=x+.080
    if cx<X1-.025:
     patch(tiles,[cx-.074+k*.148/10 for k in range(11)],[a+.0015,(a+b)/2,b-.0015],lambda xx,yy,c=cx:h(xx,yy)-.021+.018*((xx-c)/.074)**2,.009,(i*7+j*2)%len(mats))
 # Transverse fan courses in the two end hips. They are bounded by the forks.
 fan=0
 for end in[0,1]:
  xx0,xj=(X0,JL)if end==0 else(X1,JR)
  for i in range(10):
   y=CY-.66+i*.146;v=abs((y-CY)/HY);xb=xj+(xx0-xj)*v;A,B=sorted((xx0,xb));A+=.009;B-=.045
   if B-A<.065:continue
   n=max(1,math.ceil((B-A)/.24))
   for j in range(n):
    a=A+(B-A)*j/n+.0015;b=A+(B-A)*(j+1)/n-.0015;cover(tiles,'X',y,a,b,(j*7+i*3)%len(mats));fan+=1
    cy=y+.070
    if abs(cy-CY)<.70:patch(tiles,[a,(a+b)/2,b],[cy-.062+k*.124/10 for k in range(11)],lambda xx,yy,c=cy:h(xx,yy)-.021+.016*((yy-c)/.062)**2,.009,(j*11+i)%len(mats))
 put('BARREL_TILE_ROWS',tiles)
 # Curved long eaves and four swept hip ridges: the principal ridge forks.
 edge=Batch();fork_paths=[]
 for side in[-1,1]:edge.rod([(X0+(X1-X0)*i/100,CY+side*(HY+.010),h(X0+(X1-X0)*i/100,CY+side*HY)-.012)for i in range(101)],.033,12)
 for end in[0,1]:
  xe,xj=(X0,JL)if end==0 else(X1,JR)
  for side in[-1,1]:
   pts=[]
   for j in range(33):
    t=j/32;x=xj+(xe-xj)*t;y=CY+side*HY*t;z=h(x,y)+.150*(1-t)+.085*t;pts.append((x,y,z))
   edge.rod(pts,.034,12);fork_paths.append(pts)
 # Low semicircular short eave roll between the two branch tips.
 for x in[X0,X1]:edge.rod([(x,CY-HY+2*HY*j/40,h(x,CY-HY+2*HY*j/40)-.010)for j in range(41)],.028,12)
 put('CURVED_EAVE_AND_RIDGE_BORDER',edge,smooth=True)
 # The raised fork rolls sit on closed ceramic bedding, not in empty air.
 bedding=Batch();patch(bedding,[JL+(JR-JL)*i/120 for i in range(121)],[CY-.043,CY,CY+.043],lambda x,y:h(x,y)+.011,.041)
 for pts in fork_paths:
  V=[];F=[]
  for j,p in enumerate(pts):
   prev=Vector(pts[max(0,j-1)]);nxt=Vector(pts[min(len(pts)-1,j+1)]);t=nxt-prev;normal=Vector((-t.y,t.x,0)).normalized()
   for width,top in[(-.060,False),(.060,False),(.027,True),(-.027,True)]:
    x=max(X0+.001,min(X1-.001,p[0]+normal.x*width));y=max(CY-HY+.001,min(CY+HY-.001,p[1]+normal.y*width));z=p[2]-.010 if top else h(x,y)-.030;V.append((x,y,z))
  for j in range(len(pts)-1):
   for k in range(4):F.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
  F.extend([(3,2,1,0),tuple((len(pts)-1)*4+k for k in range(4))]);bedding.add(V,F)
 bed=bedding.object(col,'V24_09_Screenwall_Solid_Fork_and_Ridge_Seats',mats[:1],False);counts[bed.name]={'parts':bedding.parts,**_closed_stats(bed)}
 lattice=Batch();L=JR-JL
 for zz,rr in[(.026,.022),(.166,.031)]:lattice.rod([(JL+L*i/100,CY,h(JL+L*i/100,CY)+zz)for i in range(101)],rr,12)
 lattice_count=52;pitch=L/lattice_count
 for i in range(lattice_count):
  cx=JL+pitch*(i+.5);pts=[]
  for k in range(4):
   a=[(-pitch*.485,0),(0,.050),(pitch*.485,0),(0,-.050)][k];b=[(-pitch*.485,0),(0,.050),(pitch*.485,0),(0,-.050)][(k+1)%4]
   for j in range(5):t=j/5;x=cx+a[0]*(1-t)+b[0]*t;pts.append((x,CY,h(x,CY)+.096+a[1]*(1-t)+b[1]*t))
  lattice.rod(pts,.008,8,closed=True)
  if i%2==0:
   lattice.rod([(cx+.018*math.cos(j*2*math.pi/16),CY,h(cx+.018*math.cos(j*2*math.pi/16),CY)+.096+.018*math.sin(j*2*math.pi/16))for j in range(16)],.0055,8,closed=True)
 put('OPEN_RIDGE_LATTICE',lattice,smooth=True)
 # Four ceramic wing terminals rise from the four fork arms. No central spear.
 fin=Batch();tip_positions=[]
 for end in[0,1]:
  xe,sign=(X0,-1)if end==0 else(X1,1)
  for side in[-1,1]:
   root=Vector((xe,CY+side*HY,h(xe,CY+side*HY)+.085));pts=[];rs=[]
   for j in range(25):
    t=j/24;p=root+Vector((sign*.018*t,side*.055*t,.60*t**1.18));pts.append(p);rs.append(.036*(1-t)**.72+.012)
   fin.rod(pts,segs=12,radii=rs);tip_positions.append(tuple(pts[-1]));p=pts[-1];fin.rod([p+Vector((0,0,-.007)),p+Vector((0,0,.009))],.018,16)
 put('V12_HIGH_RIDGE_FINIALS',fin,smooth=True)
 # Reuse the original actual eight-petal disk detail at the new long-eave rows.
 src=json.loads((Path(work)/'v12_screenwall_reference/Mutation.json').read_text());templates=next(e for e in src['add']if e['name']==prefix+'V12_LOTUS_DRIP_ENDS')['parts'][:9];axis=Vector(templates[0]['drip_disk_axis']);drips=Batch()
 for i,x in enumerate(rows):
  for side in[-1,1]:
   target=Vector((x,CY+side*(HY+.018),h(x,CY+side*HY)-.003));scale=.82
   for p in templates:
    vv=[]
    for co in p['geometry']['vertices']:
     v=(Vector(co)-axis)*scale
     if side>0:v.y=-v.y
     vv.append(target+v)
    ff=p['geometry']['faces'];ff=[f[::-1]for f in ff]if side>0 else ff;drips.add(vv,ff,i%len(mats))
 put('V12_LOTUS_DRIP_ENDS',drips)
 fascia=Batch();outer=[X0,CY-HY,X1,CY+HY];inner=[3.01,-17.54,11.04,-16.26];a=ring(outer);b=ring(inner);N=len(a);V=[];F=[]
 for rr,d in[(a,0),(b,0),(a,.046),(b,.046)]:V.extend((x,y,h(x,y)-.075-d)for x,y in rr)
 for i in range(N):
  j=(i+1)%N;F.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
 fascia.add(V,F);put('V12_CLOSED_EAVE_FASCIA',fascia,[trim],True)
 put('V12_STEPPED_MASONRY_UNDEREAVE',cornice(),[trim],True)
 return {'changed_objects':changed,'added_objects':[bed.name],'geometry':counts,'roof_footprint_m':[X0,CY-HY,X1,CY+HY],'fork_junction_x_m':[JL,JR],'fork_arm_count':4,'fork_paths':fork_paths,'solid_ridge_seats':5,'wing_terminal_count':4,'wing_tip_positions':tip_positions,'central_independent_spears':0,'long_tile_rows':len(rows),'long_cover_tile_units':course_count,'hip_fan_cover_tile_units':fan,'diamond_openings':lattice_count,'lotus_disks':100,'underside':'One closed curved stepped masonry support and closed perimeter fascia, rather than disjoint rectangular ring blocks','basis':'Photo-fitted bifurcating ridge and transverse end tile fans, especially 135801; retained registered roof plan'}
