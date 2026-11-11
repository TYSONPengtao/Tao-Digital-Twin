from v24_26_common import *
from shapely.geometry import box,Point
from shapely.ops import unary_union

MAT='M_V24_20_Unified_Weathered_Gray_Clay';BRICK='M_V24_18_Continuous_Blue_Brick'
OUT['recolor']=[{'name':'V24_24_Kitchen_North_Veranda_White_Closure','material':BRICK}]
OUT['proof']['brick_closure']={'reference':'210452','object':OUT['recolor'][0]['name'],'material':BRICK,'geometry_unchanged':True,'matches_adjacent_kitchen_brick':True}

# Short verge on the storage-facing south end, preserving the two actual roof
# pitches, north end, roof course phase and every storage roof component.
FRONT=-11.85;cut=cube([7.0,-13.,2.0],[15.5,FRONT,5.5]);roof_changes=[]
for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','V24_20_Kitchen_Unified_Pan_Barrel_Slope_0','V24_25_Kitchen_East_Unified_Pan_Barrel_Field','V24_Kitchen_Curved_Gable_Coping']:
 old=load(n);m=old-cut
 m=compose([p for p in m.decompose()if p.volume()>1e-9]);put(n,m,MAT,transfer=True)
 roof_changes.append({'name':n,'removed_volume_m3':old.volume()-m.volume(),'new_front_limit_y':FRONT})
# The ear outline seats on the same shortened grey verge, rather than floating
# ahead of the new tile edge. Its profile, central axis and height are retained.
for i in [1,2,3]:
 n=f'V24_19_Kitchen_South_Faceted_Head_Frame_{i}';put(n,load(n).translate([0,.14,0]),INDEX[n]['materials'][0],transfer=True)
OUT['proof']['kitchen_verge']={'reference':['210606','210832'],'wall_front_y_m':-11.73,'old_tile_front_y_m':-12.13,'new_tile_front_y_m':FRONT,'projection_before_m':.40,'projection_after_m':.12,'trimmed_objects':roof_changes,'south_ear_reseat_y_m':.14,'storage_roof_unchanged':True,'roof_planes_and_global_tile_grid_unchanged':True}

# Substantial tiled coping on the existing L-shaped inner courtyard wall.
# Existing core, face frames and brickwork remain in place. Each roof part is
# cut at one shared 45-degree mitre, with matching levels at the corner.
CY=-11.582;END=4.904;HALF=.45;R=.068;PITCH=.18;COLLAR=.55
CHAIN='SITE_COURTYARD_WEST_TILE_WALL'
class Seg:
 def __init__(self,a,b,za,zb,j):
  self.a=np.array(a,float);self.b=np.array(b,float);self.u=(self.b-self.a)/np.linalg.norm(self.b-self.a);self.n=np.array([-self.u[1],self.u[0]]);self.L=np.linalg.norm(self.b-self.a);self.za=za;self.zb=zb;self.j=j
 def crown(self,s):
  if self.j==0:return self.za+(self.zb-self.za)*max(0,min(1,s/(self.L-COLLAR)))
  return self.za+(self.zb-self.za)*max(0,min(1,(s-COLLAR)/(self.L-COLLAR)))
 def xyz(self,s,d,z):return [*(self.a+self.u*s+self.n*d),float(z)]
 def map(self,m):
  q=m.to_mesh64();v=np.array(q.vert_properties[:,:3]);f=np.array(q.tri_verts);v=np.array([self.xyz(s,d,self.crown(s)+z)for s,z,d in v]);return solid(v,f)
 def mask(self):
  if self.j==0:q=[(0,-HALF),(self.L+HALF,-HALF),(self.L-HALF,HALF),(0,HALF)]
  else:q=[(-HALF,-HALF),(self.L,-HALF),(self.L,HALF),(HALF,HALF)]
  p=[self.xyz(s,d,0)[:2]for s,d in q];return section(p,3).translate([0,0,1.8])
 def slice_stations(self):return [0.,self.L-COLLAR,self.L]if self.j==0 else [0.,COLLAR,self.L]

segs=[Seg([0,1.9],[0,CY],2.0649414,2.0251465,0),Seg([0,CY],[END,CY],2.0251465,2.07063,1)]
parts={k:[]for k in ['TILE_COPING','V10_COVER_TILES','V10_PAN_TILES','V10_LOTUS_DRIP_ENDS','V10_OPEN_FLOWER_BRICKS','V10_RIDGE_SEAT_AND_CAP']};counts={k:0 for k in parts};hole_probes=[]

