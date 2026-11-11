"""V12 kitchen: photograph-grounded recessed timber facade and exposed timber roof.
The registered asymmetric roof, rear masonry and gate underlap remain exact.
"""
import sys,json,math,hashlib,ast,copy,collections
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,rhino3dm as rh
import export_v5 as ex
O=Path(__file__).parent;SP=Path(r'E:/jz/JIA/Rebuild_V11_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json');S=json.loads(SP.read_bytes());E={e['name']:e for e in S['elements']};D=json.loads((O/'Before_Donor.json').read_bytes())
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));func=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']];exec(compile(ast.Module(func,type_ignores=[]),'<solid_helpers>','exec'))
REFS=[D['source'],'E:/jz/VID_20260507_152114_00_001.insv','E:/jz/JIA/Rebuild_V12/07_Reference/Panorama/Kitchen_L0_1055s_Y+00_P+35.jpg','E:/jz/JIA/Rebuild_V12/07_Reference/Panorama/Kitchen_L0_1070s_Y+00_P+35.jpg','G:/处理/0005/DJI_0050.JPG','G:/处理/0001/DJI_0956.JPG','E:/0000问题合集/49886e5c-7c2b-4f84-99db-b8e1e5c3b26b.png']+[f'D:/Desktop/问题/屏幕截图 2026-10-11 {n}.jpg' for n in ['115520','115537','191926','191942']]
checks=[];excluded=[];mapping=[];contacts=[];nodes=[];solids=[];meta=[]
def check(n,ok,**kw):
 checks.append(dict(name=n,passed=bool(ok),**kw))
 if not ok:raise AssertionError((n,kw))
# Exact existing roof lower profile sampled from its retained mesh at Y=-7.1.
rv=np.asarray(E['SITE_KITCHEN_CHINESE_TILE_ROOF']['parts'][0]['geometry']['vertices']);q=rv[abs(rv[:,1]+7.1)<1e-7];xs=np.unique(q[:,0]);zs=np.array([q[abs(q[:,0]-x)<1e-8,2].min() for x in xs]);xorder=np.argsort(xs);xs=xs[xorder];zs=zs[xorder]
def roof_bottom(x,y):
 if x<=13.6:
  slopes=np.where(xs<11.5149,-.00177447,.003125757)
  return float(np.interp(x,xs,zs)+np.interp(x,xs,slopes)*(y+7.1))
 return 3.365916710451-.440835*(x-13.35)+.003125757*(y+11.65)
def before_roof(y):return 2.92+1.72*((y+.72)/3.325 if y<=2.605 else (5.93-y)/3.325)
def map_before(v):
 vv=np.asarray(v,float);xx=7.7+vv[:,1];yy=-11.87901+vv[:,0];zz=vv[:,2]-.4
 # Lower doors, sills, windows and post feet retain donor dimensions. Above
 # 3m donor Z, fit the roof-specific upper detail continuously to the actual roof.
 hi=vv[:,2]>3.0
 for j in np.where(hi)[0]:
  cap=roof_bottom(xx[j],yy[j])+.4-.040;oldcap=before_roof(vv[j,1]);ratio=max(.05,min(1.,(cap-3)/(oldcap-3))) if oldcap>3 else 1.
  zz[j]=3.+(vv[j,2]-3)*ratio-.4
 return np.c_[xx,yy,zz]
def poly_prism(top,bot):
 xx=[6.90,*xs[(xs>6.9)&(xs<14.7)].tolist(),14.7];ys=np.linspace(-12.15,-2.05,42).tolist();v=[]
 for y in ys:
  for x in xx:v.append([x,y,top(x,y)])
 for y in ys:
  for x in xx:v.append([x,y,bot])
 n=len(xx);ny=len(ys);N=n*ny;fs=[]
 for j in range(ny-1):
  for i in range(n-1):
   k=j*n+i;fs.extend([[k,k+1,k+n+1,k+n],[N+k,N+k+n,N+k+n+1,N+k+1]])
 for i in range(n-1):fs.extend([[i,N+i,N+i+1,i+1],[(ny-1)*n+i,(ny-1)*n+i+1,N+(ny-1)*n+i+1,N+(ny-1)*n+i]])
 for j in range(ny-1):
  k=j*n;fs.extend([[k,k+n,N+k+n,N+k],[k+n-1,N+k+n-1,N+k+2*n-1,k+2*n-1]])
 return oriented(dict(type='polyhedron',vertices=v,faces=fs))
below=manifold(poly_prism(lambda x,y:roof_bottom(x,y)-.028,-.600))
def add_node(name,rows,cls):
 e=dict(name=name,parts=[],layer='60_SITE',family='SITE_MODEL',confidence='MEDIUM',classification=cls,source='; '.join(REFS),status='V12_PHOTO_CONFIRMED_TIMBER_RELATION; UNMEASURED_SECTIONS; EXISTING_ASYMMETRIC_ROOF_RETAINED')
 nodes.append(e)
 for g,mat,label in rows:
  a=manifold(g);aa=a^below
  if aa.is_empty() or aa.volume()<1e-11:excluded.append(dict(name=label,reason='Above actual registered roof or tiny non-visible donor fragment'));continue
  if a.volume()-aa.volume()>1e-10:g=fromman(aa);a=manifold(g)
  p=dict(geometry=g,material=mat,source_part_name=label);e['parts'].append(p);solids.append(a);meta.append((e,p,label))
 return e
