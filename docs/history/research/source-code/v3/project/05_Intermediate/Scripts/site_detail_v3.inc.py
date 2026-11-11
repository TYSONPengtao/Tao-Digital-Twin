# Evidence-based V3 changes. Coordinates remain local metres.
S['elements']=[e for e in S['elements'] if not e['name'].startswith(('SITE_KITCHEN','SITE_INNER_RED_GATE','SITE_OUTER_ENTRY_PORTAL','SITE_ENTRY_RAMP','SITE_INTERNAL_YARD_DIVIDER','SITE_INNER_ENTRY_WALL','SITE_GATE_TO_KITCHEN_WALL'))]
M.update({'M_Grey_Brick':{'color':[110,113,111],'roughness':.95},'M_Stone_Frame':{'color':[166,168,163],'roughness':.85},'M_Timber_Honey':{'color':[173,109,45],'roughness':.48},'M_Dark_Door_Wood':{'color':[74,31,24],'roughness':.5},'M_Thatch':{'color':[155,132,86],'roughness':1},'M_Metal_Gate':{'color':[129,132,126],'metallic':.75,'roughness':.33}})
SRC='D:/DJI/0002/DCIM/101MEDIA; DJI_0073,0092,0101,0107,0110,0120,0156,0161,0303,0508,0644 + CCM JIA/PTHOUSE; video674/749/897s'

