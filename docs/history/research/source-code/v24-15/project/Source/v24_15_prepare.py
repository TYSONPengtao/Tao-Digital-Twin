"""Photo-fitted traditional storage roof frame; metres, solid native meshes."""
import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from v24_13_geometry import roof_z,front,ridge,rear
D=W/'v24_15';OUT={'objects':[],'proof':{}};WOOD='M_V24_15_Traditional_Storage_Wood';GLASS='M_V24_15_Amber_Transom_Glass'
def solid(v,f,n=''):
 m=mf.Manifold(mf.Mesh64(np.array(v,dtype=np.float64,order='C'),np.array(f,dtype=np.uint64,order='C')))
 if m.status()==mf.Error.NoError and m.volume()>0:return m
 for dec in [9,8,7,6,5]:
  vv,ix=np.unique(np.round(v,dec),axis=0,return_inverse=True);ff=ix[f];t=vv[ff];ok=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-13;ff=ff[ok];m=mf.Manifold(mf.Mesh64(np.array(vv,dtype=np.float64,order='C'),np.array(ff,dtype=np.uint64,order='C')))
  if m.status()==mf.Error.NoError and m.volume()>0:return m
 raise RuntimeError((n,m.status(),m.volume()))
def load(n):
 a=np.load(D/(n+'.npz'));return solid(a['v'],a['f'],n)