groups=collections.defaultdict(list);donor_map=[]
for row in D['parts']:
 code=row['layer'].split('_')[0];g=row['geometry'];v=map_before(g['vertices']);fs=np.asarray(g['faces'],int)
 if code in ['03','20','27','28','31','33','34'] or (code=='04' and not row['name'].startswith('BEAM_FRONT_')):
  excluded.append(dict(name=row['name'],reason='Replaced by actual near-photo V12 stone bases or two distinct fret levels'));continue
 if code=='05' and '上部格棂' in row['name']:
  excluded.append(dict(name=row['name'],reason='115520 real near photo shows solid door upper panel and curved moulding, not a rectangular timber grid'));continue
 # Rhino mesh topology welds seams independently from render indices; merge
 # coincident double-precision donor seam vertices before solid-kernel import.
 _,ix,inv=np.unique(np.round(v,8),axis=0,return_index=True,return_inverse=True);v=v[ix];fs=inv[fs];fs=fs[(fs[:,0]!=fs[:,1])&(fs[:,1]!=fs[:,2])&(fs[:,0]!=fs[:,2])]
 try:
  g=oriented(dict(type='polyhedron',vertices=v.tolist(),faces=fs.tolist()));a=manifold(g)
 except Exception as err:excluded.append(dict(name=row['name'],reason='Closed donor tessellation rejected by exact solid kernel',detail=str(err)));continue
 mat='M_V12_Kitchen_'+row['material'];groups[code].append((g,mat,row['name']));donor_map.append(dict(name=row['name'],source_id=row['source_id'],layer=row['layer']))
for code,rows in groups.items():
 if code!='05':add_node('SITE_KITCHEN_V12_BEFORE_WOOD_'+code,rows,'PHOTO_GUIDED_RECESSED_TIMBER_FACADE' if code not in ['03','26'] else 'STONE_BASE_AND_WOOD_POST_FOOT')
def boxg(a,b):
 x0,y0,z0=a;x1,y1,z1=b
 return oriented(dict(type='polyhedron',vertices=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]],faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]))
def beam(a,b,w,h):
 a=np.array(a);b=np.array(b);u=(b-a)/np.linalg.norm(b-a);v=np.cross(u,[0,0,1]);
 if np.linalg.norm(v)<.01:v=np.array([0.,1.,0.])
 v/=np.linalg.norm(v);up=np.cross(u,v);vv=[(p+v*w*ss/2+up*h*tt/2).tolist() for p in [a,b] for ss,tt in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 return oriented(dict(type='polyhedron',vertices=vv,faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]))
def cyl(a,b,r,n=32):
 a=np.array(a);b=np.array(b);u=(b-a)/np.linalg.norm(b-a);v=np.cross(u,[0,0,1]);
 if np.linalg.norm(v)<.01:v=np.array([0.,1.,0.])
 v/=np.linalg.norm(v);t=np.cross(u,v);vv=[(p+r*(v*np.cos(q)+t*np.sin(q))).tolist() for p in [a,b] for q in np.linspace(0,math.tau,n,endpoint=False)];fs=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[j,(j+1)%n,(j+1)%n+n,j+n] for j in range(n)]
 return oriented(dict(type='polyhedron',vertices=vv,faces=fs))
wood='M_Timber_Honey';dark='M_V12_Kitchen_WOOD_DARK';stone='M_Stone_Frame';newrows=[]
stations=[-11.24,-8.26,-5.94,-2.96]
for k,y in enumerate(stations):
 # Real 191942 near view shows exposed transverse cambered/slope-following
 # timbers and longitudinal purlins, without a triangulated tie-rod truss.
 newrows.append((cyl([12.95,y,-.22],[12.95,y,roof_bottom(12.95,y)-.22],.13),wood,f'露明木架{k}_后圆柱'))
 newrows.append((boxg([12.76,y-.19,-.40],[13.14,y+.19,-.20]),stone,f'露明木架{k}_后柱石础'))
 for j,(x0,x1) in enumerate([(9.04,11.515),(11.515,13.06)]):
  newrows.append((beam([x0,y,roof_bottom(x0,y)-.29],[x1,y,roof_bottom(x1,y)-.29],.17,.23),wood,f'露明木架{k}_月梁坡段{j}'))
 newrows.append((boxg([8.97,y-.13,2.25],[9.27,y+.13,roof_bottom(9.1,y)-.12]),wood,f'露明木架{k}_前柱承木'))
 for x in [9.1,10.30,11.515,12.5,13.0]:
  zz=roof_bottom(x,y)-.28;newrows.append((boxg([x-.12,y-.14,zz-.18],[x+.12,y+.14,zz+.055]),wood,f'抬梁架{k}_抱檩木{x}'))
 # Front porch post/beam gets a 15mm joint filler from the donor's small gap.
 newrows.append((cyl([7.891,y,2.316],[7.891,y,2.387],.142),wood,f'檐廊{k}_柱头承木补接'))
 newrows.append((beam([7.78,y,2.48],[9.17,y,2.89],.16,.20),wood,f'檐廊{k}_外内排挑梁'))
add_node('SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES',newrows,'PHOTO_CONFIRMED_EXPOSED_TRANSVERSE_TIMBER_AND_ROUND_PURLIN_NO_TRIANGULATED_TRUSS')
pp=[]
for k,x in enumerate([7.891,9.1,10.30,11.515,12.5,13.0]):
 pp.append((cyl([x,-11.24,roof_bottom(x,-11.24)-.205],[x,-2.96,roof_bottom(x,-2.96)-.205],.115),wood,f'纵向圆檩{k}'))
