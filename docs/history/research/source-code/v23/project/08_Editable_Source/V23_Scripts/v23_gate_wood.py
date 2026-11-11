"""Native gate joinery, supported panel fields, cast hardware and lanterns."""
from v23_common import *
D=W/'v23_gate_wood';D.mkdir(exist_ok=True);Q=start();checks=[]
WOOD='M_V21_GATE_REF_06';EDGE='M_V21_GATE_REF_07';BRASS='M_V23_GATE_CAST_BRONZE'
Q['materials'][BRASS]={'color':[126,93,51],'roughness':.43,'metallic':.78}
Q['materials']['M_V23_GATE_LANTERN_GOLD']={'color':[181,137,59],'roughness':.52,'metallic':.55}
Q['materials']['M_V23_GATE_LANTERN_RED']={'color':[151,19,21],'roughness':.68,'metallic':0}

def orb(o,s):return mf.Manifold.sphere(1,20).scale(s).translate(o)
def tube(points,radii,n=16):
 v=[];f=[];pts=np.asarray(points,float)
 for k,p in enumerate(pts):
  t=pts[min(k+1,len(pts)-1)]-pts[max(0,k-1)];t/=np.linalg.norm(t)
  u=np.cross(t,[1,0,0]);u/=np.linalg.norm(u);w=np.cross(t,u)
  for a in np.linspace(0,2*math.pi,n,endpoint=False):v.append((p+radii[k]*(u*math.cos(a)+w*math.sin(a))).tolist())
 for k in range(len(pts)-1):
  for j in range(n):
   a=k*n+j;b=k*n+(j+1)%n;c=(k+1)*n+(j+1)%n;d=(k+1)*n+j
   f.extend([[a,b,c],[a,c,d]])
 f+=[list(range(n-1,-1,-1)),list(range((len(pts)-1)*n,len(pts)*n))]
 return manifold({'type':'polyhedron','vertices':v,'faces':f})

DM={r['name']:r for r in json.loads((B/'02_Data/Door_Manifest_V22.json').read_text(encoding='utf8'))['doors']}
for n in ['SITE_V20_INNER_GATE__LEAF_L','SITE_V20_INNER_GATE__LEAF_R']:
 e=E[n];r=DM[n];pivot=np.array(r['hinge_local_m']);angle=r['open_angle_deg']
 def close(m):return m.translate((-pivot).tolist()).rotate([0,0,-angle]).translate(pivot.tolist())
 def opened(m):return m.translate((-pivot).tolist()).rotate([0,0,angle]).translate(pivot.tolist())
 old=[close(manifold(p['geometry'])) for p in e['parts']];body=old[0]
 ps=[copy.deepcopy(p) for p in e['parts'][:14]]
 support=[];back=[]
 for j in [1,3,5]:
  bb=old[j].bounding_box();x0,y0,z0,x1,y1,z1=bb
  # Former reference rings floated 9.6 mm in front of the wooden slab.
  field=cube([x0,-11.589,z0],[x1-x0,.020,z1-z0]);support.append(field)
  back.append(rectframe(x0,x1,z0,z1,-11.501,.025,.013))
  checks.append({'check':n+' raised panel field root','positive_contact_m3':float((field^body).volume()),'old_ring_contact_m3':float((field^old[j]).volume())})
 ps.append(pp(opened(uni(support)),WOOD));ps.append(pp(opened(uni(back)),EDGE))
 # Three carved diamond bosses with a continuous inset backing in the lower field.
 bb=body.bounding_box();cx=(bb[0]+bb[3])/2;zs=.035
 diamond=[]
 for x in np.linspace(bb[0]+.27,bb[3]-.27,5):
  diamond.append(prismxz([[x-.052,zs],[x,zs+.047],[x+.052,zs],[x,zs-.047]],-11.612,.044))
 ps.append(pp(opened(uni(diamond)),EDGE))
 hx=bb[3]-.132 if n.endswith('_L') else bb[0]+.132
 zc=.895;zs=[-.365,-.33,-.25,-.17,-.11,.11,.17,.25,.33,.365]
 widths=[.011,.028,.036,.026,.024,.024,.026,.036,.028,.011]
 poly=[[hx-w,zc+z] for z,w in zip(zs,widths)]+[[hx+w,zc+z] for z,w in zip(zs[::-1],widths[::-1])]
 plate=prismxz(poly,-11.605,.039)
 fittings=[plate]
 for z in [.585,1.205]:
  fittings.append(orb([hx,-11.614,z],[.028,.014,.028]))
  fittings.append(cube([hx-.017,-11.655,z-.014],[.034,.060,.028]))
  for t in np.linspace(0,2*math.pi,8,endpoint=False):
   fittings.append(orb([hx+.024*math.cos(t),-11.619,z+.024*math.sin(t)],[.010,.009,.010]))
  # Recessed screw slots in the top/bottom mount are real geometry.
  fittings.append(cyl(hx,-11.622,z-.008,.008,.016,16))
 pts=[];rr=[]
 for t in np.linspace(0,1,37):
  pts.append([hx+.008*math.sin(t*2*math.pi),-11.648-.060*math.sin(math.pi*t),.585+.620*t])
  rr.append(.0115+.005*math.sin(math.pi*t)**2+.0025*math.cos(6*math.pi*t)**6)
 fittings.append(tube(pts,rr))
 handle=uni(fittings);contact=float((handle^body).volume());assert contact>1e-7
 ps.append(pp(opened(handle),BRASS))
 put(Q,n,ps,v23_door=True,operation='HINGED_INWARD',v23_detail='Modeled curved cast pull, shaped escutcheon, supported raised timber panels and rear panel mouldings; original hinge and 13 mm sill clearance retained')
 checks.append({'check':n+' integral cast escutcheon supported','contact_m3':contact,'operation':'HINGED_INWARD'})

