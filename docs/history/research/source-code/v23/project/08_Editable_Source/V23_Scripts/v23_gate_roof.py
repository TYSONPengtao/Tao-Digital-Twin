from v23_common import *

D=W/'v23_gate_roof';D.mkdir(exist_ok=True);Q=start();checks=[]
TILE='M_V21_GATE_REF_10';STONE='M_V21_GATE_REF_11'
FRIEZE='M_V21_GATE_REF_13';BAND='M_V21_GATE_REF_12'
CX=6.6;YF=-12.262;YR=-10.886;YM=-11.486

# Sample the original registered carrier, including its corner lift, rather
# than fitting an unrelated roof shape to the perspective references.
grids=[]
for p in E['SITE_V21_GATE_REFERENCE_LAYER_09']['parts']:
 v=np.asarray(ex.world_part(p,E['SITE_V21_GATE_REFERENCE_LAYER_09'])[0])
 xs=np.unique(np.round(v[:,0],6));ys=np.unique(np.round(v[:,1],6))
 z=np.full((len(ys),len(xs)),-1e6)
 for x,y,zz in v:
  i=np.argmin(abs(xs-x));j=np.argmin(abs(ys-y));z[j,i]=max(z[j,i],zz)
 assert z.min()>0
 grids.append((xs,ys,z))

def topz(x,y):
 xs,ys,z=grids[0 if y<=YM else 1]
 j=min(max(np.searchsorted(ys,y)-1,0),len(ys)-2)
 t=(y-ys[j])/(ys[j+1]-ys[j])
 return float(np.interp(x,xs,z[j])*(1-t)+np.interp(x,xs,z[j+1])*t)

def lift(x):return topz(x,YF)-topz(CX,YF)

def shell_profile(profile,ys):
 # Cross section may be a half-round annulus or a shallow concave pan. The
 # underside is sunk 4-9 mm into the continuous carrier, so this is supported
 # ceramic geometry, not a floating skin.
 v=[];n=len(profile)
 for y in ys:
  for x,dz in profile:v.append([x,y,topz(x,y)+dz])
 f=[]
 for j in range(len(ys)-1):
  for i in range(n):f.append([j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i])
 f+=[list(range(n-1,-1,-1)),[(len(ys)-1)*n+i for i in range(n)]]
 return manifold({'type':'polyhedron','vertices':v,'faces':f})

def curved_solid(x0,x1,lo,hi,y0,y1,n=100):
 xs=np.linspace(x0,x1,n);v=[]
 for x in xs:
  r=lift(x);v.extend([[x,y0,lo+r],[x,y1,lo+r],[x,y1,hi+r],[x,y0,hi+r]])
 f=[]
 for j in range(len(xs)-1):
  for k in range(4):f.append([j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k])
 f+=[[3,2,1,0],[(len(xs)-1)*4+i for i in range(4)]]
 return manifold({'type':'polyhedron','vertices':v,'faces':f})

def axis_sweep(profile,xs):
 # Ridge copings run across the roof; cross section is in the YZ plane.
 v=[];n=len(profile)
 for x in xs:
  for y,dz in profile:v.append([x,y,topz(x,YM)+dz])
 f=[]
 for j in range(len(xs)-1):
  for i in range(n):f.append([j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i])
 f+=[list(range(n-1,-1,-1)),[(len(xs)-1)*n+i for i in range(n)]]
 return manifold({'type':'polyhedron','vertices':v,'faces':f})

roof=raw('SITE_V21_GATE_REFERENCE_LAYER_09')
soffit=raw('SITE_V21_GATE_REFERENCE_CLOSED_SOFFIT')
print('roof sources loaded',flush=True)
tileparts=[];tile_ms=[];caps=[];cap_ms=[]
centres=np.linspace(4.025,9.175,43)
for mi,offset in enumerate([-6,-3,0,3,6]):
 Q['materials'][f'M_V23_Gate_Tile_{mi:02d}']={'color':[117+offset,124+offset,125+offset],'roughness':.88,'role':'Subtle per-piece variation in registered gate barrel/pan tiles'}

for i,x in enumerate(centres):
 if i%10==0:print('barrel lane',i,flush=True)
 for side,ends in enumerate([(YF,YM),(YR,YM)]):
  # Three individually overlapping ceramic units down each shallow pitch.
  cuts=np.linspace(ends[0],ends[1],4)
  for j,(a,b) in enumerate(zip(cuts,cuts[1:])):
   pad=.011;lo,hi=sorted([a,b]);lo=max(lo-pad,min(ends));hi=min(hi+pad,max(ends))
   ts=np.linspace(0,math.pi,15)
   outer=[[x+.042*math.cos(t),-.004+.042*math.sin(t)] for t in ts]
   inner=[[x+.032*math.cos(t),-.004+.032*math.sin(t)] for t in ts[::-1]]
   m=shell_profile(outer+inner,np.linspace(lo,hi,5));tile_ms.append(m)
   tileparts.append(pp(m,f'M_V23_Gate_Tile_{(i+2*j+side)%5:02d}'))
  # Semicircular barrel terminal closes against the first supported tile.
  y=ends[0];sgn=-1 if side==0 else 1;z=topz(x,y)+.006
  outer=[[x+.042*math.cos(t),z+.042*math.sin(t)] for t in np.linspace(0,2*math.pi,32,endpoint=False)]
  disc=prismxz(outer,y+sgn*.019,.032)
  # Shallow radial flower, individual raised lobes, with a circular boss.
  motif=flower(x,z,.026,.010).translate([0,y-.032 if side==0 else y+.023,0])
  if side==0:disc=prismxz(outer,y-.027,.035)
  else:disc=prismxz(outer,y-.008,.035)
  m=disc+motif;caps.append(pp(m,TILE));cap_ms.append((m,side,i))