add_node('SITE_KITCHEN_V12_LONGITUDINAL_ROUND_PURLINS',pp,'ROUND_PURLINS_SUPPORTING_REPEATED_EXPOSED_RAFTERS')
pp=[(beam([11.515,-11.24,roof_bottom(11.515,-11.24)-.34],[11.515,-2.96,roof_bottom(11.515,-2.96)-.34],.19,.25),wood,'纵向脊下承枋')]
add_node('SITE_KITCHEN_V12_RIDGE_UNDER_TIMBER_BEAM',pp,'PHOTO_CONFIRMED_LONGITUDINAL_RIDGE_UNDER_BEAM')
pp=[]
for k,y in enumerate(np.arange(-11.12,-2.91,.18)):
 for j,(x0,x1) in enumerate([(7.12,11.515),(11.515,13.48)]):
  xx=[x0]+xs[(xs>x0)&(xs<x1)].tolist()+[x1];vv=[]
  for x in xx:
   for dy,dz in [(-.032,-.120),(.032,-.120),(.032,-.020),(-.032,-.020)]:vv.append([x,float(y+dy),roof_bottom(x,float(y+dy))+dz])
  fs=[[0,3,2,1],[len(vv)-4,len(vv)-3,len(vv)-2,len(vv)-1]]
  for h0 in range(len(xx)-1):
   for t in range(4):fs.append([h0*4+t,h0*4+(t+1)%4,(h0+1)*4+(t+1)%4,(h0+1)*4+t])
  pp.append((oriented(dict(type='polyhedron',vertices=vv,faces=fs)),dark,f'密排露明木椽{k:02d}_{j}'))
add_node('SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS',pp,'PHOTO_CONFIRMED_VISIBLE_DENSE_RAFTERS_NO_SUSPENDED_CEILING')
# Thin stepped threshold preserves the original -0.4m kitchen floor datum.
pp=[]
for j,(ya,yb) in enumerate([(-8.22,-7.26),(-6.94,-5.98)]):pp.append((boxg([8.99,ya,-.4],[9.22,yb,-.345]),stone,f'内退木门{j}_青石门槛'))
add_node('SITE_KITCHEN_V12_RECESSED_DOOR_STONE_THRESHOLDS',pp,'TWO_RECESSED_TIMBER_DOOR_THRESHOLDS')
# Rebuild every outer column base explicitly. The donor's 15mm base lift and
# 5mm post-to-base gap must not be accepted merely because its roof is connected.
pp=[]
for k,y in enumerate(stations):pp.append((boxg([7.715,y-.183,-.400],[8.080,y+.183,-.145]),stone,f'檐廊圆柱{k}_落地青石柱础'))
base_node=add_node('SITE_KITCHEN_V12_GROUNDED_OUTER_COLUMN_STONE_BASES',pp,'FOUR_EXPLICIT_GROUNDED_STONE_BASES_DIRECTLY_SUPPORTING_ROUND_COLUMNS')
# Closed rectangular bars in the facade Y/Z plane. Each segment remains an
# independently editable closed solid. Rings use joined segments instead of a
# tube with coincident first/last caps, which was invalid in the before donor.
fine='M_V12_Kitchen_GOLDEN_WOOD';fretrows=[];oct_records=[];fret_union_records=[]
def union_fret(rows,label,by_panel=True):
 # Joined tracery must have one exterior surface at a crossing, not two
 # overlapping front caps. Keep glass and other materials entirely separate.
 buckets=collections.defaultdict(list)
 for g,mat,n in rows:buckets[(mat,n.split('_')[0] if by_panel else label)].append((g,n))
 out=[]
 for (mat,panel),rs in buckets.items():
  a=mf.Manifold.batch_boolean([manifold(g) for g,n in rs],mf.OpType.Add)
  check('fret_union_valid_'+label+'_'+panel,a.status()==mf.Error.NoError and not a.is_empty())
  parts=a.decompose()
  for k,z in enumerate(parts):out.append((fromman(z),mat,panel+f'_同材质连续木格并集_{k}'))
  fret_union_records.append(dict(group=label,panel=panel,material=mat,input_parts=len(rs),closed_output_components=len(parts),same_plane_crossings_removed=True,glass_included=False))
 return out
def path_offsets(pts,w,closed=False):
 # True planar miter joints, rather than overlapping rectangular end caps.
 # Adjacent return bars meet in the same section without triangular corners.
 p=np.asarray(pts,float);ds=np.roll(p,-1,axis=0)-p if closed else np.diff(p,axis=0)
 ds/=np.linalg.norm(ds,axis=1)[:,None];ns=np.c_[-ds[:,1],ds[:,0]];offs=[]
 for j in range(len(p)):
  if not closed and j==0:n=ns[0]
  elif not closed and j==len(p)-1:n=ns[-1]
  else:
   prev=ns[(j-1)%len(ns)];nxt=ns[j%len(ns)];s=prev+nxt;n=s/np.dot(s,nxt)
  offs.append(n*w/2)
 return p,np.asarray(offs)
def facade_prism(q,x,depth):
 vv=[[x+dx,*map(float,yz)] for dx in [-depth/2,depth/2] for yz in q];n=len(q)
 return oriented(dict(type='polyhedron',vertices=vv,faces=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[j,(j+1)%n,(j+1)%n+n,j+n] for j in range(n)]))
def pathbars(pts,label,rows,w=.023,x=8.988,depth=.055):
 closed=np.linalg.norm(np.asarray(pts[0])-pts[-1])<1e-9
 p,of=path_offsets(pts[:-1] if closed else pts,w,closed)
 for j in range(len(p) if closed else len(p)-1):
  j1=(j+1)%len(p);q=[p[j]-of[j],p[j1]-of[j1],p[j1]+of[j1],p[j]+of[j]]
  rows.append((facade_prism(q,x,depth),fine,label+f'_棂段{j}'))