# Small non-lettered scroll crest follows the real fixed wooden transom.
n='SITE_V21_GATE_REFERENCE_FIXED_TIMBER_TRANSOM';ps=copy.deepcopy(E[n]['parts']);crest=[]
for sign in [-1,1]:
 pts=[[6.6+sign*t,2.268+.032*math.sin(math.pi*t/.42)] for t in np.linspace(.035,.43,39)]
 crest.append(stroke(pts,.008,.035).translate([0,-11.791,0]))
 for k in range(5):
  x=6.6+sign*(.085+k*.057);z=2.278+.025*math.sin(k*.55)
  crest.append(petal(x,z,.067,.025,70 if sign>0 else 110,.031).translate([0,-11.788,0]))
crest.append(flower(6.6,2.30,.063,.038).translate([0,-11.791,0]))
# Embedded backing fixes the crest's root to the original timber/trim.
crest.append(cube([6.13,-11.770,2.235],[.94,.025,.067]))
ps.append(pp(uni(crest),EDGE));put(Q,n,ps,classification='FIXED_TIMBER_TRANSOM_WITH_MODELED_NON_LETTERED_SCROLL_CREST')

# Photo-like rounded paper lanterns. Their cords now stop at the pale soffit,
# replacing the old metre-long rods that pierced the roof.
n='SITE_V15_INNER_GATE_HANGING_LANTERNS';ps=[]
for x in [5.190238095238095,8.009761904761906]:
 y=-12.15;zc=2.115;r=.220;half=.205
 prof=[]
 for a in np.linspace(-math.pi/2+.03,math.pi/2-.03,33):prof.append([r*math.cos(a),zc+half*math.sin(a)])
 lantern=manifold({'type':'lathe','profile':prof,'segments':64}).translate([x,y,0]);ps.append(pp(lantern,'M_V23_GATE_LANTERN_RED'))
 fixtures=[]
 for z,rad,h in [(1.896,.058,.025),(2.309,.060,.018)]:fixtures.append(cyl(x,y,z,rad,h,48))
 for a in np.linspace(0,2*math.pi,12,endpoint=False):
  pts=[]
  for t in np.linspace(-1.48,1.48,31):pts.append([x+(r+.002)*math.cos(t)*math.cos(a),y+(r+.002)*math.cos(t)*math.sin(a),zc+half*math.sin(t)])
  fixtures.append(tube(pts,[.0027]*len(pts),8))
 ps.append(pp(uni(fixtures),'M_V23_GATE_LANTERN_GOLD'))
 a=abs((x-6.6)/2.6547);bottom=2.5409+.077*a*a+.638*a**7
 ps.append(pp(cyl(x,y,2.321,.004,bottom-2.321+.008,16),'M_Metal_Black'))
 tassels=[]
 for k in range(21):
  t=2*math.pi*k/21;rad=.039*math.sqrt((k+.5)/21);xx=x+rad*math.cos(t);yy=y+rad*math.sin(t)
  tassels.append(cyl(xx,yy,1.720+(.006*(k%3)),.0033,.197-.006*(k%3),10))
 tassels.append(cyl(x,y,1.892,.048,.030,32))
 ps.append(pp(uni(tassels),'M_V23_GATE_LANTERN_RED'))
 checks.append({'check':'Lantern suspension root fitted to pale soffit','x':x,'cord_top_m':bottom+.008,'roof_piercing_rod_removed':True})
put(Q,n,ps,classification='ROUNDED_RIBBED_LANTERNS_WITH_FINE_TASSELS_AND_SHORT_SOFFIT_SUSPENSION')

# The inherited disk was buried in the deep stone header at y=-11.60.
# The front and courtyard references each show a round ceiling fitting in
# the exposed soffit zone, clear of that header footprint.
disks=[]
for yy in [-12.00,-11.12]:
 disk=cyl(6.6,yy,2.524,.128,.019,64)
 rim=cyl(6.6,yy,2.520,.135,.009,64)-cyl(6.6,yy,2.519,.124,.012,64)
 disks.append(pp(disk+rim,'M_V21_GATE_CLOSED_PALE_SOFFIT'))
put(Q,'GATE_V22_PALE_CEILING_DISK',disks,classification='FRONT_AND_COURTYARD_CEILING_DISKS_IN_EXPOSED_SOFFIT_CLEAR_OF_HEADER',centres_local_y_m=[-12.00,-11.12])

Q['cameras']=[['V23_Inner_Gate_Ideal_Compare',[6.6,-16.7,1.7],[6.6,-11.65,1.7],74],['V23_Gate_Carved_Corner',[4.12,-13.55,1.10],[5.22,-11.80,1.0],62],['V23_Gate_Underside_Front',[5.9,-14.6,.80],[6.6,-11.80,2.10],79],['V23_Gate_Underside_Courtyard',[7.0,-8.6,1.15],[6.6,-11.60,2.18],80],['V23_Gate_Roof_Oblique',[3.2,-15.2,4.75],[6.65,-11.6,2.8],65],['V23_Gate_Hardware',[6.12,-13.40,.90],[6.50,-11.55,.85],42]]
Q['change_notes']=['内大门门叶补有实体承接的凸面芯板和背面压线，替换直杆拉手为有曲柄和花形底座的长铜拉手，随原内开门叶运动。','固定木上亮补非文字卷草冠饰；灯笼改细分圆体、细金线和细穗，吊线止于封闭檐底，清除穿出屋面的过长吊杆。','将原被厚门楣埋住的檐底圆盘按前后实景视角调整到两侧外露檐底，保留吊顶承接并避开门楣体积。']
save(Q,D,checks)