def loft_strip(sg,d0,d1,upper,lower):
 stations=sg.slice_stations();stations[0]-=HALF+.01 if sg.j==1 else 0;stations[-1]+=HALF+.01 if sg.j==0 else 0
 vs=[];fs=[]
 for s in stations:vs +=[sg.xyz(s,d,sg.crown(s)+z)for d,z in [(d0,lower(d0)),(d1,lower(d1)),(d1,upper(d1)),(d0,upper(d0))]]
 for i in range(len(stations)-1):
  for j in range(4):a=i*4+j;b=i*4+(j+1)%4;c=b+4;d=a+4;fs.extend([(a,b,c),(a,c,d)])
 fs +=[(3,2,1),(3,1,0)];a=(len(stations)-1)*4;fs +=[(a,a+1,a+2),(a,a+2,a+3)]
 return solid(vs,np.array(fs))

def cover(sg,s,side,da,db):
 us=np.linspace(-R,R,13);ds=[da,(da+db)/2,db];vs=[];fs=[]
 for low in [False,True]:
  for d in ds:
   for u in us:
    z=.32-.64*d+math.sqrt(max(0,R*R-u*u))+.006*(db-d)/(db-da)-( .012 if low else 0)
    vs.append(sg.xyz(s+u,side*d,sg.crown(s+u)+z))
 N=len(us);M=len(ds);K=N*M
 for j in range(M-1):
  for i in range(N-1):a=j*N+i;b=a+N;fs.extend([(a,b,b+1),(a,b+1,a+1),(a+K,a+1+K,b+1+K),(a+K,b+1+K,b+K)])
 rim=list(range(N))+[j*N+N-1 for j in range(1,M)]+list(range(K-2,K-N-1,-1))+[j*N for j in range(M-2,0,-1)]
 for a,b in zip(rim,rim[1:]+rim[:1]):fs.extend([(a,b,b+K),(a,b+K,a+K)])
 return solid(vs,np.array(fs))

def pan(sg,s,side,da,db):
 us=np.linspace(-.067,.067,9);vs=[];fs=[]
 for low in [False,True]:
  for d in [da,db]:
   for u in us:vs.append(sg.xyz(s+u,side*d,sg.crown(s+u)+.311-.64*d+.008*(u/.067)**2-(.012 if low else 0)))
 N=len(us);K=N*2
 for i in range(N-1):fs.extend([(i,i+N,i+N+1),(i,i+N+1,i+1),(i+K,i+1+K,i+1+N+K),(i+K,i+1+N+K,i+N+K)])
 rim=list(range(N))+list(range(2*N-1,N-1,-1))
 for a,b in zip(rim,rim[1:]+rim[:1]):fs.extend([(a,b,b+K),(a,b+K,a+K)])
 return solid(vs,np.array(fs))

def lotus(sg,s,side):
 rad=.077;N=32;ring=[.012,.028,.047,.064,.077];vs=[sg.xyz(s,side*(HALF+.010),sg.crown(s)+.062)];fs=[]
 for r in ring:
  for i in range(N):
   t=2*math.pi*i/N;rr=r*(1+.025*(r/rad)**3*math.cos(8*t));rel=.0045*(.5+.5*math.cos(8*t))*math.sin(math.pi*r/rad)**2
   vs.append(sg.xyz(s+rr*math.cos(t),side*(HALF+.005+rel),sg.crown(s)+.062+rr*math.sin(t)))
 back=len(vs);vs.append(sg.xyz(s,side*(HALF-.014),sg.crown(s)+.062));bs=len(vs)
 for i in range(N):t=2*math.pi*i/N;rr=rad*(1+.025*math.cos(8*t));vs.append(sg.xyz(s+rr*math.cos(t),side*(HALF-.014),sg.crown(s)+.062+rr*math.sin(t)))
 fs +=[(0,1+i,1+(i+1)%N)for i in range(N)]
 for j in range(len(ring)-1):
  a=1+j*N;b=a+N
  for i in range(N):I=(i+1)%N;fs.extend([(a+i,b+i,b+I),(a+i,b+I,a+I)])
 a=1+(len(ring)-1)*N
 for i in range(N):I=(i+1)%N;fs.extend([(a+i,bs+i,bs+I),(a+i,bs+I,a+I),(back,bs+I,bs+i)])
 return solid(vs,np.array(fs))

def flower(sg,start,end):
 p=box(start,.350,end,.550);holes=[]
 for i in range(math.floor(start/.24)-1,math.ceil(end/.24)+1):
  cx=.12+i*.24;cz=.45
  q=unary_union([Point(cx+dx,cz+dz).buffer(.024,quad_segs=8)for dx,dz in [(0,0),(.023,0),(-.023,0),(0,.023),(0,-.023)]])
  holes.append(q);holes.append(Polygon([(cx+.12-.052,cz),(cx+.12,cz+.066),(cx+.12+.052,cz),(cx+.12,cz-.066)]))
  if start+.08<cx<end-.08:hole_probes.append({'point':sg.xyz(cx,0,sg.crown(cx)+cz),'direction':[*sg.n,0]})
 p=p.difference(unary_union(holes));ms=[]
 for q in [p]if p.geom_type=='Polygon'else p.geoms:
  if q.area<1e-10:continue
  m=section(list(q.exterior.coords)[:-1],.11)
  for h in q.interiors:m=m-section(list(h.coords)[:-1],.13).translate([0,0,-.01])
  ms.append(sg.map(m.translate([0,0,-.055])))
 return union(ms)