def frame(ya,yb,za,zb,label,rows,w=.025,x=8.988,depth=.055):pathbars([(ya,za),(yb,za),(yb,zb),(ya,zb),(ya,za)],label,rows,w,x,depth)
def octagon(cy,cz,ry,rz,label,rows,x=8.988):
 yy=ry*.42;zz=rz*.42;pts=[(cy-yy,cz-rz),(cy+yy,cz-rz),(cy+ry,cz-zz),(cy+ry,cz+zz),(cy+yy,cz+rz),(cy-yy,cz+rz),(cy-ry,cz+zz),(cy-ry,cz-zz)]
 # One continuous closed octagonal ring with a real inner opening. Front and
 # rear annular faces share vertices at all eight miters: no coplanar pieces,
 # butt-joint holes, or shadow triangles at a diagonal joint.
 p,of=path_offsets(pts,.023,True);outer=p-of;inner=p+of;n=8
 vv=[[x+dx,*map(float,q)] for dx in [-.055/2,.055/2] for contour in [outer,inner] for q in contour];fs=[]
 for j in range(n):
  k=(j+1)%n
  fs.extend([[j,k,n+k,n+j],[2*n+j,3*n+j,3*n+k,2*n+k],[j,2*n+j,2*n+k,k],[n+j,n+k,3*n+k,3*n+j]])
 rows.append((oriented(dict(type='polyhedron',vertices=vv,faces=fs)),fine,label+'_连续一体八角环'))
 oct_records.append(dict(name=label,center=[x,cy,cz],radius_y_m=ry,radius_z_m=rz,continuous_closed_ring=True,shared_vertices_at_miters=True))
 return pts
window_spans=[(.699,1.572),(1.692,2.566),(2.686,3.559),(5.999,6.872),(6.992,7.866),(7.986,8.859)]
for k,(a,b) in enumerate(window_spans):
 ya=-11.87901+a+.040;yb=-11.87901+b-.040;cy=(ya+yb)/2
 if k in [0,2,3,5]:
  for h,cz in enumerate([.93,1.58]):
   ry=.205;rz=.205;octagon(cy,cz,ry,rz,f'木窗{k}_双八角{h}',fretrows)
   # Four corner returns connect the octagon to the window perimeter rails.
   for side in [-1,1]:
    edge=ya if side<0 else yb
    for vertsign in [-1,1]:
     outerz=.62 if h==0 and vertsign<0 else 1.84 if h==1 and vertsign>0 else (cz+vertsign*.285)
     pathbars([(edge,outerz),(cy+side*.285,outerz),(cy+side*.285,cz+vertsign*.120),(cy+side*.120,cz+vertsign*.120),(cy+side*.120,cz+vertsign*.205)],f'木窗{k}_八角{h}_角回纹{side}_{vertsign}',fretrows)
   for side in [-1,1]:
    edge=ya if side<0 else yb;pathbars([(edge,cz),(cy+side*.205,cz)],f'木窗{k}_八角{h}_横接棂{side}',fretrows)
  # Rectilinear interlocking middle returns between the two octagons.
  frame(cy-.255,cy+.255,1.205,1.325,f'木窗{k}_中联双方框',fretrows,.021)
  pathbars([(ya,1.26),(yb,1.26)],f'木窗{k}_中央贯通棂',fretrows,.021)
 else:
  # Actual larger central pane remains visually open; only the edge returns.
  for side in [-1,1]:
   edge=ya if side<0 else yb;pathbars([(edge,.65),(edge-side*.09,.65),(edge-side*.09,.79),(edge-side*.15,.79),(edge-side*.15,1.70),(edge-side*.09,1.70),(edge-side*.09,1.83),(edge,1.83)],f'宽窗{k}_周边回纹{side}',fretrows)
add_node('SITE_KITCHEN_V12_PHOTO_DOUBLE_OCTAGON_AND_EDGE_FRET_WINDOWS',union_fret(fretrows,'DOUBLE_OCTAGON_WINDOWS'),'115537_PHOTO_TWO_STACKED_OCTAGONS_WITH_RECTILINEAR_PERIPHERAL_RETURNS')
pp=[]
for k,(a,b) in enumerate(window_spans):pp.append((boxg([9.035,-11.87901+a+.020,.58],[9.075,-11.87901+b-.020,1.87]),'M_V12_Kitchen_GLASS_PALE',f'木窗{k}_后衬透明玻璃'))
add_node('SITE_KITCHEN_V12_PHOTO_ATTACHED_WINDOW_GLAZING',pp,'PHOTO_CONFIRMED_RECESSED_GLAZING_ATTACHED_TO_REAL_WOOD_WINDOW_PERIMETER')
# Separate lower narrow horizontal transoms above eight doors/windows.
spans=[(.699,1.572),(1.692,2.566),(2.686,3.559),(3.659,4.619),(4.939,5.899),(5.999,6.872),(6.992,7.866),(7.986,8.859)]
narrow=[]
for k,(a,b) in enumerate(spans):
 ya=-11.87901+a-.03;yb=-11.87901+b+.03;frame(ya,yb,1.99,2.23,f'窄横格{k}_樘框',narrow,.032,x=9.060,depth=.075)
 for h,cc in enumerate([ya+(yb-ya)*.25,ya+(yb-ya)*.75]):frame(cc-.116,cc+.116,2.045,2.175,f'窄横格{k}_双方形{h}',narrow,.019,x=9.02)
 for zz in [2.075,2.14]:pathbars([(ya,zz),(yb,zz)],f'窄横格{k}_贯通双横棂{zz}',narrow,.018,x=9.019)
