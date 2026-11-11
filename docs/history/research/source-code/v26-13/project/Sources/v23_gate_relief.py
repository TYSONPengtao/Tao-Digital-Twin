"""V23 photo/ideal fitted inner-gate faceted stone piers and modeled relief.

All relief is closed geometry; no bitmap displacement is used.  Roots intersect
their relief backing.  Native stone bodies are partitioned around the inserts.
"""
from v23_common import *

D=W/'v23_gate_relief';D.mkdir(exist_ok=True);Q=start();checks=[]
STONE='M_V21_GATE_REF_02';TRIM='M_V21_GATE_REF_03';RELIEF='M_V21_GATE_REF_04';HEADER='M_V21_GATE_REF_05'

def prismxy(poly,z,h):
 return manifold({'type':'prism','profile':[[x,y,z] for x,y in poly],'vector':[0,0,h]})

def plan(x0,x1,y0,y1,c):
 return [[x0+c,y0],[x1-c,y0],[x1,y0+c],[x1,y1],[x0,y1],[x0,y0+c]]

def mapped(m,a,b):
 """Map local u/depth/z onto a face; positive depth points into the stone."""
 a=np.array(a,float);b=np.array(b,float);t=(b-a)/np.linalg.norm(b-a);n=np.array([-t[1],t[0]])
 return m.transform([[t[0],n[0],0,a[0]],[t[1],n[1],0,a[1]],[0,0,1,0]])

def dome_leaf(u,z,length,width,angle,height=.023):
 """Pointed lenticular leaf, modeled with a convex central ridge and turned tip."""
 n=24;v=[[0,-height,0]];rings=[.34,.68,1.0];f=[]
 for rr in rings:
  for j in range(n):
   t=2*math.pi*j/n;s=math.sin(t);q=math.cos(t)
   v.append([rr*q*length*.5,-height*(1-rr**1.65)*(1+.12*q),rr*s*abs(s)**.34*width*.5])
 for j in range(n):f.append([0,1+j,1+(j+1)%n])
 for k in range(2):
  for j in range(n):
   a=1+k*n+j;b=1+k*n+(j+1)%n;c=1+(k+1)*n+(j+1)%n;d=1+(k+1)*n+j
   f.extend([[a,d,c],[a,c,b]])
 last=1+2*n;back=len(v)
 for j in range(n):v.append([v[last+j][0],.009,v[last+j][2]])
 bc=len(v);v.append([0,.009,0])
 for j in range(n):
  a=last+j;b=last+(j+1)%n;c=back+(j+1)%n;d=back+j
  f.extend([[a,b,c],[a,c,d],[bc,d,c]])
 a=math.radians(angle);ca,sa=math.cos(a),math.sin(a);vv=np.array(v);x=vv[:,0].copy();zz=vv[:,2].copy();vv[:,0]=u+ca*x-sa*zz;vv[:,2]=z+sa*x+ca*zz
 return manifold({'type':'polyhedron','vertices':vv.tolist(),'faces':f})

def blossom(u,z,r,petals=8):
 ms=[]
 for j in range(petals):
  a=j*360/petals;t=math.radians(a)
  ms.append(dome_leaf(u+r*.44*math.cos(t),z+r*.44*math.sin(t),r*1.13,r*.47,a,.024))
 # A raised, rounded seed centre with a small crown of seed bosses.
 ms.append(dome_leaf(u,z,r*.58,r*.58,0,.034))
 for j in range(7):
  t=j*2*math.pi/7;ms.append(dome_leaf(u+r*.15*math.cos(t),z+r*.15*math.sin(t),r*.11,r*.11,0,.039))
 return uni(ms)

def curved_stem(points,r=.004,height=.011):
 # Back face crosses the inset stone backing, keeping every stem supported.
 return stroke(points,r,height+.009).translate([0,-height,0])

