from v24_16_common import *
X0=2.95;X1=11.10;JL=3.85;JR=10.20;HY=.66
wall=source('SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry');tri=wall['v'][wall['f']];q=tri[:,:,2]-1.;seg=[]
for t,d in zip(tri[(q.min(1)<0)&(q.max(1)>0)],q[(q.min(1)<0)&(q.max(1)>0)]):
 p=[]
 for a,b in [(0,1),(1,2),(2,0)]:
  if d[a]*d[b]<0:p.append(t[a]+(t[b]-t[a])*(-d[a]/(d[b]-d[a])))
 if len(p)==2:seg.append(p)
seg=np.array(seg)
def faces(x):
 ys=[]
 for p in seg:
  if p[:,0].min()-1e-6<=x<=p[:,0].max()+1e-6 and abs(p[1,0]-p[0,0])>1e-7:
   y=p[0,1]+(p[1,1]-p[0,1])*(x-p[0,0])/(p[1,0]-p[0,0])
   if -17.60<y<-16.3:ys.append(float(y))
 ys=np.unique(np.round(ys,6));assert len(ys)>=2,(x,ys)
 # Legacy material cells have internal triangle seams: the exterior pair
 # bounds the physical 320 mm wall, intermediate hits are internal skins.
 yy=np.array([ys.min(),ys.max()]);assert .30<yy[1]-yy[0]<.35,(x,ys)
 return yy
XX=np.linspace(3.2501,10.7999,160);YS=np.array([faces(x)for x in XX]);CC=YS.mean(1)
def center(x):
 if x<XX[0]:return float(CC[0]+(CC[1]-CC[0])*(x-XX[0])/(XX[1]-XX[0]))
 if x>XX[-1]:return float(CC[-1]+(CC[-1]-CC[-2])*(x-XX[-1])/(XX[-1]-XX[-2]))
 return float(np.interp(x,XX,CC))
def h(x,v):
 """v is signed transverse offset from the measured wall centre (metres)."""
 u=abs((x-7.025)/4.075);a=min(1.,abs(v/HY));z=3.87+.37*u**4-.25*a**1.4+.40*u**8*a**3
 t=(JL-x)/(JL-X0)if x<JL else(x-JR)/(X1-JR)if x>JR else 0
 if t>0:
  uj=abs((JL-7.025)/4.075);arm=3.87+.37*uj**4+.36*t*t
  # The triangular end fan is a continuous hip plane, gently crowned across
  # its width. It must not form a deep W-shaped valley between the forks.
  if a<=t:z=arm+.012*t*(1-(a/max(t,1e-10))**2)
  else:
   edge=3.62+.73*u**6;f=(a-t)/max(1-t,1e-10);z=arm+(edge-arm)*f**1.25
 return z
def B(x):return min(h(x,v)for v in np.linspace(-HY,HY,41))-.255
def pos(x,v,z):return [x,center(x)+v,z]
def patch(xs,vs,zfn,thick):
 ny=len(vs);V=[pos(x,v,zfn(x,v))for x in xs for v in vs];N=len(V);V+= [[x,y,z-thick]for x,y,z in V];F=[]
 for i in range(len(xs)-1):
  for j in range(ny-1):
   a=i*ny+j;b=a+ny;F.extend([(a,b,b+1),(a,b+1,a+1),(a+N,b+1+N,b+N),(a+N,a+1+N,b+1+N)])
 ring=list(range(ny))+[(i+1)*ny-1 for i in range(1,len(xs))]+list(range((len(xs)-1)*ny+ny-2,(len(xs)-1)*ny-1,-1))+[i*ny for i in range(len(xs)-2,0,-1)]
 for a,b in zip(ring,ring[1:]+ring[:1]):F.extend([(a,b+N,a+N),(a,b,b+N)])
 return solid(V,F,'parametric roof patch')