add_node('SITE_KITCHEN_V12_PHOTO_NARROW_DOUBLE_SQUARE_TRANSOMS',union_fret(narrow,'NARROW_TRANSOMS'),'115520_PHOTO_NARROW_DOUBLE_SQUARE_DOOR_AND_WINDOW_HEAD_TRANSOMS')
# Broad upper pierced band at 2.40..3.06m, separated by a solid timber header
# from the lower narrow transoms. No masonry fills the openings.
wide=[];yy0=-11.87901+.639;yy1=-11.87901+8.919
wide.append((boxg([9.008,yy0,2.245],[9.168,yy1,2.40]),wood,'宽窄格窗之间贯通实木额枋'))
frame(yy0,yy1,2.405,3.065,'上部宽格窗通长樘框',wide,.05,x=9.082,depth=.130)
for k in range(12):
 a=yy0+(yy1-yy0)*k/12;b=yy0+(yy1-yy0)*(k+1)/12;cy=(a+b)/2
 frame(a+.010,b-.010,2.423,3.045,f'上宽格窗{k}_单元框',wide,.020,x=9.035,depth=.080)
 octagon(cy,2.733,.230,.215,f'上宽格窗{k}_八角格心',wide,x=9.036)
 for side in [-1,1]:
  edge=a+.025 if side<0 else b-.025
  for sg in [-1,1]:
   z=2.453 if sg<0 else 3.015
   pathbars([(edge,z),(cy+side*.16,z),(cy+side*.16,2.733+sg*.260),(cy+side*.280,2.733+sg*.260),(cy+side*.280,2.733+sg*.088),(cy+side*.230,2.733+sg*.088)],f'上宽格窗{k}_角回纹{side}_{sg}',wide,.019,x=9.036)
add_node('SITE_KITCHEN_V12_PHOTO_UPPER_WIDE_OCTAGON_FRET_BAND',union_fret(wide,'BROAD_UPPER_BAND',False),'191926_PHOTO_BROAD_UPPER_PIERCED_BAND_SEPARATE_FROM_NARROW_LOWER_TRANSOMS')
pp=[]
for k,y in enumerate([yy0,yy0+2.98,-7.10001,yy0+5.30,yy1]):pp.append((cyl([9.097,y,2.20],[9.097,y,roof_bottom(9.097,y)-.09],.115 if k!=2 else .153),wood,f'内退立面{k}_上部落柱承宽额枋'))
add_node('SITE_KITCHEN_V12_UPPER_FACADE_COLUMN_CONTINUATIONS',pp,'UPPER_COLUMNS_ATTACH_BOTH_FRET_LEVELS_TO_EXPOSED_ROOF_TIMBERS')
# Separate the already positioned moving door wood from all fixed frame rails.
# 115520 confirms the upper door's curved raised moulding. Lower carvings and
# hinge opening direction are not sufficiently visible and are not invented.
door_records=[]
for k,cy in enumerate([-7.74001,-6.46001],1):
 did=f'DOOR_COURTYARD_KITCHEN_V12_{k}';source_prefix=f'DOOR_{k}_'
 fixed=[r for r in groups['05'] if r[2].startswith(source_prefix) and any(t in r[2] for t in ['框左挺','框右挺','框顶枋'])]
 moving=[r for r in groups['05'] if r[2].startswith(source_prefix) and r not in fixed]
 for h,(dy,dz,w) in enumerate([(0.,0.,.016),(0.,.031,.013),(0.,.060,.011)]):
  # The pair rises toward the central door meeting direction and flattens at
  # the outside edge. Each leaf is a mirrored half curve, not its own arch.
  profile=[(-.37,1.51),(-.30,1.51),(-.22,1.51),(-.16,1.545),(-.08,1.58),(0.,1.615),(.10,1.66),(.20,1.69),(.29,1.705),(.37,1.71)]
  pts=[(cy+(yy if k==1 else -yy),zz+dz) for yy,zz in profile]
  pathbars(pts,f'DOOR_{k}_实景上部弧形压条{h}',moving,w,x=9.048,depth=.055)
 frame_node=add_node(did+'__FRAME',fixed,'FIXED_TIMBER_DOOR_FRAME')
 leaf_node=add_node(did+'__LEAF',moving,'MOVABLE_SOLID_TIMBER_DOOR_WITH_PHOTO_CURVED_MOULDING')
 hinge=[9.074,(-8.17001 if k==1 else -6.09001),-.372]
 for node in [frame_node,leaf_node]:node.update(door_id=did,parent_id=did,role='FRAME' if node is frame_node else 'LEAF',interactive_role='FRAME' if node is frame_node else 'LEAF',hinge_origin_local_m=hinge,hinge_axis_local=[0,0,1],hinge_evidence='Reference axis at existing frame edge; handedness/opening direction unconfirmed in near photo')
 # Parts use absolute LOCAL vertices, so do not give the element an `origin`
 # transform that could inadvertently translate the already positioned mesh.
 leaf_node['pivot_world_m']=hinge;leaf_node['pivot_local_m']=[0,0,0];leaf_node['interaction']='HINGED_LEAF';leaf_node['hinge_axis']=[0,0,1];leaf_node['open_angle_degrees_provisional']=90 if k==1 else -90
 door_records.append(dict(door_id=did,frame_node=frame_node['name'],leaf_node=leaf_node['name'],hinge_origin_local_m=hinge,hinge_axis_local=[0,0,1],world_geometry_preserved=True,opening_direction_field_confirmed=False,frame_parts=len(frame_node['parts']),leaf_parts=len(leaf_node['parts'])))
# Confirmed visible fixed services in 191926/191942. These dimensions are
# reference fits only. Furniture and hidden kitchen equipment are not inferred.
def frustumz(cx,cy,z0,z1,r0,r1,n=32):
 vv=[[cx+r*math.cos(t),cy+r*math.sin(t),z] for r,z in [(r0,z0),(r1,z1)] for t in np.linspace(0,math.tau,n,endpoint=False)]
 return oriented(dict(type='polyhedron',vertices=vv,faces=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[j,(j+1)%n,(j+1)%n+n,j+n] for j in range(n)]))
