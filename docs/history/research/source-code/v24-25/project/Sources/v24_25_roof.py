from v24_25_common import *
from shapely.ops import unary_union
from shapely.geometry import box
OUT.update(json.loads((D/'Prepared_Geometry.json').read_text('utf8')))
roof_names={'SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','V24_20_Kitchen_Unified_Pan_Barrel_Slope_0','V24_25_Kitchen_East_Unified_Pan_Barrel_Field'}
OUT['objects']=[r for r in OUT['objects']if r['name']not in roof_names]
OUT['remove']=list(dict.fromkeys(OUT['remove']))
MAT='M_V24_20_Unified_Weathered_Gray_Clay';RIDGE=11.7625;PITCH=.158;EXPOSE=.30
east=np.array([-.487509082361,.003126681698,10.020600366289])
west=np.array([.42259216,east[1],east[2]-(.487509082361+.42259216)*RIDGE])

def up_polys(n,predicate=lambda t,no:True):
 a=source(n);ps=[]
 for t in a['v'][a['f']]:
  no=np.cross(t[1]-t[0],t[2]-t[0]);size=np.linalg.norm(no)
  if size>1e-9 and no[2]>.5*size and predicate(t,no):ps.append(Polygon(t[:,:2]))
 return unary_union(ps).buffer(0)

def polygons(p):return[p]if p.geom_type=='Polygon'else list(getattr(p,'geoms',[]))
def footprint(p,lo=-2,hi=8):
 pieces=[]
 for q in polygons(p):
  if q.area<1e-8:continue
  m=section(list(q.exterior.coords)[:-1],hi-lo).translate([0,0,lo])
  for h in q.interiors:
   if Polygon(h).area>1e-8:m=m-section(list(h.coords)[:-1],hi-lo+.02).translate([0,0,lo-.01])
  pieces.append(m)
 return union(pieces)

def bed(p,co):return footprint(p,0,.07).transform(np.array([[1,0,0,0],[0,1,0,0],[co[0],co[1],1,co[2]-.07]],float))

mainpoly=unary_union([up_polys(n)for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','SITE_KITCHEN_V11_REGISTERED_EAST_EAVE_STRIP_Geometry']]).buffer(.00002).buffer(-.00002)
# Fill the old front rectangular notch up to the existing two-roof interface.
mainpoly=unary_union([mainpoly,box(8.25,-12.13,9.54,-11.20)]).buffer(0)
jointpoly=up_polys('V24_20_Two_Rooms_Continuous_Valley_Roof_Bed',lambda t,n:n[0]>.25*n[2])
westp=mainpoly.intersection(box(7.42,-13,RIDGE,0));eastp=mainpoly.intersection(box(RIDGE,-13,16,0))
gate_names=['V24_XIESHAN_01_Upper_Two_Main_Slopes','V24_XIESHAN_02_Four_Lower_Hipped_Eaves','V24_XIESHAN_07_Closed_Pale_Ceiling','V24_XIESHAN_08_Five_Continuous_Stepped_Eave_Bands','V24_XIESHAN_09_Continuous_Eave_Bearing_Core']
gate=union([load(n)for n in gate_names]);guard=union([gate.translate(v)for v in [[0,0,0],[.003,0,0],[-.003,0,0],[0,.003,0],[0,-.003,0],[0,0,.003],[0,0,-.003]]])
deck=union([bed(westp,west),bed(eastp,east)])-guard
put('SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry',deck,MAT)
if 'SITE_KITCHEN_V11_REGISTERED_EAST_EAVE_STRIP_Geometry'not in OUT['remove']:OUT['remove'].append('SITE_KITCHEN_V11_REGISTERED_EAST_EAVE_STRIP_Geometry')

def tile(s,a,b,co,pan):
 lift_a=.006 if co[0]>0 else 0.;lift_b=0. if co[0]>0 else .006;slope=co[0]+(lift_b-lift_a)/(b-a);along=np.array([1.,0.,slope]);length=np.linalg.norm(along)*(b-a);along/=np.linalg.norm(along);across=np.array([0.,-1.,0.]);normal=np.cross(across,along);normal/=np.linalg.norm(normal)
 if pan:
  us=np.linspace(-.061,.061,9);p=[(float(u),-.012+.012*(u/.061)**2)for u in us];p +=[(u,z-.010)for u,z in p[::-1]]
 else:
  ts=np.linspace(0,math.pi,13);p=[(.054*math.cos(t),.054*math.sin(t)-.005)for t in ts]+[(.044*math.cos(t),.044*math.sin(t)-.005)for t in ts[::-1]]
 m=section(p,length)
 if not pan:
  ts=np.linspace(0,math.pi,13);p=[(.063*math.cos(t),.063*math.sin(t)-.005)for t in ts]+[(.045*math.cos(t),.045*math.sin(t)-.005)for t in ts[::-1]]
  lip=section(p,min(.018,length));m=union([m,lip.translate([0,0,0 if slope>0 else max(0,length-.018)])])
 origin=[a,s,float(co@np.array([a,s,1]))+.025+lift_a]
 return m.transform(np.c_[across,normal,along,origin])

tile_stats=[]
for name,p,co,anchor,new in [('V24_20_Kitchen_Unified_Pan_Barrel_Slope_0',westp,west,7.43,False),('V24_25_Kitchen_East_Unified_Pan_Barrel_Field',unary_union([eastp,jointpoly]).buffer(0),east,RIDGE,True)]:
 parts=[];dx=EXPOSE/math.sqrt(1+co[0]**2);overlap=.018/math.sqrt(1+co[0]**2);x0,y0,x1,y1=p.bounds
 for iy in range(math.floor((y0+12.13)/PITCH)-1,math.ceil((y1+12.13)/PITCH)+1):
  for pan,off in [(False,0.),(True,PITCH/2)]:
   s=-12.13+.061+iy*PITCH+off
   for ix in range(math.floor((x0-anchor)/dx)-1,math.ceil((x1-anchor)/dx)+1):
    aa=anchor+ix*dx;bb=aa+dx+overlap
    if not p.intersects(box(aa,s-.063,bb,s+.063)):continue
    parts.append(tile(s,aa,bb,co,pan))
 m=(compose(parts)^footprint(p))-guard
 # Remove numerical dust left by the trimming planes.
 m=compose([q for q in m.decompose()if q.volume()>1e-9])
 put(name,m,MAT,new)
 tile_stats.append({'name':name,'units_before_boundary_trim':len(parts),'plane':co.tolist(),'across_pitch_m':PITCH,'course_exposure_m':EXPOSE,'along_origin_x':anchor,'across_origin_y':-12.069,'all_rows_share_course_origin':True})
OUT['proof']['kitchen_roof']={'reference':'180416 roof diagonal strip','cause':'Warped roof faces and per-row adaptive tile spacing displaced the courses diagonally.','method':'Two true pitched planes meet at the retained ridge axis; global course phase across every row; continuous pan-and-barrel fields; preserve the existing storage valley envelope.','ridge_x_m':RIDGE,'deck_thickness_m':.07,'west_plane':west.tolist(),'east_plane':east.tolist(),'tiles':tile_stats,'gate_guard_clearance_m':.003,'ridge_caps_ears_and_storage_tiles_preserved':True,'no_new_front_flat_plate':True}
write();print('V25_ROOF_READY',flush=True)