def beam3(a,b,w,d,mat):
 a=np.array(a,float);b=np.array(b,float);u=(b-a)/np.linalg.norm(b-a);axis=np.array([0.,0,1]) if abs(u[2])<.9 else np.array([1.,0,0]);v=np.cross(u,axis);v/=np.linalg.norm(v);n=np.cross(u,v)
 pp=[(a+v*x*w/2+n*y*d/2).tolist() for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 return part(prism(pp,(b-a).tolist()),mat)

def raised_ring(name,x,y,z,w,h,depth,mat,source=SRC):
 # Recessed stepped panel frame, modelled without decorative imagery claims.
 c=.09;outer=[(0,c),(c,c),(c,0),(w-c,0),(w-c,c),(w,c),(w,h-c),(w-c,h-c),(w-c,h),(c,h),(c,h-c),(0,h-c)]
 poly=Polygon(outer);ring=poly.difference(poly.buffer(-.035,join_style=2));pieces=[]
 for q in polys(ring):
  # Transform a planar ring through a closed triangulated thin prism.
  g=pg(q,0,depth,mat)
  for ppart in g:
   gg=ppart['geometry'];gg['v3_vertical_transform']=[x,y,z]
   # Geometry adapter already accepts arbitrary prism profiles; split ring into rectangles via triangulation.
   rings=[list(q.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in q.interiors];vv=np.array([p for r in rings for p in r]);tt=mapbox_earcut.triangulate_float64(vv,np.cumsum([len(r) for r in rings]).astype(np.uint32)).reshape(-1,3)
   for tri in tt:pieces.append(part(prism([[x+float(vv[i,0]),y,z+float(vv[i,1])] for i in tri],[0,-depth,0]),mat))
   break
 add(name,pieces,source=source,classification='MASONRY_ORNAMENT_FRAME',detail_limit='Stepped frame reproduced; carved relief images omitted where unmeasured')

def chinese_cap(name,x0,x1,y,depth,eave,rise=.32,end_lift=.28,mat='M_Roof'):
 nx=17;ny=9;vv=[];ff=[]
 def zz(x,dy):
  end=max(0,1-min(x-x0,x1-x)/.75)**2
  return eave+rise*(1-abs(dy)/(depth/2))+.11*(abs(dy)/(depth/2))**3+end_lift*end
 for x in np.linspace(x0,x1,nx):
  for dy in np.linspace(-depth/2,depth/2,ny):vv.append([float(x),y+float(dy),zz(x,dy)])
 for i in range(nx-1):
  for j in range(ny-1):a=i*ny+j;ff.append([a,a+ny,a+ny+1,a+1])
 N=len(vv);bottom=[[x,yy,z-.075] for x,yy,z in vv];edges=[]
 edges.extend((i*ny,(i+1)*ny) for i in range(nx-1));edges.extend(((nx-1)*ny+j,(nx-1)*ny+j+1) for j in range(ny-1));edges.extend((i*ny+ny-1,(i-1)*ny+ny-1) for i in range(nx-1,0,-1));edges.extend((j,j-1) for j in range(ny-1,0,-1))
 faces=ff+[[i+N for i in f[::-1]] for f in ff]+[[b,a,a+N,b+N] for a,b in edges]
 add(name+'_CURVED_TILE_SHELL',[part({'type':'polyhedron','vertices':vv+bottom,'faces':faces},mat)],source=SRC,classification='CURVED_CHINESE_TILE_COPING',roof_ridge_direction='X',roof_shape='Curve rises at ridge ends; front/rear slopes; not a doorway')
 ribs=[]
 for x in np.arange(x0+.12,x1-.10,.20):
  for side in [-1,1]:
   xx=float(x);dy0=0;dy1=side*depth/2
   a=[xx,y+dy0,zz(xx,dy0)+.035];b=[xx,y+dy1,zz(xx,dy1)+.035];ribs.append(beam3(a,b,.06,.06,mat))
 add(name+'_BARREL_TILE_ROWS',ribs,family='VIS_MODEL',source='DJI_0107,0110; approximately 200mm barrel tile pitch',classification='CERAMIC_TILE_DETAILS')
 # Open lattice ridge with diamond openings, clearly distinct from solid wall body.
 ridge_z=eave+rise+.12;rr=[]
 rr.append(beam3([x0+.15,y,ridge_z],[x1-.15,y,ridge_z],.08,.05,mat));rr.append(beam3([x0+.15,y,ridge_z+.21],[x1-.15,y,ridge_z+.21],.08,.05,mat))
 for x in np.arange(x0+.18,x1-.35,.27):
  rr.extend([beam3([x,y,ridge_z+.02],[x+.25,y,ridge_z+.20],.028,.04,mat),beam3([x,y,ridge_z+.20],[x+.25,y,ridge_z+.02],.028,.04,mat)])
 add(name+'_OPEN_RIDGE_LATTICE',rr,source='DJI_0107,0110,0025 visible diamond open ridge',classification='OPENWORK_TILE_RIDGE')

# Inner courtyard dividing wall: grey brick towards farmyard, white rendering inside.
wallchain('SITE_COURTYARD_WEST_TILE_WALL',[[0,1],[0,-10.7],[4.9,-11.7]],.25,False,2.65)
wallchain('SITE_GATE_EAST_FLANK',[[8.3,-11.7],[13.3,-11.7]],.25,False,2.65)
for e in S['elements']:
 if e['name'] in ['SITE_COURTYARD_WEST_TILE_WALL','SITE_GATE_EAST_FLANK']:
  for pa in e['parts'][::2]:pa['material']='M_Grey_Brick'
  e.update(source='DJI_0025 and DJI_0073: grey brick dividing wall, tiled ridge',classification='CHINESE_TILE_TOP_MASONRY_WALL')
add('SITE_COURTYARD_WEST_WHITE_INSIDE',[part(box(.125,-10.65,-.15,.018,11.65,2.28),'M_Wall_Exterior')],source='DJI_0156,0161: courtyard-facing white rendered wall',classification='WHITE_INNER_FACE_FINISH')

# Low timber farmyard fence beside the car passage; this was wrongly a tall tiled wall in V2.
fencepts=[[0,-10.7],[-5,-10.5],[-11.4,-8.6],[-14.65,-8.37]];fparts=[]
for a,b in zip(fencepts[:-1],fencepts[1:]):
 a=np.array(a);b=np.array(b);length=np.linalg.norm(b-a)
 for t in np.linspace(0,1,max(2,int(length/1.8)+1),endpoint=False):
  x,y=(1-t)*a+t*b;fparts.append(part({'type':'cylinder','origin':[float(x),float(y),-.5],'radius':.05,'height':1.48,'segments':12},'M_Wood'))
 for z in [.05,.6]:fparts.append(beam3([*a,z],[*b,z],.055,.055,'M_Wood'))
add('SITE_FARMYARD_TIMBER_FENCE',fparts,source='DJI_0073,0303: low timber fence beside entry passage',classification='FARMYARD_TIMBER_FENCE')

# Actual outer entry: an open-top metal gate at the south-west boundary gap.
gateA=np.array([-14.65,-8.37]);gateB=np.array([-12.88,-12.7275]);gv=gateB-gateA;length=np.linalg.norm(gv);gu=gv/length;gn=np.array([-gu[1],gu[0]])
def local_gate(x,y,z):return [*(gateA+gu*x+gn*y),z-.85-.35*x/length]
metal=[];base=0;H=2.25
for j in range(4):
 a=.12+j*(length-.24)/4+.004;b=.12+(j+1)*(length-.24)/4-.004
 metal.extend([beam3(local_gate(a,0,base),local_gate(a,0,base+H),.045,.045,'M_Metal_Gate'),beam3(local_gate(b,0,base),local_gate(b,0,base+H),.045,.045,'M_Metal_Gate'),beam3(local_gate(a,0,base+.78),local_gate(b,0,base+.78),.045,.045,'M_Metal_Gate'),beam3(local_gate(a,0,base+.02),local_gate(b,0,base+.02),.045,.045,'M_Metal_Gate')])
 panel=[local_gate(a+.03,-.019,base+.05),local_gate(b-.03,-.019,base+.05),local_gate(b-.03,-.019,base+.75),local_gate(a+.03,-.019,base+.75)];metal.append(part(prism(panel,[float(gn[0]*.038),float(gn[1]*.038),0]),'M_Metal_Gate'))
 for x in np.arange(a+.12,b-.04,.14):metal.append(beam3(local_gate(x,0,base+.81),local_gate(x,0,base+H-.06),.018,.018,'M_Metal_Gate'))
 metal.append(beam3(local_gate(a,0,base+H),local_gate(b,0,base+H+.12*math.sin(math.pi*(j+.5)/4)),.045,.045,'M_Metal_Gate'))
add('SITE_SW_METAL_ENTRY_GATE',metal,source='DJI_0073; video897s metal lattice and solid lower leaves; JIA/PTHOUSE gap endpoints',classification='METAL_VEHICLE_GATE',clear_width_m=round(length-.24,3),gap_endpoints=[gateA.tolist(),gateB.tolist()],no_tile_roof=True)

# Gatehouse between the passage and inner court. Doorway is 2.60m, not the previous 4.54m.
door0,door1=5.30,7.90;y=-11.7;z=-.45;h=2.50;w=door1-door0
posts=[part(box(4.9,y-.25,z,.4,.5,2.9),'M_Stone_Frame'),part(box(7.9,y-.25,z,.4,.5,2.9),'M_Stone_Frame'),part(box(5.3,y-.25,z+h,2.6,.5,.4),'M_Stone_Frame')]
add('SITE_INNER_STONE_GATEHOUSE',posts,source='DJI_0101,0120; JIA roof plan; carved stone/plaster frame, not plain white or timber post',classification='MASONRY_CARVED_GATEHOUSE',clear_width_m=w,clear_height_m=h)
doorparts=[]
for j in range(2):
 xx=door0+j*w/2;doorparts.append(part(box(xx+.012,y-.035,z+.02,w/2-.024,.07,h-.04),'M_Dark_Door_Wood'))
 for zz in [.16,.85,1.7]:
  ring=rect(xx+.09,z+zz,xx+w/2-.09,z+min(zz+.57,h-.12)).difference(rect(xx+.13,z+zz+.04,xx+w/2-.13,z+min(zz+.53,h-.16)))
  for poly in polys(ring):
   # four rectangular raised door moulding strips
   bx0,bz0,bx1,bz1=poly.bounds
   doorparts.extend([part(box(bx0,y-.064,bz0,.035,.025,bz1-bz0),'M_Dark_Door_Wood'),part(box(bx1-.035,y-.064,bz0,.035,.025,bz1-bz0),'M_Dark_Door_Wood'),part(box(bx0+.035,y-.064,bz0,bx1-bx0-.07,.025,.035),'M_Dark_Door_Wood'),part(box(bx0+.035,y-.064,bz1-.035,bx1-bx0-.07,.025,.035),'M_Dark_Door_Wood')])
add('SITE_INNER_DARK_TIMBER_DOORS',doorparts,source='DJI_0120 dark brown panelled double gate leaves',classification='PANELLED_TIMBER_GATE_LEAVES')
chinese_cap('SITE_INNER_GATEHOUSE_ROOF',4.45,8.75,y,1.5,2.45,.35,.35)
for x in [4.95,7.95]:raised_ring('SITE_GATEHOUSE_CARVED_PANEL_FRAME_'+str(x),x,y-.26,.1,.30,1.75,.025,'M_Stone_Frame')

# Solid screen wall outside the gate: raised masonry centre with moulded panels and curved tile ridge.
add('SITE_SOUTH_SCREENWALL_RAISED_BODY',[part(box(3.25,-17.10,2.15,7.55,.38,.45),'M_Wall_Exterior')],source='DJI_0107,0110; outside centre is a solid screen wall, no doorway',classification='SOLID_MASONRY_SCREENWALL',door_opening=False)
chinese_cap('SITE_SOUTH_SCREENWALL',3.1,10.95,-16.9,1.10,2.62,.32,.44)
for i,(x,w) in enumerate([(3.55,1.0),(4.65,2.65),(7.40,2.65)]):raised_ring(f'SITE_SCREENWALL_STEPPED_PANEL_{i}',x,-17.105,1.70,w,.52,.025,'M_Stone_Frame')
add('SITE_SCREENWALL_HORIZONTAL_MOULDINGS',[part(box(3.27,-17.145,z,7.50,.055,.045),'M_Stone_Frame') for z in [1.59,2.27,2.39]],source='DJI_0107,0110 moulded frame belts',classification='SCREENWALL_PLASTER_MOULDINGS')

# Chinese kitchen wing: masonry backs and gables, timber columns, beams, panels, glazing and exposed roof framing.
x0,y0,x1,y1=7.7,-11.6,13.35,-2.6;kfoot=rect(x0,y0,x1,y1);backwall=unary_union([rect(x1-.22,y0,x1,y1),rect(x0,y0,x1,y0+.22),rect(x0,y1-.22,x1,y1)])
add('SITE_KITCHEN_STONE_FLOOR',pg(kfoot,-.57,.17,'M_Concrete'),source='CCM footprint; DJI_0156 timber wing stone threshold',classification='TRADITIONAL_KITCHEN_WING')
add('SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES',pg(backwall,-.40,3.35,'M_Grey_Brick'),source='DJI_0120,0508 exterior masonry; kitchen courtyard front is timber',classification='MASONRY_BACK_AND_GABLE_WALLS')
roof('SITE_KITCHEN_CHINESE_TILE_ROOF',x0-.72,y0-.45,x1+.25,y1+.45,2.95,4.65,'gable','M_Roof','60_SITE','SITE_MODEL')
for yy in [y0+.11,y1-.11]:
 profile=[[x0,yy,2.95],[x1,yy,2.95],[(x0-.72+x1+.25)/2,yy,4.52]]
 add('SITE_KITCHEN_GABLE_INFILL_'+str(yy),[part(prism(profile,[0,.18,0]),'M_Grey_Brick')],source='DJI_0508 masonry gable behind tile roof',classification='MASONRY_GABLE_INFILL')
timber=[]
for yy in [y0+.18,(y0+y1)/2,y1-.18]:
 timber.append(part(box(x0-.21,yy-.18,-.4,.36,.36,.36),'M_Stone_Frame'))
 timber.append(part({'type':'cylinder','origin':[x0-.03,yy,-.04],'radius':.14,'height':2.86,'segments':32},'M_Timber_Honey'))
timber.extend([part(box(x0-.18,y0+.18,2.55,.30,y1-y0-.36,.30),'M_Timber_Honey'),part(box(x0-.14,y0+.18,1.92,.22,y1-y0-.36,.16),'M_Timber_Honey')])
add('SITE_KITCHEN_TIMBER_COLUMNS_AND_BEAMS',timber,source='DJI_0156,0867: honey-coloured timber columns, beams and stone bases',classification='EXPOSED_CHINESE_TIMBER_FRAME')

def lattice_panel(name,xa,ya,yb,sill,head):
 parts=[];t=.035
 for yy in [ya,yb-t]:parts.append(part(box(xa-.045,yy,sill,.09,t,head-sill),'M_Timber_Honey'))
 for zz in [sill,head-t]:parts.append(part(box(xa-.045,ya+t,zz,.09,yb-ya-2*t,t),'M_Timber_Honey'))
 parts.append(part(box(xa-.008,ya+t,sill+t,.012,yb-ya-2*t,head-sill-2*t),'M_Glass_Clear'))
 # Rectangular/octagonal pattern from DJI_0156, not an invented generic vertical grille.
 yc=(ya+yb)/2;zc=(sill+head)/2;wy=min(.42,(yb-ya)*.28);hz=min(.24,(head-sill)*.25)
 pp=[[yc-wy,zc-hz*.45],[yc-wy*.55,zc-hz],[yc+wy*.55,zc-hz],[yc+wy,zc-hz*.45],[yc+wy,zc+hz*.45],[yc+wy*.55,zc+hz],[yc-wy*.55,zc+hz],[yc-wy,zc+hz*.45]]
 for a,b in zip(pp,pp[1:]+pp[:1]):parts.append(beam3([xa-.055,*a],[xa-.055,*b],.024,.026,'M_Timber_Honey'))
 for yy in [yc-wy,yc+wy]:
  parts.append(part(box(xa-.065,yy-.013,sill+t,.026,.026,max(.01,zc-hz-sill-t)),'M_Timber_Honey'));parts.append(part(box(xa-.065,yy-.013,zc+hz,.026,.026,max(.01,head-t-zc-hz)),'M_Timber_Honey'))
 add(name,parts,source='DJI_0156,0867 octagonal and rectangular timber lattice over glazing',classification='CHINESE_TIMBER_LATTICE_WINDOW')

middle=(y0+y1)/2;doors=[(middle-1.12,middle-.16),(middle+.16,middle+1.12)];windows=[(y0+.36,doors[0][0]-.04),(doors[1][1]+.04,y1-.36)]
for j,(a,b) in enumerate(doors):
 parts=[part(box(x0-.055,a,-.40,.11,b-a,2.3),'M_Timber_Honey')]
 for zz in [-.23,.25,.85,1.52]:
  parts.append(part(box(x0-.084,a+.07,zz,.026,b-a-.14,.035),'M_Timber_Honey'))
 for yy in [a+.07,b-.10]:parts.append(part(box(x0-.084,yy,-.23,.026,.035,2.0),'M_Timber_Honey'))
 add(f'SITE_KITCHEN_TIMBER_DOOR_{j+1}',parts,source='DJI_0867: two separate solid single timber doors flanking centre post',classification='TIMBER_PANELLED_DOOR',opening_width=b-a)
for j,(a,b) in enumerate(windows):
 add(f'SITE_KITCHEN_TIMBER_SILL_PANEL_{j+1}',[part(box(x0-.055,a,-.40,.11,b-a,.95),'M_Timber_Honey')],source='DJI_0156 lower solid timber panel',classification='TIMBER_SILL_PANEL')
 width=(b-a)/3
 for k in range(3):lattice_panel(f'SITE_KITCHEN_LATTICE_{j}_{k}',x0,a+k*width,b if k==2 else a+(k+1)*width,.55,1.92)
for j in range(8):
 a=y0+.36+j*(y1-y0-.72)/8;b=y0+.36+(j+1)*(y1-y0-.72)/8
 lattice_panel(f'SITE_KITCHEN_TRANSOM_{j}',x0,a,b,2.10,2.48)
framing=[]
for yy in np.arange(y0+.5,y1-.1,1.1):
 ridge_x=(x0-.72+x1+.25)/2
 framing.extend([beam3([x0,yy,2.85],[x1-.20,yy,2.85],.10,.16,'M_Timber_Honey'),beam3([x0-.72,yy,2.78],[ridge_x,yy,4.48],.065,.085,'M_Timber_Honey'),beam3([ridge_x,yy,4.48],[x1+.25,yy,2.78],.065,.085,'M_Timber_Honey')])
add('SITE_KITCHEN_EXPOSED_TIMBER_ROOF_FRAMING',framing,source='DJI_0156 exposed eave wood framing; hidden joinery not asserted',classification='TIMBER_RAFTERS_AND_TIE_BEAMS')

# Traditional brick annex is not labelled as timber structure without evidence.
for e in S['elements']:
 if e['name'].startswith('SITE_SOUTH_EAST_ANNEX'):
  e.update(classification='CHINESE_MASONRY_TILE_ROOF_ANNEX',source='DJI_0508,0581; CCM footprint; no evidence of an all-timber structural system')
  if e['name'].endswith('_WALLS'):
   for pa in e['parts']:pa['material']='M_Grey_Brick'
 if e['name'].startswith('SITE_GAZEBO'):
  e.update(classification='LIGHT_CANOPY_WITH_METAL_ROOF',source='DJI_0285,0303 metal sheet hip canopy; not a traditional tile-roof pavilion')
  if e['name'].endswith('_POSTS'):
   for pa in e['parts']:pa['material']='M_Metal_Black'
 if e['name'].startswith('SITE_WEST_PERGOLA_ROOF'):
  for pa in e['parts']:pa['material']='M_Thatch'
  e.update(classification='FARMYARD_THATCH_SHELTER',source='DJI_0073,0303 woven thatch cover; not tiled roof')

# Short exterior approach connects the real SW gate to the public lane; no opening through screen wall.
approach=Polygon([[-16.2,-8.7],[-14.65,-8.37],[-12.88,-12.7275],[-14.3,-13.5],[-17.0,-11.4]])
entry_gap_line=LineString([gateA,gateB]);entry_outer_edge=approach.boundary.difference(plot.buffer(.35))
def entry_ground_height(x,y):
 point=Point(x,y);near=point.distance(entry_gap_line);far=point.distance(entry_outer_edge);blend=near/max(1e-8,near+far)
 return gate_datum_v3(x,y)*(1-blend)+gz(x,y)*blend
terrain('SITE_SW_GATE_APPROACH',approach.difference(plot),'M_Site_Paving',.55,height_function=entry_ground_height)
# Cope at the gate threshold with the local level; 4.7m width covers the observed diagonal gap.
threshold_xy=[gateA,gateB,gateB+gn*.35,gateA+gn*.35]
threshold=[[*pt,courtyard_datum_v3(*pt)] for pt in threshold_xy]
add('SITE_SW_GATE_THRESHOLD',[part({'type':'terrain','vertices':threshold,'faces':[[0,1,2],[0,2,3]]},'M_Site_Paving')],surface_only=True,source='DJI_0073 and video897s; modest threshold, no south central ramp',classification='ACTUAL_ENTRY_THRESHOLD')

# Wall top ornament along the courtyard west wall, on farmyard-facing side.
for j in range(10):
 ya=-10.4+j*1.05
 parts=[part(box(-.145,ya,1.85,.026,.9,.035),'M_Stone_Frame'),part(box(-.145,ya,2.25,.026,.9,.035),'M_Stone_Frame'),part(box(-.145,ya,1.885,.026,.035,.365),'M_Stone_Frame'),part(box(-.145,ya+.865,1.885,.026,.035,.365),'M_Stone_Frame')]
 add(f'SITE_WEST_TILE_WALL_PANEL_{j}',parts,source='DJI_0025 rectangular white frame belt over grey brick wall',classification='TILE_WALL_ORNAMENT_BELT')

S['cameras'] += [dict(name='CAM_09_SW_Gate',position=[-24,-22,6],target=[-13.9,-10.6,.8],fov=52,status='REVIEW_CAMERA'),dict(name='CAM_10_Screenwall',position=[6.5,-29,4],target=[6.5,-16.9,1.8],fov=52,status='REVIEW_CAMERA'),dict(name='CAM_11_Chinese_Kitchen',position=[1.1,-6.6,2.1],target=[7.7,-7.1,1.3],fov=65,status='REVIEW_CAMERA'),dict(name='CAM_12_Inner_Gate',position=[6.5,-15.7,1.6],target=[6.5,-11.7,1.1],fov=70,status='REVIEW_CAMERA')]
for j in range(3):
 x=4.19+j*1.59;raised_ring(f'BALCONY_STONE_PANEL_MOULDING_{j}',x,-.092,4.06,1.40,.62,.035,'M_Stone',source='DJI_0862 three stone panel relief fields; frame retained, relief motifs not fabricated')
for e in S['elements']:
 if e['name'].startswith('BALCONY_STONE_PANEL'):e['layer']='41_RAILING';e['family']='ARCH_MODEL'