fan_xy=[11.515,-7.10001];fan_attach=roof_bottom(*fan_xy)-.455
pp=[(cyl([*fan_xy,fan_attach-.05],[*fan_xy,fan_attach+.025],.095),'M_PVC_Rainwater','实景三叶吊扇_梁下吊座'),(cyl([*fan_xy,3.265],[*fan_xy,fan_attach],.018),'M_Metal_Stainless','实景三叶吊扇_竖直吊杆'),(cyl([*fan_xy,3.155],[*fan_xy,3.300],.13),'M_PVC_Rainwater','实景三叶吊扇_电机壳')]
add_node('SITE_KITCHEN_V12_PHOTO_CEILING_FAN_FIXED_MOUNT',pp,'191926_191942_PHOTO_BEAM_HUNG_THREE_BLADE_FAN_FIXED_CANOPY_AND_ROD')
pp=[(cyl([*fan_xy,3.115],[*fan_xy,3.185],.105),'M_PVC_Rainwater','实景三叶吊扇_独立转子轮毂')]
for j in range(3):
 t=j*math.tau/3;u=np.array([math.cos(t),math.sin(t)]);v=np.array([-math.sin(t),math.cos(t)]);p=[np.asarray(fan_xy)+u*r+v*s for r,s in [(.075,-.045),(.21,-.055),(.605,-.095),(.655,-.050),(.655,.050),(.605,.095),(.21,.055),(.075,.045)]];n=len(p);vv=[[float(q[0]),float(q[1]),z] for z in [3.122,3.142] for q in p];fs=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[k,(k+1)%n,(k+1)%n+n,k+n] for k in range(n)]
 pp.append((oriented(dict(type='polyhedron',vertices=vv,faces=fs)),'M_PVC_Rainwater',f'实景三叶吊扇_活动扇叶{j+1}'))
fan_node=add_node('SITE_KITCHEN_V12_PHOTO_CEILING_FAN_THREE_BLADE_ROTOR',pp,'191926_191942_PHOTO_THREE_BLADE_FAN_SEPARATE_EDITABLE_ROTOR');fan_node.update(pivot_world_m=[*fan_xy,3.132],hinge_axis=[0,0,1],interaction='CONTINUOUS_ROTATION_ROTOR')
light_records=[]
for j,y in enumerate([stations[0],stations[-1]],1):
 x=10.30;beam_center=roof_bottom(x,y)-.29;zc=beam_center-.11
 pp=[(cyl([x,y,zc-.012],[x,y,zc+.032],.052),'M_Metal_Stainless',f'实景侧灯{j}_梁下固定座'),(cyl([x,y,3.20],[x,y,zc+.010],.016),'M_Metal_Stainless',f'实景侧灯{j}_明装灯杆'),(frustumz(x,y,3.045,3.222,.115,.045),'M_Metal_Stainless',f'实景侧灯{j}_小反光罩'),(cyl([x,y,3.025],[x,y,3.062],.050),'M_PVC_Rainwater',f'实景侧灯{j}_外露灯头')]
 add_node(f'SITE_KITCHEN_V12_PHOTO_EXPOSED_SIDE_LAMP_{j}',pp,'191926_191942_PHOTO_SMALL_EXPOSED_LIGHT_FITTING');light_records.append(dict(lamp=j,local_center_m=[x,y,3.10],mount_lower_z_m=zc,reference_dimensions_not_measured=True))
pp=[cyl([9.247,-7.10001,1.985],[9.247,-7.10001,2.34],.013)]
for y in [stations[0],stations[-1]]:
 pp.extend([cyl([9.247,-7.10001,2.34],[9.247,y,2.34],.013),cyl([9.247,y,2.34],[10.30,y,2.34],.013),cyl([10.30,y,2.34],[10.30,y,3.22],.013)])
pipe=mf.Manifold.batch_boolean([manifold(g) for g in pp],mf.OpType.Add)
add_node('SITE_KITCHEN_V12_PHOTO_COLUMN_SURFACE_CONDUIT',[(fromman(g),'M_PVC_Rainwater',f'实景中央柱明敷线管_接两侧灯_{j}') for j,g in enumerate(pipe.decompose())],'191926_PHOTO_COLUMN_SURFACE_CONDUIT_ATTACHED_TO_TIMBER_AND_SIDE_LAMPS')
# Protect exact retained roof/gate/wall nodes; retire only the obsolete simplified facade.
remove=[n for n in E if n.startswith(('SITE_KITCHEN_TIMBER_COLUMNS_AND_BEAMS','SITE_KITCHEN_TIMBER_DOOR_','SITE_KITCHEN_TIMBER_SILL_PANEL_','SITE_KITCHEN_LATTICE_','SITE_KITCHEN_TRANSOM_','SITE_KITCHEN_EXPOSED_TIMBER_ROOF_FRAMING','SITE_KITCHEN_TIMBER_FRAME_CLOSURES','SITE_KITCHEN_VISIBLE_FLY_RAFTER_ENDS'))]
protected=[n for n in E if ('KITCHEN' in n and n not in remove) or n.startswith(('SITE_GATE_','SITE_PERIMETER_'))]
for i,a in enumerate(solids):
 check('new_closed_valid_'+str(i),a.status()==mf.Error.NoError and a.volume()>1e-11)
 g=meta[i][1]['geometry'];v=np.array(g['vertices']);over=max(vv[2]-(roof_bottom(vv[0],vv[1])-.0249) for vv in v);check('new_no_roof_penetration_'+str(i),over<2e-6,roof_bottom_margin_m=float(-over))