def loft(xs,profile):
 # profile is an ordered cross-section in (transverse offset, elevation).
 n=len(profile(xs[0]));V=[];F=[]
 for x in xs:V.extend(pos(x,v,z)for v,z in profile(x))
 for j in range(len(xs)-1):
  for k in range(n):
   a=j*n+k;b=j*n+(k+1)%n;c=(j+1)*n+(k+1)%n;d=(j+1)*n+k;F.extend([(a,b,c),(a,c,d)])
 # Triangulate both end caps through manifold CrossSection, preserving rings.
 for j,rev in [(0,True),(len(xs)-1,False)]:
  p=profile(xs[j]);cs=mf.CrossSection([np.array(orient(Polygon(p),1).exterior.coords)[:-1]]).extrude(.01).to_mesh64();vv=np.asarray(cs.vert_properties);ff=np.asarray(cs.tri_verts);top=vv[ff][:,:,2].min(1)>.009;inds={}
  for t in ff[top]:
   face=[]
   for ii in t:
    pp=vv[ii,:2];kk=int(np.argmin(np.linalg.norm(np.array(p)-pp,axis=1)));assert np.linalg.norm(np.array(p)[kk]-pp)<1e-5;face.append(j*n+kk)
   # End faces point opposite to the path direction on the first end.
   F.append(tuple(face[::-1]if rev else face))
 return solid(V,F,'longitudinal stepped loft')
def tube(points,r=.03,sides=12):
 pts=np.array(points);V=[];F=[]
 for j,p in enumerate(pts):
  z=pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)];z/=np.linalg.norm(z);a=np.cross(z,[0.,1.,0.])
  if np.linalg.norm(a)<.1:a=np.cross(z,[1.,0.,0.])
  a/=np.linalg.norm(a);b=np.cross(z,a)
  for k in range(sides):V.append(p+r*(a*math.cos(k*math.tau/sides)+b*math.sin(k*math.tau/sides)))
 for j in range(len(pts)-1):
  for k in range(sides):a=j*sides+k;b=j*sides+(k+1)%sides;c=b+sides;d=a+sides;F.extend([(a,b,c),(a,c,d)])
 for k in range(1,sides-1):F.extend([(0,k+1,k),((len(pts)-1)*sides,(len(pts)-1)*sides+k,(len(pts)-1)*sides+k+1)])
 return solid(V,F,'continuous ceramic roll')
def cover(axis,c,a,b):
 V=[];F=[];n=11;steps=4
 for j in range(steps):
  s=a+(b-a)*j/(steps-1);x,v=(c,s)if axis=='Y'else(s,c);eps=.0001;dz=((h(x,v+eps)-h(x,v-eps))if axis=='Y'else(h(x+eps,v)-h(x-eps,v)))/(2*eps);t=np.array([0.,1.,dz])if axis=='Y'else np.array([1.,0.,dz]);t/=np.linalg.norm(t);lat=np.array([1.,0.,0.])if axis=='Y'else np.array([0.,1.,0.]);normal=np.cross(t,lat)
  if normal[2]<0:normal=-normal
  normal/=np.linalg.norm(normal);p=np.array(pos(x,v,h(x,v)-.003))
  for r in [.050,.040]:
   for k in range(n):an=k*math.pi/(n-1);V.append(p+r*(lat*math.cos(an)+normal*math.sin(an)))
 for j in range(steps-1):
  A=j*2*n;bb=(j+1)*2*n
  for k in range(n-1):F.extend([(A+k,A+k+1,bb+k+1),(A+k,bb+k+1,bb+k),(A+n+k,bb+n+k,bb+n+k+1),(A+n+k,bb+n+k+1,A+n+k+1)])
  F.extend([(A,bb,bb+n),(A,bb+n,A+n),(A+n-1,A+2*n-1,bb+2*n-1),(A+n-1,bb+2*n-1,bb+n-1)])
 for j in [0,steps-1]:
  A=j*2*n
  for k in range(n-1):
   f=(A+k,A+n+k,A+n+k+1,A+k+1)
   if j==0:f=f[::-1]
   F.extend([(f[0],f[1],f[2]),(f[0],f[2],f[3])])
 return solid(V,F,'closed barrel tile')