for sg in segs:
 mask=sg.mask();lo=-HALF-.01 if sg.j==1 else 0;hi=sg.L+HALF+.01 if sg.j==0 else sg.L
 bedding=union([loft_strip(sg,-HALF,0,lambda d:.31+.64*d,lambda d:.245+.64*d),loft_strip(sg,0,HALF,lambda d:.31-.64*d,lambda d:.245-.64*d),loft_strip(sg,-.17,0,lambda d:.246+.64*d,lambda d:-.04),loft_strip(sg,0,.17,lambda d:.246-.64*d,lambda d:-.04)])^mask
 parts['TILE_COPING'].append(bedding)
 for s in np.arange(math.floor(lo/PITCH)*PITCH+.09,hi+.09,PITCH):
  for side in [-1,1]:
   for a,b in [(.055,.26),(.245,HALF)]:parts['V10_COVER_TILES'].append(cover(sg,float(s),side,a,b))
   parts['V10_LOTUS_DRIP_ENDS'].append(lotus(sg,float(s),side))
 for s in np.arange(math.floor(lo/PITCH)*PITCH,hi+.10,PITCH):
  for side in [-1,1]:
   for a,b in [(.055,.26),(.245,HALF)]:parts['V10_PAN_TILES'].append(pan(sg,float(s),side,a,b))
 # Split at the level mitre collar so all extrusion faces remain planar.
 breaks=[lo]+[s for s in sg.slice_stations()[1:-1]if lo<s<hi]+[hi]
 for a,b in zip(breaks,breaks[1:]):parts['V10_OPEN_FLOWER_BRICKS'].append(flower(sg,a,b)^mask)
 seats=[loft_strip(sg,-.09,.09,lambda d:.350,lambda d:.306),loft_strip(sg,-.080,.080,lambda d:.563,lambda d:.548)]
 # Rounded ridge cap, short separate courses with visible narrow joints.
 ts=np.linspace(0,math.pi,15);profile=[(-.075,.555),(.075,.555)]+[(.075*math.cos(t),.555+.075*math.sin(t))for t in ts]
 for a in np.arange(math.floor(lo/.40)*.40,hi,.40):
  b=min(a+.398,hi)
  if b<=a:continue
  m=section(profile,b-a);q=m.to_mesh64();v=np.array(q.vert_properties[:,:3]);f=np.array(q.tri_verts);vv=[sg.xyz(a+s,d,sg.crown(a+s)+z)for d,z,s in v];seats.append(solid(vv,f))
 parts['V10_RIDGE_SEAT_AND_CAP'].append(compose(seats)^mask)
 # Clip curved cover/pan/disc units only once for the whole field at the mitre.
 for key in ['V10_COVER_TILES','V10_PAN_TILES','V10_LOTUS_DRIP_ENDS']:
  take=parts[key];parts[key]=[]
  # Previous segment has already been reduced to one clipped manifold.
  prior=take[:counts[key]];new=take[counts[key]:];parts[key]=prior+[(compose(new)^mask)];counts[key]=len(parts[key])

for key,ms in parts.items():
 m=compose(ms);m=compose([c for c in m.decompose()if c.volume()>1e-10]);put(CHAIN+'_'+key+'_Geometry',m,MAT)
OUT['proof']['courtyard_coping']={'reference':['DJI_0095.JPG','211022','211048'],'existing_wall_core_and_panel_frames_unchanged':True,'centerline_xy':[[0,1.9],[0,CY],[END,CY]],'roof_full_width_before_m':.410,'roof_full_width_after_m':.900,'projection_each_side_from_250mm_wall_m':.325,'tile_bedding_thickness_m':.065,'barrel_tile_radius_m':R,'tile_pitch_m':PITCH,'tile_courses_per_half':2,'lotus_diameter_m':.154,'open_flower_and_diamond_height_m':.200,'ridge_cap_top_above_wall_m':.630,'through_openwork_depth_m':.110,'shared_45_degree_mitre':True,'hole_probes':hole_probes,'gate_clearance_x_m':4.909333-END,'dimension_status':'PHOTO_PROPORTION_FIT'}
write();print('V26_GEOMETRY_READY',len(OUT['objects']),flush=True)