fan_clearances=[]
roof_wood_indices=[i for i,(e,p,n) in enumerate(meta) if e['name'].startswith(('SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES','SITE_KITCHEN_V12_LONGITUDINAL_ROUND_PURLINS','SITE_KITCHEN_V12_RIDGE_UNDER_TIMBER_BEAM','SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS'))]
for i,(e,p,n) in enumerate(meta):
 if n.startswith('实景三叶吊扇_活动扇叶'):
  mingap=min(solids[i].min_gap(solids[j],2.) for j in roof_wood_indices);check('fan_blade_clear_of_beams_purlins_'+n,mingap>.01,minimum_gap_m=mingap);fan_clearances.append(dict(blade=n,minimum_timber_gap_m=mingap))
# Solid-kernel contact graph (2mm gap tolerance) to ground/wall/fixed roof anchors.
anchor_nodes=[E['SITE_KITCHEN_STONE_FLOOR'],E['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES'],E['SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS']]
anchors=[manifold(p['geometry']) for e in anchor_nodes for p in e['parts']]
ab=np.array([a.bounding_box() for a in anchors]);bb=np.array([a.bounding_box() for a in solids]);roots=[];edges=[]
tol=.002
def nearbox(a,b,t):return np.all(a[:3]<=b[3:]+t) and np.all(b[:3]<=a[3:]+t)
for i,a in enumerate(solids):
 for j,z in enumerate(anchors):
  if nearbox(bb[i],ab[j],tol) and a.min_gap(z,tol+.0001)<=tol:roots.append(i);break
adj=[[] for _ in solids]
for i,a in enumerate(solids):
 cand=np.where(np.all(bb[i,:3]<=bb[i+1:,3:]+tol,axis=1)&np.all(bb[i,3:]+tol>=bb[i+1:,:3],axis=1))[0]+i+1
 for j in cand:
  gap=a.min_gap(solids[int(j)],tol+.0001)
  if gap<=tol:adj[i].append(int(j));adj[int(j)].append(i);edges.append([i,int(j),gap])
seen=set(roots);stack=list(roots)
while stack:
 i=stack.pop()
 for j in adj[i]:
  if j not in seen:seen.add(j);stack.append(j)
unattached=[i for i in range(len(solids)) if i not in seen]
# Do not retain non-structural donor carved accents which were floating already.
# Every V12 structural frame/purlin/rafter must remain connected.
donor_names={row['name'] for row in D['parts']}
structfloat=[i for i in unattached if meta[i][2] not in donor_names]
check('new_traditional_structure_has_grounded_solid_contact_path',not structfloat,unattached_new_structural_parts=[meta[i][2] for i in structfloat])
for i in unattached:
 e,p,label=meta[i];e['parts'].remove(p);excluded.append(dict(name=label,reason='Donor detail lacked a 2mm solid-contact path to ground/wall/frame and was excluded'))
nodes=[e for e in nodes if e['parts']]
for rec in door_records:
 rec['frame_parts']=len(next(e for e in nodes if e['name']==rec['frame_node'])['parts']);rec['leaf_parts']=len(next(e for e in nodes if e['name']==rec['leaf_node'])['parts'])
column_support=[]
for k,y in enumerate(stations):
 ii=next(i for i,(_,_,n) in enumerate(meta) if n==f'COL_{k+1:02d}_实体柱身');jj=next(i for i,(_,_,n) in enumerate(meta) if n==f'檐廊圆柱{k}_落地青石柱础')
 gap=solids[ii].min_gap(solids[jj],.01);floor_gap=solids[jj].min_gap(anchors[0],.01);cbb=bb[ii];sbb=bb[jj]
 check(f'outer_column_{k}_directly_supported_by_stone_base',gap<.00001 and floor_gap<.00001 and cbb[2]<sbb[5] and abs(sbb[2]+.4)<1e-7,column_base_min_z_m=float(cbb[2]),stone_base_min_z_m=float(sbb[2]),stone_base_max_z_m=float(sbb[5]),stone_post_gap_m=gap,stone_floor_gap_m=floor_gap)
 column_support.append(dict(column=k+1,local_xy=[7.891,y],column_bottom_z_m=float(cbb[2]),stone_base_bottom_z_m=float(sbb[2]),stone_base_top_z_m=float(sbb[5]),wood_stone_overlap_z_m=float(sbb[5]-cbb[2]),stone_floor_gap_m=floor_gap))