def compose(ms):return mf.Manifold.compose(ms)
def prepare_screen():
 p='SITE_SOUTH_SCREENWALL_';xs=np.linspace(X0,X1,161)
 put(p+'CURVED_TILE_SHELL_Geometry',patch(xs,np.linspace(-HY,HY,33),lambda x,v:h(x,v)-.025,.046),CERAMIC)
 tiles=[];rows=np.linspace(X0+.075,X1-.075,60);fan_count=0
 for i,x in enumerate(rows):
  t=max(0,(JL-x)/(JL-X0)if x<JL else(x-JR)/(X1-JR)if x>JR else 0);start=HY*t+.035
  for sg in [-1,1]:
   if HY-start<.065:continue
   num=max(1,math.ceil((HY-start)/.245))
   for j in range(num):
    a,b=sorted([sg*(start+(HY-start)*j/num),sg*(start+(HY-start)*(j+1)/num)]);tiles.append(cover('Y',x,a+.0015,b-.0015))
    cx=x+.067
    if cx<X1-.03:tiles.append(patch(np.linspace(cx-.060,cx+.060,7),[a+.0015,(a+b)/2,b-.0015],lambda xx,v,c=cx:h(xx,v)-.020+.015*((xx-c)/.06)**2,.008))
 for xe,xj in [(X0,JL),(X1,JR)]:
  for v in np.linspace(-HY+.07,HY-.07,9):
   xb=xj+(xe-xj)*abs(v/HY);aa,bb=sorted([xe,xb]);aa+=.012;bb-=.05
   if bb-aa<.06:continue
   num=max(1,math.ceil((bb-aa)/.24))
   for j in range(num):
    a=aa+(bb-aa)*j/num+.002;b=aa+(bb-aa)*(j+1)/num-.002;tiles.append(cover('X',v,a,b));fan_count+=1
    cy=v+.065
    if abs(cy)<HY-.03:tiles.append(patch([a,(a+b)/2,b],np.linspace(cy-.058,cy+.058,7),lambda x,v,c=cy:h(x,v)-.021+.014*((v-c)/.058)**2,.008))
 put(p+'BARREL_TILE_ROWS_Geometry',compose(tiles),CERAMIC)
 # Thin closed profiles, centred on the wall, with a real continuous bearing
 # stem down to the native wall crown. No remote wide soffit hanging aside.
 xx=np.linspace(3.25,10.80,161)
 def profile(x):
  b=B(x);v=[(-.155,3.085),(.155,3.085),(.155,b),(.22,b),(.22,b+.06),(.33,b+.06),(.33,b+.12),(.55,b+.12),(.55,h(x,.55)-.058)]
  v+=[(float(t),h(x,t)-.058)for t in np.linspace(.55,-.55,25)[1:]]
  v +=[(-.55,b+.12),(-.33,b+.12),(-.33,b+.06),(-.22,b+.06),(-.22,b),(-.155,b)]
  return v
 put(p+'V12_STEPPED_MASONRY_UNDEREAVE_Geometry',loft(xx,profile),TRIM)
 # End-fan eave apron is kept thin outside the load-bearing wall ends.
 fascia=[]
 for sg in [-1,1]:fascia.append(loft(xs,lambda x,s=sg:[(s*.551,h(x,s*.551)-.065),(s*.661,h(x,s*.661)-.065),(s*.661,h(x,s*.661)-.112),(s*.551,h(x,s*.551)-.112)]))
 for a,b in [(X0,3.25),(10.80,X1)]:fascia.append(patch(np.linspace(a,b,14),np.linspace(-.66,.66,31),lambda x,v:h(x,v)-.065,.045))
 put(p+'V12_CLOSED_EAVE_FASCIA_Geometry',compose(fascia),'M_V24_09_Screenwall_Gray_Moulding')
 edges=[];beds=[];forks=[];tips=[]
 for sg in [-1,1]:edges.append(tube([pos(x,sg*(HY+.006),h(x,sg*HY)-.012)for x in xs],.026))
 for xe,xj,sign in [(X0,JL,-1),(X1,JR,1)]:
  for sg in [-1,1]:
   path=[pos(xj+(xe-xj)*t,sg*HY*t,h(xj+(xe-xj)*t,sg*HY*t)+.050)for t in np.linspace(0,1,33)];forks.append(path);edges.append(tube(path,.035));beds.append(tube([[x,y,z-.035]for x,y,z in path],.047))
   base=np.array(path[-1]);direction=np.array([sign*.90,sg*HY]);direction/=np.linalg.norm(direction);prof=[(-.28,base[2]-.060),(-.18,base[2]-.005),(-.10,base[2]+.085),(-.045,base[2]+.22),(0,base[2]+.375),(.028,base[2]+.380),(.050,base[2]+.015),(.095,base[2]-.060)];tips.append(vertical_profile(prof,base[:2],base[:2]+direction,.073))
  edges.append(tube([pos(xe,v,h(xe,v)-.010)for v in np.linspace(-HY,HY,41)],.026))
 put(p+'CURVED_EAVE_AND_RIDGE_BORDER_Geometry',compose(edges),CERAMIC)
 beds.append(patch(np.linspace(JL,JR,101),[-.046,0,.046],lambda x,v:h(x,v)+.023,.063));put('V24_09_Screenwall_Solid_Fork_and_Ridge_Seats',compose(beds),CERAMIC)
 put(p+'V12_HIGH_RIDGE_FINIALS_Geometry',compose(tips),CERAMIC)
 lattice=[];L=JR-JL
 for z,r in [(.034,.023),(.153,.028)]:lattice.append(tube([pos(x,0,h(x,0)+z)for x in np.linspace(JL,JR,101)],r))
 for i in range(48):
  cx=JL+L*(i+.5)/48;pitch=L/48;points=[(cx-pitch*.48,.092),(cx,.137),(cx+pitch*.48,.092),(cx,.047),(cx-pitch*.48,.092)]
  lattice.append(tube([pos(x,0,h(x,0)+z)for x,z in points],.007,8))
 put(p+'OPEN_RIDGE_LATTICE_Geometry',compose(lattice),CERAMIC)
 # Preserve the actual lotus detail in a repeated array, now on the corrected
 # long eaves. Original pieces retain orientation and scale, never stretched.
 ref=json.loads((W/'v12_screenwall_reference/Mutation.json').read_text());templates=next(r for r in ref['add']if r['name']=='SITE_SOUTH_SCREENWALL_V12_LOTUS_DRIP_ENDS')['parts'][:9];axis=np.array(templates[0]['drip_disk_axis']);disks=[]
 for x in rows:
  slope=(center(x+.005)-center(x-.005))/.01;tangent=np.array([1.,slope]);tangent/=np.linalg.norm(tangent);normal=np.array([-tangent[1],tangent[0]])
  for sg in [-1,1]:
   target=np.array(pos(x,sg*(HY+.018),h(x,sg*HY)-.003))
   for part in templates:
    vv=(np.array(part['geometry']['vertices'])-axis)*.82
    if sg>0:vv[:,1]*=-1
    vv[:,:2]=vv[:,0,None]*tangent+vv[:,1,None]*normal;vv+=target;ff=part['geometry']['faces']
    if sg>0:ff=[face[::-1]for face in ff]
    # Reference polygons are triangulated for the independent closed-mesh test.
    ff=np.array([[f[0],f[k],f[k+1]]for f in ff for k in range(1,len(f)-1)])
    disks.append(solid(vv,ff,'lotus petal'))
 put(p+'V12_LOTUS_DRIP_ENDS_Geometry',compose(disks),CERAMIC)
 enddisks=[]
 for xe,sg in [(X0,-1),(X1,1)]:
  for v in np.linspace(-HY+.07,HY-.07,9):enddisks.append(rod(pos(xe-sg*.008,v,h(xe,v)+.003),pos(xe+sg*.023,v,h(xe,v)+.003),.043,20))
 put('V24_14_Screenwall_Hip_Fan_Tile_End_Disks',compose(enddisks),'M_V24_09_Screenwall_Ceramic_1')
 # Frieze and end panels now follow the very same wall centre and bearing.
 panels=[];frames=[];triangles=[];endpan=[];endframes=[]
 for sg in [-1,1]:
  panels.append(loft(xx,lambda x,s=sg:[(s*.159,B(x)-.34),(s*.173,B(x)-.34),(s*.173,B(x)-.085),(s*.159,B(x)-.085)]))
  x=3.39
  for width in [1.45,.34,1.45,.34,1.45,.34,1.45]:
   a=x;b=x+width;x=b+.075
   for dz in [-.315,-.110]:frames.append(tube([pos(t,sg*.180,B(t)+dz)for t in np.linspace(a,b,max(3,int(width/.06)))],.012,8))
   for t in [a,b]:frames.append(rod(pos(t,sg*.180,B(t)-.315),pos(t,sg*.180,B(t)-.110),.012,8))
  for x in np.arange(3.30,10.75,.10):
   points=[pos(x,sg*.178,B(x)-.070),pos(x+.045,sg*.178,B(x+.045)-.040),pos(x+.09,sg*.178,B(x+.09)-.070)]
   for a,b in zip(points,points[1:]):triangles.append(rod(a,b,.006,8))
 for x,sg in [(3.25,-1),(10.80,1)]:
  cy=center(x);z=B(x);endpan.append(cube([x-.008,cy-.127,z-.32],[x+.008,cy+.127,z-.095]))
  for y in [cy-.145,cy+.145]:endframes.append(beam([x+sg*.018,y,z-.34],[x+sg*.018,y,z-.075],.020,.025))
  for zz in [z-.34,z-.075]:endframes.append(beam([x+sg*.018,cy-.145,zz],[x+sg*.018,cy+.145,zz],.025,.020))
 for n,ms,mat in [('Curved_Panel_Backings',panels,'M_V24_09_Screenwall_Pale_Panel'),('Long_Short_Moulded_Frames',frames,'M_V24_09_Screenwall_Gray_Moulding'),('Triangular_Frieze',triangles,'M_V24_09_Screenwall_Gray_Moulding'),('End_Panel_Stone_Frames',endframes,'M_V24_09_Screenwall_Gray_Moulding'),('White_End_Inset_Panels',endpan,WHITE)]:put('V24_09_Screenwall_'+n,compose(ms),mat)
 # Re-centre the complete stepped foot, including both sides of the wall.
 plinth=[]
 for hw,z0,z1 in [(.40,-.70,-.55),(.34,-.55,-.29),(.38,-.29,-.23)]:plinth.append(loft(np.linspace(3.17,10.88,161),lambda x,w=hw,a=z0,b=z1:[(-w,a),(w,a),(w,b),(-w,b)]))
 put('V24_11_Screenwall_Continuous_Stepped_Stone_Plinth',union(plinth),'M_V24_11_Screenwall_Dressed_Stone')
 OUT['proof']['screen']={'centreline_source':'actual two faces of saved native wall at Z=1; midpoint sampled before changes','centerline_xy':[[float(x),float(y)]for x,y in zip(XX,CC)],'wall_sections':[[float(x),*map(float,faces(x))]for x in [3.5,7.,10.5]],'maximum_previous_roof_axis_offset_m':float(max(abs(CC+16.9))),'roof_half_width_m':HY,'fork_junction_x':[JL,JR],'fork_arms':4,'fan_barrel_tiles':fan_count,'end_fan_slight_cross_crown_m':.012,'no_deep_end_valley':True,'ridge_diamond_panels':48,'wall_crown_new_z':3.10,'continuous_bearing_stem_bottom_z':3.085,'load_path':'wall and plinth centre / continuous masonry stem / three centred corbel steps / closed roof and fork beds','end_panel_centred':True,'short_end_fan_instead_of_disconnected_needle_posts':True,'centerline_is_model_geometry_not_new_field_measurement':True}