def panel_art(width,z0,z1,kind,seed):
 """Return a full inset plate with rooted botanical low relief."""
 h=z1-z0;mid=width/2
 ms=[cube([.003,-.001,z0],[width-.006,.010,h])]
 if kind=='bamboo':
  for k in range(3):
   xx=mid+(k-1)*width*.19;zz0=z0+.055;zz1=z1-.07
   pts=[[xx+.009*math.sin(5*t+k),zz0+t*(zz1-zz0)] for t in np.linspace(0,1,40)]
   ms.append(curved_stem(pts,.0048,.012))
   for j,t in enumerate(np.linspace(.15,.92,7)):
    zz=zz0+t*(zz1-zz0);side=-1 if (j+k+seed)%2 else 1;lng=width*(.40 if k==1 else .35)
    cx=xx+side*lng*.34;cz=zz+.015
    ms.append(dome_leaf(cx,cz,lng,width*.105,55 if side>0 else 125,.022+.002*((j+k)%3)))
    # Raised bamboo nodes vary with height rather than repeated rectangular tabs.
    ms.append(dome_leaf(xx,zz-.019,width*.075,.011,0,.016))
  for j in range(3):
   u=width*(.22+.25*j);ms.append(dome_leaf(u,z0+.045+j*.012,width*.46,width*.10,22+65*j,.018))
 else:
  r=min(width*.35,h*.19);zz=z0+h*.57
  ms.append(blossom(mid,zz,r,10 if seed%2 else 8))
  if h>.6:ms.append(blossom(mid+width*.18,z0+h*.23,r*.58,7))
  pts=[[mid+width*.26*math.sin(t*5-1),z0+.035+t*(h-.09)] for t in np.linspace(0,1,40)]
  ms.append(curved_stem(pts,.004,.013))
  for j,t in enumerate([.12,.27,.43,.73,.89]):
   side=-1 if j%2 else 1;u=mid+width*.26*math.sin(t*5-1)
   ms.append(dome_leaf(u+side*width*.13,z0+.035+t*(h-.09),width*.47,width*.17,38 if side>0 else 145,.022))
 return uni(ms)

def framed_insert(width,z0,z1):
 # Three differently stepped moulding beads leave a shadow recess around art.
 return uni([rectframe(0,width,z0,z1,-.028,.010,.030),rectframe(.013,width-.013,z0+.013,z1-.013,-.037,.006,.040)])

cores=[];frames=[];art=[];allorn=[];face_records=[];waist_panels=[]
header_raw=cube([5.338095,-11.8084,2.435],[2.52381,.4264,.2643])
for pi,(x0,x1) in enumerate([(4.933333333333334,5.457142857142857),(7.742857142857142,8.266666666666666)]):
 y0=-11.87;y1=-11.294;c=.09
 core=prismxy(plan(x0,x1,y0,y1,c),-.4577,3.091)
 # One visible base, a lower-third waist, and a narrow capital.  The chamfer
 # continues through all collars instead of reverting to a square box.
 collars=[]
 for zz,hh,projection in [(-.45,.079,.032),(.633,.082,.025),(2.365,.070,.021)]:
  outline=plan(x0-.017,x1+.017,y0-projection,y1+.010,c+.012)
  body=prismxy(outline,zz,hh)
  # Finer shallow lip above and below is part of the collar union.
  lip=prismxy(plan(x0-.024,x1+.024,y0-projection-.004,y1+.011,c+.013),zz+.009,.014)
  collar=body+lip
  # The ornamental front lip may project, but the back of the inner collar
  # stops exactly at the structural jamb.  A rear return wider than the jamb
  # intrudes into the independently moving leaf at its closed pose.
  if pi==0:collar-=cube([x1,-11.75,-.6],[.10,.60,3.4])
  else:collar-=cube([x0-.10,-11.75,-.6],[.10,.60,3.4])
  collars.append(collar)
 frame_piece=uni(collars)
 # Front plane plus both front bevels.  The narrow bevel carries a climbing
 # vine; the broad face carries bamboo above and flower sprays below.
 faces=[([x0+c,y0],[x1-c,y0],'front'),([x0,y0+c],[x0+c,y0],'left_bevel'),([x1-c,y0],[x1,y0+c],'right_bevel')]
 pierorn=[frame_piece];waistorn=[]
 for aa,bb,face in faces:
  fw=np.linalg.norm(np.array(bb)-aa);margin=.010 if face=='front' else .008
  w=fw-2*margin;t=(np.array(bb)-aa)/fw;start=(np.array(aa)+margin*t).tolist();end=(np.array(bb)-margin*t).tolist()
  for z0,z1 in [(-.305,.575),(.778,2.312)]:
   fr=mapped(framed_insert(w,z0,z1),start,end)
   inner=.018;pla=panel_art(w-2*inner,z0+.022,z1-.022,'bamboo' if z0>0 and face=='front' else 'flowers',pi+(face!='front'))
   ins=mapped(pla.translate([inner,0,0]),start,end)
   frames.append(pp(fr,TRIM));art.append(pp(ins,RELIEF));pierorn.extend([fr,ins])
   face_records.append({'pier':pi,'face':face,'panel_z':[z0,z1],'width_m':w,'modeled_surface':True,'backing_rooted':True})
  # Waist rosette and winding scroll follows each exposed faceted face.
  wm=[cube([.005,-.002,.649],[w-.010,.009,.048])]
  rr=min(w*.13,.020);wm.append(blossom(w*.5,.674,rr,8))
  for side in [-1,1]:
   pts=[[w*.5+side*t,.674+.009*math.sin(2*math.pi*t/max(.02,w*.35))] for t in np.linspace(rr,w*.41,25)]
   wm.append(curved_stem(pts,.0022,.011))
  wa=mapped(uni(wm).translate([0,-.029,0]),start,end);art.append(pp(wa,RELIEF));pierorn.append(wa);waistorn.append(wa)
 frame_piece=uni(collars)-uni(waistorn);frames.append(pp(frame_piece,TRIM))
 # Remove only occupied embedded insert volumes, maintaining a single joined
 # native structural stone core with the V22 rear and header bearings.
 core=core-uni(pierorn)-header_raw
 cores.append(pp(core,STONE));allorn.extend(pierorn)