check('photo_four_double_octagon_windows_have_eight_closed_lower_octagons',sum(n['name'].startswith('木窗') for n in oct_records)==8)
check('upper_wide_and_lower_narrow_transoms_are_distinct_levels',3.065-2.405>.60 and 2.245>2.23)
mats={'M_V12_Kitchen_'+n:sp for n,sp in D['materials'].items()}
M=dict(replace=[],add=nodes,remove=remove,definitions={},materials=mats,source_scene_sha256=hashlib.sha256(SP.read_bytes()).hexdigest(),protected_node_sha256={n:hashlib.sha256(json.dumps(E[n],sort_keys=True,separators=(',',':')).encode()).hexdigest() for n in protected},changes=[dict(id='V12_KITCHEN_EXPOSED_TRADITIONAL_TIMBER',description='按漫游1055/1070和4张实景近照建立内退檐廊、落石础圆柱、两层回纹格窗、连续双八角窗环及门板弧形压条，补露明横向坡段月梁、纵圆檩、密排木椽；两木门独立活动分组。保留航拍确认的偏心屋脊、门楼屋面上下关系和灰砖院墙交接。',source=REFS,roof_shape_preserved=True,dimensions_reference_not_field_measured=True)],coordinate_mapping_before_mm_to_LOCAL_m='[7.70+Ymm/1000,-11.87901+Xmm/1000,-.40+Zmm/1000]; roof-specific donor Z>3m continuously fitted below exact retained roof')
(O/'Mutation.json').write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding='utf8')
qa=dict(status='PASS',added_nodes=len(nodes),closed_parts=sum(len(e['parts']) for e in nodes),old_nodes_retired=len(remove),donor_closed_parts=D['included_parts'],before_source_sha256=D['source_sha256'],preserved_nodes=protected,excluded=excluded,solid_contact_tolerance_m=tol,connected_new_parts=len(seen),contact_edges=len(edges),new_structure_disconnected=structfloat,contact_verification='Manifold exact solid minimum-gap graph to retained kitchen floor/walls/sheathing; 2mm visible-joint tolerance. Every outer column also directly checked against its stone base and floor.',outer_column_direct_support=column_support,octagon_details=oct_records,fret_boolean_union=fret_union_records,door_interaction=door_records,photo_confirmed_services=dict(fan_blade_timber_clearance=fan_clearances,side_lamps=light_records,column_surface_conduit=True,relative_placement_fitted_not_measured=True),near_photo_fret_levels={'narrow_transom_z_m':[1.99,2.23],'timber_header_z_m':[2.245,2.40],'broad_upper_band_z_m':[2.405,3.065],'lower_double_octagon_centers_z_m':[.93,1.58]},actual_photo_over_complex_reference_truss=True,checks_count=len(checks),checks=checks,dimensions_reference_not_field_measured=True)
(O/'Geometry_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');(O/'Contact_Graph.json').write_text(json.dumps(dict(roots=roots,edges=edges,index=[dict(node=e['name'],part=p['source_part_name']) for e,p,_ in meta]),ensure_ascii=False),encoding='utf8')
def native_file(path,elems):
 F=rh.File3dm();F.Settings.ModelUnitSystem=rh.UnitSystem.Meters;F.Settings.ModelAbsoluteTolerance=.001;ly=rh.Layer();ly.Name='60_SITE';li=F.Layers.Add(ly);mids={};mm=dict(S['materials']);mm.update(mats)
 for n,sp in mm.items():
  m=rh.Material();m.Name=n;m.DiffuseColor=(*sp['color'],255);m.Transparency=1-sp.get('alpha',1);m.ToPhysicallyBased();m.PhysicallyBased.Roughness=sp.get('roughness',.5);mids[n]=F.Materials.Add(m)
 for e in elems:
  gr=rh.Group();gr.Name=e['name'];gi=len(F.Groups);F.Groups.Add(gr)
  for j,p in enumerate(e['parts']):
   v,fs,_,_=ex.solid_data(p['geometry']);g=rh.Mesh();g.Vertices.UseDoublePrecisionVertices=True
   for v0 in v:g.Vertices.AddPoint3d(*map(float,v0))
   for f0 in fs:
    if len(f0)<=4:g.Faces.AddFace(*f0)
    else:
     for t in ex.triangulate(v[f0]):g.Faces.AddFace(*[f0[k] for k in t])
   g.Normals.ComputeNormals();g.Compact();check('CAD_mesh_closed_'+e['name']+'_'+str(j),g.IsValid and g.IsClosed)
   at=rh.ObjectAttributes();at.Name=e['name']+'__'+str(j+1);at.LayerIndex=li;at.MaterialIndex=mids[p['material']];at.MaterialSource=rh.ObjectMaterialSource.MaterialFromObject;at.AddToGroup(gi);at.SetUserString('V12_Element',e['name']);at.SetUserString('V12_Part_Index',str(j));at.SetUserString('V12_Material',p['material']);at.SetUserString('SourcePart',p.get('source_part_name','Retained exact V11 geometry'));at.SetUserString('DimensionStatus','Reference fit; not field-measured')
   if 'door_id' in e:
    for tag in ['door_id','role','hinge_origin_local_m','hinge_axis_local','hinge_evidence']:at.SetUserString(tag,json.dumps(e[tag],ensure_ascii=False) if isinstance(e[tag],list) else e[tag])
   F.Objects.AddMesh(g,at)
 assert F.Write(str(path),8);Q=rh.File3dm.Read(str(path));check('CAD_readback_'+path.name,len(Q.Objects)==sum(len(e['parts']) for e in elems) and all(o.Geometry.IsValid and o.Geometry.IsClosed for o in Q.Objects));return F
native_file(O/'Changed_Kitchen_V12_LOCAL.3dm',nodes)
allk=[e for e in S['elements'] if e['name'].startswith('SITE_KITCHEN_') and e['name'] not in remove]+nodes
full=native_file(O/'Kitchen_Complete_V12_LOCAL.3dm',allk)
C=json.loads((Path(r'E:/jz/JIA/Rebuild_V11_Hybrid/02_Data/Coordinate.json')).read_bytes());a=math.radians(C['rotation_deg']);T=rh.Transform.Multiply(rh.Transform.Translation(*C['origin']),rh.Transform.Rotation(a,rh.Vector3d(0,0,1),rh.Point3d(0,0,0)))
for ob in list(full.Objects):g=ob.Geometry;assert g.Transform(T);at=ob.Attributes;full.Objects.Delete(at.Id);full.Objects.Add(g,at)
assert full.Write(str(O/'Kitchen_Complete_V12_ALIGNED_ENU.3dm'),8)
qa.update(checks_count=len(checks),checks=checks,mutation_sha256=hashlib.sha256((O/'Mutation.json').read_bytes()).hexdigest(),changed_cad_sha256=hashlib.sha256((O/'Changed_Kitchen_V12_LOCAL.3dm').read_bytes()).hexdigest());(O/'Geometry_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:qa[k] for k in ['status','added_nodes','closed_parts','old_nodes_retired','checks_count','contact_edges','new_structure_disconnected']},ensure_ascii=False),flush=True)