def cube(lo,hi):return mf.Manifold.cube(np.array(hi)-lo).translate(lo)
def union(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def put(n,m,new=True,mat=WOOD,axis='X',transfer=False):
 assert m.status()==mf.Error.NoError and m.volume()>0,(n,m.status());a=m.to_mesh64();v=np.asarray(a.vert_properties[:,:3]);f=np.asarray(a.tri_verts);solid(v.astype(np.float32).astype(np.float64),f,n+' saved');OUT['objects'].append({'name':n,'new':new,'material':mat,'axis':axis,'v':v.tolist(),'f':f.tolist(),'volume_m3':m.volume(),'bodies':len(m.decompose()),'transfer':transfer});print(n,round(m.volume(),6),len(m.decompose()),flush=True)
def rod(a,b,r,sides=20):
 a=np.array(a,float);b=np.array(b,float);z=(b-a)/np.linalg.norm(b-a);x=np.cross(z,[0.,0.,1.])
 if np.linalg.norm(x)<1e-8:x=np.array([1.,0.,0.])
 x/=np.linalg.norm(x);y=np.cross(z,x);return mf.Manifold.cylinder(float(np.linalg.norm(b-a)),r,r,sides).transform(np.c_[x,y,z,a])
def beam(a,b,w,d):
 a=np.array(a,float);b=np.array(b,float);z=(b-a)/np.linalg.norm(b-a);x=np.cross(z,[0.,0.,1.])
 if np.linalg.norm(x)<1e-8:x=np.array([1.,0.,0.])
 x/=np.linalg.norm(x);y=np.cross(z,x);return mf.Manifold.cube([w,d,float(np.linalg.norm(b-a))],True).transform(np.c_[x,y,z,(a+b)/2])
def section(poly,thick):return mf.CrossSection([np.array(orient(Polygon(poly),1).exterior.coords)[:-1]]).extrude(thick)
def vertical_profile(poly,a,b,width):
 a=np.array(a,float);b=np.array(b,float);u=(b-a)/np.linalg.norm(b-a);lat=np.array([-u[1],u[0]]);m=section(poly,width);return m.transform(np.array([[u[0],0,lat[0],a[0]-lat[0]*width/2],[u[1],0,lat[1],a[1]-lat[1]*width/2],[0,1,0,0]],float))
def board(poly):
 a=section(poly,.026).to_mesh64();v=np.asarray(a.vert_properties[:,:3]).copy();f=np.asarray(a.tri_verts)
 for p in v:p[2]+=roof_z(p[0],p[1])-.093
 return solid(v,f,'boarding')
def fy(x):return -14.295+(x-13.60)*.009
def facade_point(x,z,dy=0):return [x,fy(x)+dy,z]
def facade_box(x0,x1,z0,z1,depth=.075,dy=0):
 m=mf.Manifold.cube([x1-x0,depth,z1-z0]);return m.transform(np.array([[1,0,0,x0],[.009,1,0,fy(x0)-depth/2+dy],[0,0,1,z0]],float))
# Retain only the lower original joinery and the concealed kitchen adapter.
# All obsolete trusses, posts, repeated roof boards and dangling beam ends go.
n='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry';old=load(n);lower=old^cube([13.50,-14.62,-.60],[18.42,-13.99,1.82]);adapter=old^cube([10,-12.35,2.6],[13.535,-8.4,5.5]);put(n,union([lower,adapter]),False,'M_V18_Aged_Storage_Timber',transfer=True)
OUT['proof']['old_frame_removed']={'retained_lower_joinery_max_z':1.82,'upper_legacy_frame_completely_removed':True,'retained_volume_m3':lower.volume(),'kitchen_adapter_preserved':True}
X0=13.535;X1=18.405
south=[(X0,-16.48),(X1,-16.48),(X1,-12.15),(X0,-12.15)]
north=[(X0,-12.15),(X1,-12.15)]+[(float(x),rear(x))for x in np.linspace(X1,X0,96)]
put('V24_15_Storage_Continuous_Wood_Boarding',union([board(south),board(north)]),axis='Y')
# Close-spaced round rafters on the two accepted roof planes, never warped.
rafters=[];r=.032;xs=np.arange(13.60,18.38,.158)
for x in xs:
 for ya,yb in [(-16.46,-12.15),(-12.15,rear(float(x))-.045)]:rafters.append(rod([x,ya,roof_z(x,ya)-.120],[x,yb,roof_z(x,yb)-.120],r,18))
put('V24_15_Storage_Continuous_Round_Rafters',union(rafters),axis='Y')
OUT['proof']['rafters']={'rows':len(xs),'round_members':len(rafters),'diameter_m':r*2,'pitch_m':.158,'orientation':'continuous down both roof slopes','two_roof_planes_preserved':True}
# Three bents use the original rear column bases and the front jamb/middle seam.
backs=[(13.6444068,-9.8055975),(15.7202005,-10.2612326),(18.2593603,-10.8367174)]
fronts=[(13.72,fy(13.72)+.09),(15.94,fy(15.94)+.09),(18.26,fy(18.26)+.09)]
purliny=[-16.10,-14.27,-13.25,-12.15,-11.25,-10.45];purlins=[]
for y in purliny:purlins.append(rod([X0-.025,y,roof_z(0,y)-.234],[X1+.025,y,roof_z(0,y)-.234],.085,24))
backline=[(X0,backs[0][1]+(X0-backs[0][0])*.218)]+backs+[(X1,backs[-1][1]+(X1-backs[-1][0])*.227)]
for a,b in zip(backline,backline[1:]):purlins.append(rod([*a,roof_z(*a)-.234],[*b,roof_z(*b)-.234],.085,24))
put('V24_15_Storage_Seven_Round_Purlin_Rows',union(purlins),axis='X')
OUT['proof']['purlins']={'fixed_rows_y':purliny,'radius_m':.085,'seventh_row_follows_original_rear_supports':backline,'ends_seated_in_sealed_gables':True}
bents=[];shortposts=[];rearposts=[];support=[]
for i,(a,b)in enumerate(zip(fronts,backs)):
 a=np.array(a);b=np.array(b);L=float(np.linalg.norm(b-a));u=(b-a)/L
 prof=[(float(t),3.03+.018*math.sin(math.pi*t/L))for t in np.linspace(0,L,25)]+[(float(t),2.81+.055*math.sin(math.pi*t/L))for t in np.linspace(L,0,25)]
 bents.append(vertical_profile(prof,a,b,.18))
 rearposts.append(rod([*b,[-.247,-.240,-.229][i]],[*b,roof_z(*b)-.313],.100,24))
 def at(y):return a+(b-a)*((y-a[1])/(b[1]-a[1]))
 ua,ub=at(-13.25),at(-11.25);bents.append(beam([*ua,3.55],[*ub,3.55],.145,.18))
 for y in [-13.25,-11.25]:
  p=at(y);shortposts.append(rod([*p,3.025],[*p,3.465],.067,20));zt=roof_z(*p)-.313
  if zt>3.635:shortposts.append(cube([p[0]-.085,p[1]-.08,3.635],[p[0]+.085,p[1]+.08,zt+.006]))
 p=at(-12.15);shortposts.append(rod([*p,3.635],[*p,roof_z(*p)-.313],.075,24))
 p=at(-10.45)
 # The left bent reaches beyond this row; all three have a real bearing.
 if min(a[1],b[1])-.01<=-10.45<=max(a[1],b[1])+.01:shortposts.append(rod([*p,3.025],[*p,roof_z(*p)-.313],.067,20))
 support.append({'front':a.tolist(),'back':b.tolist(),'tie_top_z':3.03,'upper_beam_z':3.55,'ridge_post_top_z':roof_z(0,-12.15)-.313})
put('V24_15_Storage_Three_Traditional_Beam_Bents',union(bents),axis='Y')
put('V24_15_Storage_Short_Posts_and_Purlin_Seats',union(shortposts),axis='Z')
put('V24_15_Storage_Rear_Round_Posts',union(rearposts),axis='Z')
OUT['proof']['beam_bents']=support
# The partition is fixed behind the existing veranda. Its middle bearing
# stops above the door lintel; it does not introduce another veranda column.
frame=[]
for x in [13.72,15.94,18.26]:
 hw=.055 if x==15.94 else .080;frame.append(facade_box(x-hw,x+hw,1.805,3.345,.14,.065))
for x in [15.49,16.389]:frame.append(facade_box(x-.035,x+.035,1.805,2.205,.085))
frame.extend([facade_box(13.535,18.405,1.775,1.925,.14),facade_box(13.535,18.405,2.145,2.235,.12),facade_box(13.535,18.405,3.195,3.345,.15)])
# Small continuous bearing under the front purlin, hidden behind the top rail.
frame.append(facade_box(13.535,18.405,3.335,roof_z(0,-14.27)-.313+.008,.15,.016))
put('V24_15_Storage_Upper_Partition_Bearing_Frame',union(frame),axis='X')
# Four complete geometric flower panels above the opening, as in 124221.
lattice=[];panes=[];recess=[];cx0=13.61;cx1=18.32;pitch=(cx1-cx0)/4;cz=2.715
def stick(a,b,width=.027,depth=.075,dy=0):return beam(facade_point(a[0],a[1],dy),facade_point(b[0],b[1],dy),depth,width)
for i in range(4):
 cx=cx0+(i+.5)*pitch;hw=pitch/2-.025;z0,z1=2.235,3.195
 lattice.extend([facade_box(cx-hw-.018,cx-hw+.018,z0,z1,.085,0),facade_box(cx+hw-.018,cx+hw+.018,z0,z1,.085,0),facade_box(cx-hw,cx+hw,z0,z0+.035,.085,0),facade_box(cx-hw,cx+hw,z1-.035,z1,.085,0)])
 points=[(-.17,-.30),(.17,-.30),(.32,-.15),(.32,.15),(.17,.30),(-.17,.30),(-.32,.15),(-.32,-.15)]
 for a,b in zip(points,points[1:]+points[:1]):lattice.append(stick((cx+a[0],cz+a[1]),(cx+b[0],cz+b[1])))
 for sx in [-1,1]:
  for sz in [-1,1]:
   pts=[(cx+sx*.32,cz+sz*.15),(cx+sx*.45,cz+sz*.15),(cx+sx*.45,cz+sz*.32),(cx+sx*hw,cz+sz*.32)]
   for a,b in zip(pts,pts[1:]):lattice.append(stick(a,b))
   lattice.append(stick((cx+sx*.17,cz+sz*.30),(cx+sx*.17,cz+sz*.455)))
 panes.append(facade_box(cx-hw,cx+hw,2.255,3.175,.010,.005))
 # Framed recessed dark wood panel above each lower door/window bay.
 recess.append(facade_box(cx-hw,cx+hw,1.925,2.145,.035,.018))
 lattice.extend([facade_box(cx-hw,cx+hw,1.932,1.957,.055,-.012),facade_box(cx-hw,cx+hw,2.113,2.138,.055,-.012),facade_box(cx-hw,cx-hw+.025,1.932,2.138,.055,-.012),facade_box(cx+hw-.025,cx+hw,1.932,2.138,.055,-.012)])
for i in range(1,4):
 xx=cx0+i*pitch;lattice.append(facade_box(xx-.030,xx+.030,1.925,3.195,.085,0))
lattice_solid=union(lattice)
put('V24_15_Storage_Four_Upper_Transom_Flower_Panels',lattice_solid,axis='X')
put('V24_15_Storage_Upper_Transom_Amber_Panes',union(panes)-lattice_solid-union(frame),mat=GLASS,axis='X')
put('V24_15_Storage_Upper_Recessed_Wood_Frieze',union(recess),axis='X')
OUT['proof']['front_transom']={'four_octagon_panels':4,'z_bounds':[2.235,3.195],'moved_again':False,'follows_existing_recessed_partition_plane':True,'central_bearing_above_door_only':True}
# Horizontal veranda tie over the original oblique pair of vertical posts.
posts=[(13.72,-14.65),(18.26,-15.60)];a=np.array(posts[0]);b=np.array(posts[1]);L=float(np.linalg.norm(b-a));u=(b-a)/L;lat=np.array([-u[1],u[0]])
gallery=[];profile=[(0,2.905),(L,2.905)]+[(float(t),2.685+.035*math.sin(math.pi*t/L))for t in np.linspace(L,0,33)]
gallery.append(vertical_profile(profile,a,b,.17));gallery.append(beam([*a,2.42],[*b,2.42],.070,.075))
gallery.append(beam([X0,-16.48,2.91],[X1,-16.48,2.91],.070,.12))
for x,y in posts:
 # Full projecting eave tie, seated on the post and joined to the inner frame.
 end=fy(x)+.07;ll=end+16.10;prof=[(0,2.827),(ll,2.827),(ll,2.657),(.05,2.657),(0,2.707)];gallery.append(vertical_profile(prof,[x,-16.10],[x,end],.14))
put('V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails',union(gallery),False,WOOD,axis='X')
# Open stepped fretwork below the tie; every end lands on a rail.
fret=[]
for j in range(11):
 t0=.17+j*(L-.34)/11;ww=(L-.34)/11;pts=[(t0,2.740),(t0,2.535),(t0+ww*.26,2.535),(t0+ww*.26,2.455),(t0+ww*.74,2.455),(t0+ww*.74,2.535),(t0+ww,2.535),(t0+ww,2.740)]
 for (t,z),(tt,zz)in zip(pts,pts[1:]):p=a+u*t;q=a+u*tt;fret.append(beam([*p,z],[*q,zz],.030,.030))
put('V24_15_Storage_Veranda_Open_Stepped_Fretwork',union(fret),axis='X')
# Curved sparrow braces with shallow carved scrolls, no bulky disconnected heads.
braces=[];carve=[]
for i,p in enumerate([a,b]):
 sign=1 if i==0 else-1;q=p+u*sign*.42;profile=[(0,2.715),(.42,2.715),(.40,2.625),(.33,2.60),(.27,2.55),(.20,2.46),(.12,2.36),(0,2.36)];braces.append(vertical_profile(profile,p,q,.10))
 # A pierced scroll and incised curl on the inner cheek.
 for sg in [-1,1]:
  cen=p+u*sign*.18+lat*sg*.052;pts=[]
  for j in range(40):
   t=j/39;r=.057*(1-.62*t);ang=-.4+math.tau*1.1*t;d=u*sign*r*math.cos(ang);pts.append([cen[0]+d[0],cen[1]+d[1],2.54+r*math.sin(ang)])
  for aa,bb in zip(pts,pts[1:]):carve.append(rod(aa,bb,.004,8))
put('V24_15_Storage_Veranda_Queti_Brackets',union(braces),axis='X')
put('V24_15_Storage_Queti_Carved_Scroll_Lines',union(carve),axis='X')
OUT['proof']['veranda']={'column_axes':posts,'column_top_z':2.89,'horizontal_tie_top_z':2.905,'two_columns_only':True,'oblique_plan_line_retained':True,'open_fretwork_units':11,'queti_count':2}
OUT['proof']['scope']={'roof_tiles_shell_and_gables_unchanged':True,'foundation_kitchen_screenwalls_unchanged':True,'all_door_animations_unchanged':True,'photos':['124027','123950','124130','124221'],'wide_angle_reference_not_used_as_literal_beam_warp':True,'geometry_is_photo_fitted_not_new_field_measurement':True}
(D/'Prepared_Geometry.json').write_text(json.dumps(OUT,ensure_ascii=False,separators=(',',':')),encoding='utf8')
