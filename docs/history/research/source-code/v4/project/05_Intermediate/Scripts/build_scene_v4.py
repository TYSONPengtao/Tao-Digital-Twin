import sys,json,math,shutil,csv,copy
from pathlib import Path
W=Path(__file__).parent
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs','v4_audit_junction','v4_audit_safety']]
import numpy as np
from shapely.geometry import Polygon,LineString,Point,box as rect
from shapely.ops import unary_union
from scipy.spatial import cKDTree
import apply_junction_v4 as J,apply_safety_v4 as A
OLD=Path(r'E:\jz\JIA\Rebuild_V3');OUT=Path(r'E:\jz\JIA\Rebuild_V4')
for d in ['01_Source','02_PDF_Reference','03_Insta360_Frames','04_ContextCapture','05_Intermediate','06_Rhino','07_SketchUp','08_Export','09_Report','10_DJI_Reference','11_Construction_Reference']:(OUT/d).mkdir(parents=True,exist_ok=True)
S=json.loads((OLD/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'))
changes=J.apply(S)+A.apply(S)
E={e['name']:e for e in S['elements']}
S['name']='Production_1QK V4 construction coordination proposal'
S['status']='CONSTRUCTION_COORDINATION_PROPOSAL_PENDING_ENGINEERING_REVIEW'
S['materials'].update({'M_Waterproof':{'color':[60,75,81],'roughness':.9},'M_PVC_Rainwater':{'color':[214,215,209],'roughness':.55},'M_Sealant':{'color':[45,46,44],'roughness':.9}})
def part(g,m):return {'geometry':g,'material':m}
def box(x,y,z,w,d,h):return J._box(x,y,z,w,d,h)
def pg(p,z,h,m):return J._prisms(p,z,h,m)
def body(p,bottom,top,m):return part(J._polyhedron(p,bottom,top),m)
def add(name,parts,layer='70_EQUIPMENT',host='',**kw):
 e=dict(name=name,parts=parts,layer=layer,family='ARCH_MODEL',confidence='MEDIUM',source=kw.pop('source','V4 construction coordination proposal; sizes and fixings require design/field verification'),status='CONSTRUCTION_REVIEW_PROPOSAL',host=host,**kw);S['elements'].append(e);E[name]=e;return e
def record(id,note,parts,**kw):changes.append(dict(id=id,description=note,elements=parts,**kw))
def tube(a,b,ro=.055,ri=.05,n=24):
 a=np.array(a,float);v=np.array(b,float)-a;axis=v/np.linalg.norm(v);u=np.cross(axis,[0,0,1])
 if np.linalg.norm(u)<.1:u=np.cross(axis,[0,1,0])
 u/=np.linalg.norm(u);vv=np.cross(axis,u)
 pts=[(a+r*(math.cos(t)*u+math.sin(t)*vv)).tolist() for r in [ro,ri] for t in np.linspace(0,2*math.pi,n,endpoint=False)]
 verts=pts+[(np.array(p)+v).tolist() for p in pts];N=2*n;ff=[]
 for k in range(n):
  j=(k+1)%n
  ff += [[k,j,j+N,k+N],[n+j,n+k,n+k+N,n+j+N],[k,n+k,n+j,j],[k+N,j+N,n+j+N,n+k+N]]
 return {'type':'polyhedron','vertices':verts,'faces':ff}

# Outside sills are separate per-instance parts: slope goes toward the actual
# exterior side, including the rotated three-sided bay windows. Existing
# frame sizes are retained. Cut an actual 8x8 mm underside drip groove.
for e in list(S['elements']):
 if e['layer']!='31_WINDOW' or e['name'].startswith('WINDOW_STUDY'):continue
 d=S['definitions'][e['definition']];w=d['parameters']['Width'];h=d['parameters']['Height'];theta=e.get('angle',0)
 sign=-1 if e['name'].startswith(('BAY_','WINDOW_FRONT','WINDOW_RIGHT')) else 1
 dkey=e['definition']+('_V4_OUT_POSY' if sign==1 else '_V4_OUT_NEGY')
 if dkey not in S['definitions']:
  nd=copy.deepcopy(d)
  nd['parts']=[p for p in nd['parts'] if not(p['material']=='M_Stone' and p['geometry']['type']=='box' and p['geometry']['origin'][2]<0)]
  nd['parameters']['Sill_Drainage_Gradient']=.05;nd['source']+='; sill moved to per-instance sloping drainage node';S['definitions'][dkey]=nd
 e['definition']=dkey
 # Outward coordinate t goes from rear -60mm to projecting lip +180mm.
 def slope(x,y,sign=sign):return -.010-.05*(sign*y+.06)
 p=rect(-.04,-.06,w+.04,.18) if sign==1 else rect(-.04,-.18,w+.04,.06)
 inner=rect(-.04,.154,w+.04,.162) if sign==1 else rect(-.04,-.162,w+.04,-.154)
 parts=pg(p.difference(inner),-.060,.008,'M_Stone')+[body(p,lambda x,y:-.052,slope,'M_Stone')]
 head=rect(-.04,-.08,w+.04,.18) if sign==1 else rect(-.04,-.18,w+.04,.08)
 parts+=pg(head.difference(inner),h+.008,.008,'M_Stone')+pg(head,h+.016,.030,'M_Stone')
 seal=rect(-.006,-.048,w+.006,.048).difference(rect(.006,-.038,w-.006,.038))
 # Sill/frame seal is a separate trim component; no implicit hole drilling.
 parts+=pg(seal,-.010,.006,'M_Sealant')
 z=e['origin'][2];angle=e.get('angle',0)
 out=[-math.sin(angle)*sign,math.cos(angle)*sign]
 add('CONSTRUCTION_SILL_'+e['name'],parts,'31_WINDOW',host=e['name'],origin=e['origin'],angle=angle,finished_surface_role='window_sill',outward_xy=out,structural_datum_m=z,sill_gradient=.05,drip_groove_m=[.008,.008],source='GB55030-2022 4.5.3; external side checked against V3 facade; sill profile/groove inferred')
record('C13','Exterior window sills: 5% outward top and real 8x8mm underside drip groove; head drip and seal trim. Frame dimensions retained.',[e['name'] for e in S['elements'] if e['name'].startswith('CONSTRUCTION_SILL_')],dimension_status='Slope per code; groove dimensions are proposal')

# Low bay sills need protection measured from their climbable sill, not
# merely 900mm above room structure. Propose vertical, anti-climb guards.
for e in list(S['elements']):
 if not e['name'].startswith('BAY_WINDOW_'):continue
 d=S['definitions'][e['definition']];w=d['parameters']['Width'];pp=[]
 pp.append(part(box(.035,.070,.620,w-.070,.030,.030),'M_Metal_Black'))
 n=math.ceil((w-.10)/.125)
 for k in range(n+1):
  x=.05+(w-.10)*k/n
  pp.append(part(box(x-.0125,.072,.015,.025,.025,.605),'M_Metal_Black'))
 for xx in [.034,w-.062]:
  for zz in [.12,.60]:pp.append(part(box(xx,.035,zz,.028,.065,.020),'M_Metal_Black'))
 add('CONSTRUCTION_LOW_SILL_GUARD_'+e['name'],pp,'41_RAILING',host=e['name'],origin=e['origin'],angle=e.get('angle',0),guard_above_sill_m=.65,guard_condition='Assumed existing bay sill 600mm >450mm; verify sill and climbing surfaces',source='GB55038-2025 4.1.16; proposal for existing bay window sill safety; anchoring requires design')
record('C20','Low bay-window vertical guards proposed650mm above sill; vertical spacing <=100mm. Existing sill height and anchors require site verification.',[e['name'] for e in S['elements'] if e['name'].startswith('CONSTRUCTION_LOW_SILL_GUARD_')])

# Finished drainage surfaces. Separate waterproof coating and finish from
# unchanged structural slab. The terrace follows the drawn 2% crossfall.
balcony=rect(4.12,.12,8.88,2.00)
terrace=rect(.20,1.25,3.70,7.20)
for name,p,z,top,role,host,drain,out in [
 ('BALCONY',balcony,3.9,lambda x,y:3.910+.01*(y-.12),'balcony','BALCONY_STONE_JOINED',[8.82,.13], [0,-1]),
 ('TERRACE',terrace,7.5,lambda x,y:7.510+.02*(x-.20),'terrace','TERRACE_STONE_PARAPET',[.21,1.30],[-1,0])]:
 parts=pg(p,z,.002,'M_Waterproof')+[body(p,lambda x,y,z=z:z+.002,top,'M_Floor')]
 add('CONSTRUCTION_'+name+'_SLOPED_FINISH',parts,'22_SLAB',host=host,finished_surface_role=role,structural_datum_m=z,drain_xy=drain,outward_xy=out,waterproof_thickness_m=.002,finished_surface_max_m=max(top(x,y) for x,y in p.exterior.coords),source='D04 terrace i=0.02; GB55030-2022 4.5.4 balcony >=1%; finish/waterproof build-up and outlets are proposal')
 # Water outlet and external rain pipe reach a receiving pit; connection to
 # the offsite network is deliberately an unresolved design item.
 dx,dy=drain;drop=-.40
 add('CONSTRUCTION_'+name+'_RAINWATER_BRANCH',[part(tube([dx,dy,drop],[dx,dy,z+.01]),'M_PVC_Rainwater')],host='CONSTRUCTION_'+name+'_SLOPED_FINISH',nominal_DN_mm=100,penetration='Sleeve location and reinforcement to be reviewed before drilling',connection_status='Discharge receiver proposed; external sewer/network connection unverified')
record('C14','Balcony 1% and terrace 2% slope finishes with separate waterproof layers; discharge routes and sleeves need coordinated design. Structural slabs unchanged.',['CONSTRUCTION_BALCONY_SLOPED_FINISH','CONSTRUCTION_TERRACE_SLOPED_FINISH'])
# Ensure >=1.20m above highest proposed 80mm finish; model guard 1.30m.
for name in ['BALCONY_STONE_JOINED','BALCONY_STONE_COPING_JOINED','TERRACE_STONE_PARAPET']:
 e=E[name]
 for p in e['parts']:
  g=p['geometry']
  if g['type']=='prism_holes':
   if name=='BALCONY_STONE_JOINED':g['height']=1.17
   elif name=='BALCONY_STONE_COPING_JOINED':g['z']=5.07;g['height']=.13
   else:g['height']=1.30
 e.update(proposal_guard_height=1.30,finish_raise_allowance=.08,useful_guard_height_at_highest_finish=1.22)
record('C15','Guards rechecked from sloping proposed finish: structure-to-top1.30m, finish-to-top >=1.22m. Raised stonework load/fixing review remains required.',['BALCONY_STONE_JOINED','BALCONY_STONE_COPING_JOINED','TERRACE_STONE_PARAPET'])

# Five roof rainwater symbols from D04, coordinated to the CCM-based actual
# eaves. Paper positions are symbolic, not surveyed pipe centre coordinates.
roof_pipes=[('NW',-.28,10.12,10.82),('NE',13.32,10.12,10.43),('WING_SW',-.28,6.58,10.82),('MAIN_SW',3.05,.48,10.43),('SE',13.32,.48,10.43)]
for key,x,y,z in roof_pipes:
 parts=[part(tube([x,y,-.37],[x,y,z]),'M_PVC_Rainwater')]
 for zz in np.arange(.8,z-.4,1.5):parts+=pg(Point(x,y).buffer(.062,quad_segs=12).difference(Point(x,y).buffer(.055,quad_segs=12)),zz,.025,'M_Metal_Stainless')
 add('CONSTRUCTION_ROOF_DN100_'+key,parts,host='ROOF_MAIN_JOINED' if key in ['NE','MAIN_SW','SE'] else 'UTILITY_FLAT_ROOF_WEST',nominal_DN_mm=100,model_outer_diameter_m=.11,model_inner_diameter_m=.10,pipe_location_status='D04 symbol relocated to actual reconstructed eave; field verification required',hydraulic_sizing='Not calculated',source='D04 DN100 PVC rainwater pipe; five roof drain symbols, unspecified same. Not sewage WL-1/WL-2.')
 # Open collecting receiver rim with no false connection to a sewage pipe.
 rim=rect(x-.22,y-.22,x+.22,y+.22).difference(rect(x-.18,y-.18,x+.18,y+.18))
 add('CONSTRUCTION_RAINWATER_RECEIVER_'+key,pg(rim,-.87,.46,'M_Concrete')+pg(rect(x-.22,y-.22,x+.22,y+.22),-.92,.05,'M_Concrete'),host='CONSTRUCTION_ROOF_DN100_'+key,network_connection='Invert/outfall not surveyed; final connection needs drainage design')
record('C16','Five D04 DN100 roof rainwater locations rebuilt as hollow pipes with clamps and separate receivers; retain distinction from sanitary WL stacks. No pipe-capacity or external outfall assertion.',[e['name'] for e in S['elements'] if e['name'].startswith('CONSTRUCTION_ROOF_DN100_')])

# Main tile-roof eave U-gutters, slope 0.5% to nearest corner collection.
# The inner cavity is open; wall/base thicknesses are proposed 3mm metal.
gutter_parts=[]
for label,p,zfun in [
 ('N',rect(3.02,10.60,13.88,10.74),lambda x,y:10.365+.005*min(x-3.02,13.88-x)),
 ('S',rect(3.02,.46,13.88,.60),lambda x,y:10.365+.005*min(x-3.02,13.88-x)),
 ('W',rect(2.96,.60,3.10,10.60),lambda x,y:10.365+.005*min(y-.60,10.60-y)),
 ('E',rect(13.80,.60,13.94,10.60),lambda x,y:10.365+.005*min(y-.60,10.60-y))]:
 # Split at ridge of drainage gradient to keep the top faces planar.
 x0,y0,x1,y1=p.bounds
 ps=[rect(x0,y0,(x0+x1)/2,y1),rect((x0+x1)/2,y0,x1,y1)] if label in ['N','S'] else [rect(x0,y0,x1,(y0+y1)/2),rect(x0,(y0+y1)/2,x1,y1)]
 pp=[]
 for q in ps:
  pp.append(body(q,zfun,lambda x,y,zfun=zfun:zfun(x,y)+.003,'M_Metal_Stainless'))
  wall=q.difference(rect(x0+.003,y0+.003,x1-.003,y1-.003))
  for r in J._polys(wall):pp.append(body(r,lambda x,y,zfun=zfun:zfun(x,y)+.003,lambda x,y,zfun=zfun:zfun(x,y)+.103,'M_Metal_Stainless'))
 add('CONSTRUCTION_MAIN_EAVE_GUTTER_'+label,pp,'50_ROOF',host='ROOF_MAIN_JOINED',drainage_slope=.005,proposed_section_m=[.14,.103,.003],waterproof_status='Eave joint/flashing and sizing require specialist coordination')
for label,start,end in [('NE',[13.88,10.60,10.413],[13.32,10.12,10.413]),('NW',[3.02,10.60,10.413],[-.28,10.12,10.413]),('SE',[13.88,.60,10.413],[13.32,.48,10.413]),('MAIN_SW',[3.02,.60,10.413],[3.05,.48,10.413])]:
 add('CONSTRUCTION_GUTTER_CONNECTOR_'+label,[part(tube(start,end),'M_PVC_Rainwater')],host='CONSTRUCTION_ROOF_DN100_'+label)
record('C17','Proposed eave gutters close the rain collection route to main roof downpipes; U-section hollow, 0.5% fall. Section/fixings and rainfall calculation remain design items.',[e['name'] for e in S['elements'] if 'EAVE_GUTTER' in e['name']])

# Western utility roof has two D04 drain symbols. Provide an inward finish
# slope to its west collection line and explicit masonry scupper openings.
uf=rect(.10,6.80,3.65,9.80)
ufs=[rect(.10,6.80,3.65,8.30),rect(.10,8.30,3.65,9.80)]
add('CONSTRUCTION_UTILITY_ROOF_SLOPED_FINISH',pg(uf,10.8,.002,'M_Waterproof')+[body(p,lambda x,y:10.802,lambda x,y:10.810+.01*(x-.10)+.002*min(y-6.8,9.8-y),'M_Floor') for p in ufs],'50_ROOF',host='UTILITY_FLAT_ROOF_WEST',finished_surface_role='roof_finish',structural_datum_m=10.8,outward_xy=[-1,0],source='V3 CCM utility roof; proposed 1% crossfall and 0.2% longitudinal fall toward two scuppers; dimensions require design')
par=E['UTILITY_PARAPET_WEST'];gg=par['parts'][0]['geometry'];foot=Polygon(gg['outer'],gg['holes'])
cut=unary_union([rect(-.16,6.59,.11,6.77),rect(-.16,9.83,.11,10.01)])
par['parts']=pg(foot.difference(cut),10.8,.14,'M_Wall_Exterior')+pg(foot,10.94,.14,'M_Wall_Exterior')
par['construction_v4']='Two proposed130mm-high scuppers; parapet/support reinforcement and waterproof return require design'
for label,a,b in [('NW',[.09,9.83,10.85],[-.28,10.12,10.82]),('WING_SW',[.09,6.77,10.85],[-.28,6.58,10.82])]:
 add('CONSTRUCTION_UTILITY_SCUPPER_'+label,[part(tube(a,b),'M_PVC_Rainwater')],'50_ROOF',host='CONSTRUCTION_ROOF_DN100_'+label,penetration_status='Proposed masonry scupper; sleeves/seal and original wall condition to inspect')
record('C22','Western utility roof proposed 1% crossfall and two explicit scupper openings connecting separate roof rain pipes. Roof-access guard requirement and hydraulic/fixing checks remain unresolved.',['CONSTRUCTION_UTILITY_ROOF_SLOPED_FINISH','UTILITY_PARAPET_WEST','CONSTRUCTION_UTILITY_SCUPPER_NW','CONSTRUCTION_UTILITY_SCUPPER_WING_SW'])

# Exposed masonry support skirts below farm-shed bases. Their lower edges
# are interpolated from nearby source-derived earth, never called footings.
terrain=[p['geometry'] for e in S['elements'] if e['name'] in ['SITE_WEST_EARTH_COURTYARD'] for p in e['parts']]
tv=np.array([v for g in terrain for v in g['vertices']]);tree=cKDTree(tv[:,:2])
for i in [1,2,3]:
 e=E[f'SITE_SHED_{i}_POSTS'];pts=[]
 for p in e['parts']:
  v=np.array(p['geometry']['vertices']);pts.append(np.mean(v[:4,:2],axis=0))
 outline=Polygon(pts).buffer(.10,join_style=2);edge=outline.difference(outline.buffer(-.15,join_style=2));pp=[]
 for q in J._polys(edge):
  def toe(x,y):
   di,ind=tree.query([x,y],k=5);return min(-.50,float(np.mean(tv[ind,2]))-.04)
  pp.append(body(q,toe,lambda x,y:-.45,'M_Stone_Rubble'))
 add(f'CONSTRUCTION_SHED_{i}_EXPOSED_PLINTH',pp,'60_SITE',host=e['name'],classification='EXPOSED_MASONRY_SUPPORT_GEOMETRY_NOT_FOUNDATION_DESIGN',ground_status='Occluded soil elevation interpolated from adjacent photographed earth; field level required',foundation_design='Not supplied; do not infer bearing depth or reinforcement from this skirt')
record('C18','Shed floating-base gaps replaced with exposed masonry support geometry down to adjacent inferred earth; no foundation depth/load capacity claim.',[f'CONSTRUCTION_SHED_{i}_EXPOSED_PLINTH' for i in [1,2,3]])

# West tiled wall finish trimmed to actual masonry crown; detached frame
# backgrounds seated on slim measured-gap infill in the same finish family.
west=E['SITE_COURTYARD_WEST_WHITE_INSIDE'];g=west['parts'][0]['geometry'];v=np.array(E['SITE_COURTYARD_WEST_TILE_WALL']['parts'][0]['geometry']['vertices'])
def crown_at(y):
 # V3 west straight segment top slopes gently; interpolate the two end tops.
 ps=[p['geometry'] for p in E['SITE_COURTYARD_WEST_TILE_WALL']['parts'] if p['geometry']['type']=='polyhedron'];vv=np.vstack([p['vertices'] for p in ps]);near=vv[np.abs(vv[:,0])<.20]
 order=np.argsort(near[:,1]);a=near[order];bins=sorted(set(a[:,1]));tops=[max(a[np.isclose(a[:,1],yy),2]) for yy in bins]
 return float(np.interp(y,bins,tops))
if g['type']=='box':
 x,y,z=g['origin'];w,d,h=g['size'];west['parts']=[body(rect(x,y,x+w,y+d),lambda xx,yy:z,lambda xx,yy:min(z+h,crown_at(yy)),'M_Wall_Exterior')]
relief_changes=[]
for e in list(S['elements']):
 gap=.010 if e['name'].startswith('SITE_GATEHOUSE_CARVED_PANEL') else .005 if e['name'].startswith('SITE_SCREENWALL_STEPPED_PANEL') else .002 if e['name'].startswith('BALCONY_STONE_PANEL') else 0
 if gap:
  for p in e['parts']:
   for pt in p['geometry']['profile']:pt[1]+=gap
  e['installation_interface']='Relief rear face shifted to actual base face; fixing not structurally calculated'
  relief_changes.append(e['name'])
 if e['name'].startswith('SITE_WEST_TILE_WALL_PANEL'):
  gs=[p['geometry'] for p in e['parts']];y=gs[0]['origin'][1];oldtop=max(g['origin'][2]+g['size'][2] for g in gs);offset=crown_at(y+.45)-.055-oldtop
  for g in gs:g['origin'][2]+=offset
  e['installation_interface']='Decorative rectangle moved wholly below masonry crown; original height retained'
  relief_changes.append(e['name'])
# Metal vehicle-gate bottom rails: put 37.5mm above threshold instead of 2.5mm below.
gate_changes=[]
for e in S['elements']:
 if 'METAL' in e['name'] and 'GATE' in e['name']:
  for p in e.get('parts',[]):
   g=p['geometry']
   if g['type']=='polyhedron':
    arr=np.array(g['vertices']);a=np.array([-14.65,-8.37]);b=np.array([-12.88,-12.7275]);gu=(b-a)/np.linalg.norm(b-a);along=(arr[:,:2]-a)@gu;localz=arr[:,2]+.85+.35*along/np.linalg.norm(b-a)
    if np.ptp(along)>.8 and np.ptp(localz)<.10 and abs(np.mean(localz)-.02)<.02:
     for pt in g['vertices']:pt[2]+=.04
     gate_changes.append(e['name'])
record('C19','West wall finish and decorative frames now below crown; detached gate/screen/balcony relief backs seated on base faces; vehicle-gate low rail raised40mm for a working gap. Fixings and operation require review.',[west['name']]+sorted(set(gate_changes))+relief_changes)

# Main open court: a proposed finish zone with two orthogonal 0.2% falls
# to a corner receiver, laid over the unchanged photographed base terrain.
cp=rect(.40,-10.90,7.25,-.90)
def court_top(x,y):return -.445+.002*(x-.40)+.002*(y+10.90)
add('CONSTRUCTION_COURTYARD_DRAINAGE_FINISH',[body(cp,lambda x,y:-.45,court_top,'M_Site_Paving')],'60_SITE',host='SITE_MAIN_COURTYARD_PAVING',finished_surface_role='site_paving',structural_datum_m=-.45,drain_xy=[.40,-10.90],outward_xy=[-1,-1],drainage_scope='Proposed main open courtyard zone only, not all photographed site ground',source='GB55038-2025 3.2.5 >=0.2%; existing court datum from V3, corner discharge proposal')
rim=rect(.22,-11.08,.58,-10.72).difference(rect(.25,-11.05,.55,-10.75))
add('CONSTRUCTION_COURTYARD_DRAINAGE_RECEIVER',pg(rim,-.90,.455,'M_Concrete')+pg(rect(.22,-11.08,.58,-10.72),-.94,.04,'M_Concrete'),'60_SITE',host='CONSTRUCTION_COURTYARD_DRAINAGE_FINISH',outfall_status='Channel/outside-network invert requires survey and design')
record('C21','Main open-court grading zone rebuilt with 0.2% orthogonal falls to receiving corner; keep photographed terrain as base. External drainage connection remains unverified.',['CONSTRUCTION_COURTYARD_DRAINAGE_FINISH','CONSTRUCTION_COURTYARD_DRAINAGE_RECEIVER'])

S['cameras'] += [dict(name='CAM_13_Stair_Coordination',position=[14,2,9.9],target=[5.9,8.55,3.8],fov=58,status='CUTAWAY_REVIEW_CAMERA'),dict(name='CAM_14_Roof_Drainage',position=[21,20,24],target=[6,5,8.5],fov=48,status='PROPOSED_CONSTRUCTION_REVIEW')]

for e in S['elements']:
 if e.get('finished_surface_role'):
  for p in e['parts']:
   g=p['geometry'];p['finished_surface']=g['type']=='polyhedron' and (e['finished_surface_role']!='window_sill' or max(v[2] for v in g['vertices'])<0)

from fix_screen_relief_backing import fix_screen_relief_backing
changes+=fix_screen_relief_backing(S)

# Remove only volumes already owned by the receiving platform/floor. This
# preserves the exact union of concrete, retains underside bearing wedges,
# and eliminates coincident top faces in native/mesh viewers.
stair_interfaces=[]
for storey,mid,top in [(1,1.95,3.9),(2,5.7,7.5)]:
 for flight,receiver,za,zb in [(1,'STAIR_LANDING_F'+str(storey),mid-.14,mid),(2,'SLAB_JOINED_F'+str(storey+1),top-.13,top)]:
  e=E[f'STAIR_F{storey}_FLIGHT{flight}'];gg=e['parts'][0]['geometry'];yy=gg['profile'][0][1];wide=gg['vector'][1]
  xz=Polygon([(p[0],p[2]) for p in gg['profile']]);occupied=rect(3.9,za,5.2,zb) if flight==1 else rect(7.8,za,9,zb)
  repaired=xz.difference(occupied);pnew=[]
  for q in J._polys(repaired):
   coords=list(q.exterior.coords)[:-1]
   pnew.append(part({'type':'prism','profile':[[float(x),yy,float(z)] for x,z in coords],'vector':[0,wide,0]},'M_Concrete'))
  e['parts']=pnew;e['terminal_joint']='Receiving platform/slab owns shared concrete; waist underside wedge retained; no overlapping top faces'
  contact=repaired.boundary.intersection(occupied.boundary).length*wide
  union_error=repaired.union(occupied).symmetric_difference(xz.union(occupied)).area*wide
  assert union_error<1e-8
  r=dict(flight=e['name'],receiver=receiver,shared_volume_removed_m3=(xz.area-repaired.area)*wide,remaining_receiver_overlap_m3=repaired.intersection(occupied).area*wide,shared_contact_area_m2=contact,union_difference_volume_m3=union_error,union_geometry_changed=False)
  stair_interfaces.append(r)
record('C23','Stair end/platform and floor shared concrete removed from flight parts; receiving slabs retain it. Exterior union unchanged, coincident top faces eliminated.',[r['flight'] for r in stair_interfaces],checks=stair_interfaces)
(OUT/'09_Report/Stair_Interface_Overlap_QA.json').write_text(json.dumps(stair_interfaces,indent=2),encoding='utf-8')

for opening in S.get('openings',[]):
 name=opening['name']
 if name in ['DOOR_BACKROOM_F2_R','DOOR_BACKROOM_F3_R']:
  opening['previous_name']=name;opening['previous_origin']=opening['origin'];name=name.replace('BACKROOM','BATH')
 host=E.get(name)
 if host and 'definition' in host:
  opening.update(name=name,origin=host['origin'],angle=host.get('angle',0),definition=host['definition'])

S['v4_construction_changes']=changes
S['construction_review']={'role':'Construction coordination proposal; V3 remains the source-based existing-state model','standards':'See 11_Construction_Reference/Applicable_Constraints.json','not_approved':['Structural calculations and reinforcement','Foundation/soil bearing and retaining-wall design','Timber anchors and connections','Drainage pipe sizing and network invert','Site boundary ownership','Actual existing finish elevations and door passage'], 'review_method':'Source drawings + DJI evidence + CCM-linked geometry + geometric/native/exchange checks'}
(OUT/'05_Intermediate/Architecture_Scene.json').write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'09_Report/Construction_Changes_V4.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
print('V4 scene:',len(S['elements']),'elements,',len(changes),'change records',flush=True)