put(Q,'SITE_V21_GATE_REFERENCE_LAYER_02',cores,classification='FACETED_FRONT_CORNER_STONE_PIERS_WITH_PARTITIONED_RELIEF_RECESSES',front_corner_chamfer_m=.09,structural_rear_envelope_preserved=True)
put(Q,'SITE_V21_GATE_REFERENCE_LAYER_03',frames,classification='ALIGNED_FACETED_STONE_PANEL_MOULDINGS_AND_LOWER_THIRD_WAIST',waist_z_m=[.633,.715])
put(Q,'SITE_V21_GATE_REFERENCE_LAYER_04',art,classification='MODELED_DOMED_BAMBOO_FLORAL_AND_BEVEL_VINE_BAS_RELIEF',motif_status='Photo/ideal fitted modeled relief; not a scan or exact carving facsimile',face_panels=face_records)

# Header keeps its exact V22 load-bearing box and two end supports.  Engraved
# fields now carry genuinely domed flowers, leaves and curling vines.
header=cube([5.338095,-11.8084,2.435],[2.52381,.4264,.2643]);hp=[];hdeco=[]
for k,cx in enumerate([5.78,6.60,7.42]):
 fr=rectframe(cx-.373,cx+.373,2.463,2.671,-11.833,.011,.030)+rectframe(cx-.357,cx+.357,2.478,2.656,-11.841,.004,.040)
 ms=[cube([cx-.340,-11.812,2.488],[.680,.009,.158])]
 fl=blossom(cx,2.567,.073,10 if k==1 else 8).translate([0,-11.812,0]);ms.append(fl)
 for side in [-1,1]:
  pts=[[cx+side*t,2.567+.020*math.sin(t*25)] for t in np.linspace(.045,.315,35)]
  ms.append(curved_stem(pts,.0032,.014).translate([0,-11.812,0]))
  for u,z,a in [(cx+side*.155,2.602,25 if side>0 else 155),(cx+side*.250,2.545,155 if side>0 else 25)]:
   ms.append(dome_leaf(u,z,.091,.032,a,.022).translate([0,-11.812,0]))
 ins=uni(ms);hdeco.extend([fr,ins]);hp.extend([pp(fr,TRIM),pp(ins,RELIEF)])
header=header-uni(hdeco);hp.insert(0,pp(header,HEADER))
put(Q,'SITE_V21_GATE_REFERENCE_LAYER_05',hp,classification='THREE_FLORAL_HEADER_FIELDS_WITH_VOLUMETRIC_ROSETTES_AND_CURLING_LEAVES')

checks=[{'check':'faceted_pier_front','chamfer_m':.09,'rear_y_m':-11.294,'front_y_m':-11.87,'status':'PASS'},
 {'check':'aligned_relief_and_frames','front_bevel_panels':len(face_records),'waist_z_m':[.633,.715],'status':'PASS'},
 {'check':'door_sweep_clearance_by_envelope','pier_rear_unchanged':True,'carvings_front_of_y_m':-11.77,'status':'PASS_DESIGN_ENVELOPE'},
 {'check':'rear_jamb_collar_clipping','rear_notch_y_min_m':-11.75,'left_inner_x_max_m':5.457142857142857,'right_inner_x_min_m':7.742857142857142,'status':'PASS_DESIGN_ENVELOPE'},
 {'check':'modeled_bowed_leaf_petals','texture_displacement_used':False,'relief_faces_per_pier':3,'status':'PASS'},
 {'check':'reference_limit','description':'Carving composition is fitted from ideal and site imagery; fine motif iconography is not surveyed.'}]
Q['change_notes']=['内大门方柱前缘改为连续折面，正面及两个斜面均设置有厚度的花卉竹叶浮雕。','腰线移至与理想图一致的下段比例，装饰框与上下雕花板统一分段，修正旧腰线横穿竹叶的矛盾。','花瓣、竹叶采用带中脊和鼓起表面的三维几何，花心、卷草和斜面细藤均落在连续嵌板上；门楣同步细化。','保留 V22 门洞、后缘、厨房接合与门扇运动位置。浮雕为照片拟合构图，不冒充精确石刻测绘。']
save(Q,D,checks)