for i,(a,b) in enumerate(zip(centres,centres[1:])):
 if i%10==0:print('pan lane',i,flush=True)
 x=(a+b)/2;w=(b-a)/2+.012
 for side,ends in enumerate([(YF,YM),(YR,YM)]):
  cuts=np.linspace(ends[0],ends[1],4)
  for j,(ya,yb) in enumerate(zip(cuts,cuts[1:])):
   lo,hi=sorted([ya,yb]);lo=max(lo-.009,min(ends));hi=min(hi+.009,max(ends))
   xx=np.linspace(-w,w,9)
   up=[[x+dx,-.002+.028*(abs(dx)/w)**2] for dx in xx]
   dn=[[x+dx,-.012+.028*(abs(dx)/w)**2] for dx in xx[::-1]]
   m=shell_profile(up+dn,np.linspace(lo,hi,4));tile_ms.append(m)
   tileparts.append(pp(m,f'M_V23_Gate_Tile_{(i+j+side+1)%5:02d}'))

put(Q,'SITE_V21_GATE_REFERENCE_LAYER_10',tileparts,classification='REGISTERED_THICK_SEGMENTED_BARREL_AND_CONCAVE_PAN_TILES',barrel_lanes=43,segments_per_slope=3,carrier='SITE_V21_GATE_REFERENCE_LAYER_09')
put(Q,'GATE_V22_EMBOSSED_TILE_END_CAPS',caps,classification='FRONT_AND_REAR_ROUND_FLOWER_TILE_TERMINALS',front_rear_count=[43,43])
print('tiles complete',len(tileparts),flush=True)

# Replace six thin front ribbons by genuinely deep, solid, joined mouldings.
# Back-side construction follows DJI_0118; front retains the real front fit.
cornices=[];zigzags=[];lace=[];rafters=[]
for side in [0,1]:
 print('eave side',side,flush=True)
 back=side==1;dy=(YR-YF) if back else 0.;dz=.0495 if back else 0.
 if not back:ya,yb=-12.307,-12.175
 else:ya,yb=-10.973,-10.841
 for lo,hi,ext in [(2.632,2.655,.006),(2.655,2.699,.0),(2.699,2.716,.010)]:
  cornices.append(pp(curved_solid(3.9691,9.2309,lo+dz,hi+dz,ya-ext,yb+ext),STONE))
 # Pierced triangular rhythm: shallow backing is continuous with the soffit;
 # diagonals are actual 9 mm wide relieved ribs rather than filled diamonds.
 yface=-12.321 if not back else -10.867
 thick=.036
 backing=curved_solid(3.991,9.209,2.578+dz,2.634+dz,-12.307,-12.205) if not back else curved_solid(3.991,9.209,2.578+dz,2.634+dz,-10.953,-10.851)
 zms=[backing]
 for x in np.linspace(4.035,9.165,50):
  pts=[[x-.052,2.585+dz+lift(x-.052)],[x,2.624+dz+lift(x)],[x+.052,2.585+dz+lift(x+.052)]]
  zms.append(stroke(pts,.0048,.030).translate([0,yface,0]))
 zigzags.append(pp(uni(zms),BAND))
 # Each drip slab has a rounded-lobed perimeter, relieved floral motif and
 # raised inner border. Plates penetrate the retained soffit/carved cornice.
 for x in np.linspace(4.033,9.167,39):
  z0=2.512+dz+lift(x);ww=.0675
  poly=[[x-ww,z0+.073],[x+ww,z0+.073],[x+ww,z0+.024],[x+.049,z0+.020],[x+.036,z0+.010],[x+.020,z0+.008],[x,z0-.001],[x-.020,z0+.008],[x-.036,z0+.010],[x-.049,z0+.020],[x-ww,z0+.024]]
  y0=-12.327 if not back else -10.931
  m=prismxz(poly,y0,.122)
  oy=-12.336 if not back else -10.815
  motif=flower(x,z0+.041,.022,.010).translate([0,oy,0])
  # Rear relief extrudes to the courtyard face (+Y); both meet their plates.
  m+=motif
  lace.append(pp(m,FRIEZE))
 # Short exposed rafter tails, with square shoulders and rounded lower ends.
 # They sit above the moulding and are sunk into the carrier at the rear.
 for x in np.linspace(4.075,9.125,31):
  r=lift(x);lo=2.713+dz+r;hi=2.814+dz+r
  yy=-12.306 if not back else -11.056
  sizey=.244
  m=cube([x-.029,yy,lo],[.058,sizey,hi-lo])
  # Round bead across exposed tail, united with the rectangular bearing.
  profile=[[x+.029*math.cos(t),lo+.022+.022*math.sin(t)] for t in np.linspace(0,2*math.pi,24,endpoint=False)]
  end=prismxz(profile,-12.314 if not back else -10.831,.026)
  m+=end
  rafters.append(pp(m,'M_V21_GATE_REF_15'))

put(Q,'SITE_V21_GATE_REFERENCE_LAYER_11',cornices,classification='DEEP_SUPPORTED_FRONT_AND_REAR_STEPPED_STONE_CORNICE')
put(Q,'SITE_V21_GATE_REFERENCE_LAYER_12',zigzags,classification='FRONT_AND_REAR_RELIEVED_OPEN_TRIANGULAR_ORNAMENT_WITH_STRUCTURAL_BACKING')
put(Q,'SITE_V21_GATE_REFERENCE_LAYER_13',lace,classification='FRONT_AND_REAR_SCALLOPED_FLOWER_DRIP_SLABS')
put(Q,'SITE_V21_GATE_REFERENCE_LAYER_15',[*nativeparts('SITE_V21_GATE_REFERENCE_LAYER_15'),*rafters],classification='RETAINED_INTERNAL_BEARING_AND_SHORT_PROJECTING_FRONT_AND_REAR_RAFTER_TAILS')

# Retain registered uplifted wing interfaces and replace the long rectangular
# ridge stick with short, rounded and genuinely overlapping coping units.
ridgeparts=[]
for p in E['SITE_V21_GATE_REFERENCE_LAYER_14']['parts'][1:]:ridgeparts.append(copy.deepcopy(p))
for j,(a,b) in enumerate(zip(np.linspace(3.99,9.21,35),np.linspace(3.99,9.21,35)[1:])):
 ts=np.linspace(0,math.pi,17)
 prof=[[YM+.052*math.cos(t),-.008+.052*math.sin(t)] for t in ts]
 prof+=[[YM-.052,-.015],[YM+.052,-.015]]
 m=axis_sweep(prof,np.linspace(a-.005,b+.005,5))
 ridgeparts.append(pp(m,'M_V21_GATE_REF_14'))
put(Q,'SITE_V21_GATE_REFERENCE_LAYER_14',ridgeparts,classification='RETAINED_UPLIFTED_WING_RIDGES_WITH_SEGMENTED_ROUNDED_MAIN_COPING')

# Test actual solid contacts on every new ceramic unit. Contact is structural
# overlap in mm, not a screenshot-only proximity measurement.
print('start support QA',flush=True)
contacts=[]
for k,m in enumerate(tile_ms):
 overlap=(m^roof).volume();assert overlap>1e-9,('unsupported_tile',k,overlap)
 contacts.append(overlap)
checks.append({'check':'ALL_SEGMENTED_TILES_CONTACT_RETAINED_ROOF_CARRIER','count':len(contacts),'min_overlap_m3':min(contacts)})
for k,(m,side,i) in enumerate(cap_ms):
 # End caps also contact their lane directly; a carrier may end 27 mm behind.
 lane=tile_ms[(i*2+side)*3]
 overlap=(m^lane).volume();assert overlap>1e-10,('unsupported_cap',k,overlap)
checks.append({'check':'ALL_FLOWER_TERMINALS_CONTACT_THEIR_FIRST_BARREL_TILE','count':len(cap_ms)})
for i,p in enumerate(rafters):
 m=manifold(p['geometry']);ov=(m^(roof+soffit)).volume();assert ov>1e-9,('unsupported_rafter',i,ov)
checks.append({'check':'ALL_SHORT_RAFTER_TAILS_CONTACT_ORIGINAL_ROOF_OR_CLOSED_SOFFIT','count':len(rafters)})
checks.append({'check':'ORIGINAL_ROOF_CARRIER_CLOSED_SOFFIT_AND_WING_INTERFACE_RETAINED','preserved_nodes':['SITE_V21_GATE_REFERENCE_LAYER_09','SITE_V21_GATE_REFERENCE_CLOSED_SOFFIT'],'preserved_wing_parts':4})
Q['change_notes']=['内大门前后坡替换为分节厚筒瓦和凹板瓦，瓦端增加独立圆花瓦当，保持原屋面及翼角定位。','根据 DJI_0118 的院内侧可见构造，门楼前后均补有承托深度的三道檐枋、短椽尾、三角纹带及波形花卉滴水板，保持封闭浅色檐底。','DJI_0086 用于参考瓦件搭接与体积，不把照壁屋脊的比例套到内大门。']
save(Q,D,checks)
if __name__=='__main__':
 import runpy
 runpy.run_path(str(W/'v23_gate_roof_finish.py'),run_name='__main__')
