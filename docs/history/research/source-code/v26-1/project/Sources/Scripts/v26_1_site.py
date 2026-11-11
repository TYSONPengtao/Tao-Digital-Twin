from v26_1_common import *
from v24_16_common import beam,rod
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
import math
raw=[];archive=[];proof={}
ground=[n for n in I if n.startswith('V24_28_High_Approach_Stone_')]+['V24_31_Continuous_Gray_Road_And_Storage_Approach','SITE_KITCHEN_STONE_FLOOR_Geometry','SITE_V14_INNER_STORAGE_FLOOR_Geometry','SITE_V14_OUTER_STORAGE_FLOOR_Geometry','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','V24_30_Low_Main_Court_Joint_Base','V24_30_Low_Main_Court_Running_Bond_Stone','V24_30_High_North_Lane_And_Rear_Joint_Base','V24_30_High_North_Lane_And_Rear_Running_Bond_Stone','V24_30_Outer_Yard_White_Building_Pad','V24_30_Graded_Approach_Curb_Retaining_Base','V24_30_Individual_Roadside_Curb_Stones','V24_30_House_West_Pad_Foundation_Closure','HOUSE_V20_ONE_SOLID_ENTRY_STEP_AND_PORCH_SUPPORT_Geometry']
print('GROUND_UNION',len(ground),flush=True);m=union([load(n)for n in ground]);row,m=export('V26_1_Continuous_Court_Road_And_Floor_Surfaces',m,'Single closed visible ownership for court, gallery, graded road, flooring and foundation; retained grey paving and original gate ramp seam');raw.append(row);archive+=ground;proof['ground']={'sources':ground,'positive_components':len(m.decompose()),'height_geometry_changed':False,'internal_or_coincident_faces_removed':True}
# These four legacy layers contest exactly the same square metres on the
# courtyard wall. Unite them and give the inward wall its white finish.
west=['SITE_COURTYARD_WEST_TILE_WALL_Geometry','SITE_COURTYARD_WEST_WHITE_INSIDE_Geometry','SITE_COURTYARD_WEST_TILE_WALL_V10_PLINTH_MORTAR_BACKING_Geometry','SITE_COURTYARD_WEST_TILE_WALL_V10_STAGGERED_GRAY_PLINTH_BRICKS_Geometry','SITE_COURTYARD_WEST_TILE_WALL_V10_CORNER_RETURN_STEPPED_FRAMES_Geometry'];print('WEST_WALL_UNION',len(west),flush=True)
# The inherited L-shaped core contains T-junctions and doubled horizontal
# faces. Re-form its registered plan and exact top height field as one solid.
n='SITE_COURTYARD_WEST_TILE_WALL_Geometry';a=arr(n);t=a['v'][a['f']];cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);tops=t[cross[:,2]>1e-9];poly=unary_union([Polygon(q[:,:2])for q in tops]).buffer(0);core=section(list(poly.exterior.coords)[:-1],1);md=core.to_mesh64();vv=np.array(md.vert_properties[:,:3]);ff=np.array(md.tri_verts)
for j,(x,y,z)in enumerate(vv):
 A2=tops[:,1,:2]-tops[:,0,:2];B2=tops[:,2,:2]-tops[:,0,:2];Q=np.array([x,y])-tops[:,0,:2];det=A2[:,0]*B2[:,1]-A2[:,1]*B2[:,0];u=(Q[:,0]*B2[:,1]-Q[:,1]*B2[:,0])/det;w=(A2[:,0]*Q[:,1]-A2[:,1]*Q[:,0])/det;ok=(u>=-1e-4)&(w>=-1e-4)&(u+w<=1.0001);assert ok.any(),(x,y);h=(tops[:,0,2]+u*(tops[:,1,2]-tops[:,0,2])+w*(tops[:,2,2]-tops[:,0,2]))[ok].max();vv[j,2]=-.625+z*(h+.625)
mi0,uv0=remap(a,vv,ff);CACHE[n]=tracked(vv,ff,I[n]['materials'],mi0,uv0,n+' repaired native wall core')
backplan=poly.buffer(.019,join_style=2).difference(box(.125,-11.458084,10,10));back=section(list(backplan.exterior.coords)[:-1],.625).translate([0,0,-.625]);back=finish(back,I['SITE_COURTYARD_WEST_TILE_WALL_V10_PLINTH_MORTAR_BACKING_Geometry']['materials'][0],'closed recessed plinth backing')
try:inner=load('SITE_COURTYARD_WEST_WHITE_INSIDE_Geometry')
except RuntimeError:inner=mf.Manifold()
framesname='SITE_COURTYARD_WEST_TILE_WALL_V10_CORNER_RETURN_STEPPED_FRAMES_Geometry';aa=arr(framesname);vvf=aa['v'].copy();vvf[vvf[:,1]>-11.58,1]-=.019;CACHE[framesname]=tracked(vvf,aa['f'],I[framesname]['materials'],aa['mi'],aa['uv'],framesname+' seated into wall')
back+=finish(cube([4.80,-11.725,-.625],[4.9343,-11.675,0.]),I['SITE_COURTYARD_WEST_TILE_WALL_V10_PLINTH_MORTAR_BACKING_Geometry']['materials'][0],'closed terminal brick bedding')
wm=[load(n)for n in west if not any(k in n for k in ['MORTAR_BACKING','WHITE_INSIDE'])]+[back,inner]
m=union(wm);row,m=export('V26_1_Courtyard_West_Wall_Single_Surface',m,'Remove overlapping white wall and brick/mortar backing skins; preserve antique outer brick and white inner face');a=np.load(D/row['file']);v=a['v'];f=a['f'];mi=a['mi'].copy();uv=a['uv'];t=v[f];c=t.mean(1);no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);no/=np.maximum(np.linalg.norm(no,axis=1)[:,None],1e-30);mats=row['materials'];white='M_V24_11_Plain_White_Limewash'
if white not in mats:mats.append(white)
mask=((no[:,0]>.99)&(abs(c[:,0]-.125)<.0002))|((no[:,1]>.99)&(abs(c[:,1]+11.458084)<.0002));mi[mask]=mats.index(white);np.savez_compressed(D/row['file'],v=v,f=f,mi=mi,uv=uv);raw.append(row);archive+=west;proof['west_wall']={'sources':west,'single_visible_surface':True,'inward_white_faces':int(mask.sum())}
# The new reference shows a continuous shallow wall coping, not a transverse
# gable at the right end. Keep the registered wall line and reconstruct only
# this short branch above its existing brickwork.
U=np.array([1.,.098]);U/=np.linalg.norm(U);N=np.array([-U[1],U[0]]);A=np.array([10.80,-16.84174904]);L=(13.10-A[0])/U[0]
def p(s,d,z):return np.r_[A+U*s+N*d,z]
def band(poly,s0=0,s1=L):return section(poly,s1-s0).transform(np.c_[np.r_[N,0.],[0,0,1.],np.r_[U,0.],np.r_[A+U*s0,0.]])
old=[n for n in I if any(k in n for k in ['V24_10_Secondary_Screenwall','V24_14_Secondary_Screenwall','V24_17_Secondary_Screenwall'])];archive+=old
WHITE='M_V24_11_Plain_White_Limewash';STONE='M_Stone_Frame';CLAY='M_V24_20_Unified_Weathered_Gray_Clay';BRICK='M_V24_20_Shared_AsBuilt_Perimeter_Brick'
body=band([(-.16,2.43),(.16,2.43),(.16,2.96),(-.16,2.96)],-.035,L+.015);row,_=export('V26_1_Secondary_Wall_Continuous_Upper_Brick',finish(body,BRICK,'reference upper brick'), 'Extend the existing lower brick body continuously to the photographed white frieze');raw.append(row)
steps=[band([(-w,lo),(w,lo),(w,hi),(-w,hi)],-.04,L+.04)for w,lo,hi in [(.17,2.94,2.98),(.19,2.98,3.025),(.225,3.245,3.285),(.255,3.285,3.33)]]
steps.append(band([(-.17,3.01),(.17,3.01),(.17,3.26),(-.17,3.26)],-.025,L+.025));whitebody=union(steps);row,_=export('V26_1_Secondary_Wall_Level_White_Frieze',finish(whitebody,WHITE,'reference white wall frieze'),'Continuous white head band and stepped cornice; removes the raised end gable and fractured low band');raw.append(row)
frames=[]
# Three horizontal inset panels, with a short middle panel as in the photo.
cuts=[(.075,.46*L),(.46*L+.025,.57*L),(.57*L+.025,L-.075)]
for sg in [-1,1]:
 for s0,s1 in cuts:
  h0,h1=3.055,3.218
  for z0 in [h0,h1]:frames.append(beam(p(s0,sg*.174,z0),p(s1,sg*.174,z0),.017,.018))
  for s in [s0,s1]:frames.append(beam(p(s,sg*.174,h0),p(s,sg*.174,h1),.017,.018))
row,_=export('V26_1_Secondary_Wall_Horizontal_Panel_Mouldings',finish(union(frames),STONE,'reference rectangular white band frames'),'Horizontal continuous panel borders matching the real wall, with no loose diagonal end frame');raw.append(row)
# Thin two-sided roof cap with a shallow curve toward its end, not a tall gable.
def lift(s):
 u=np.clip(s/L,0,1);return .028*(2*u-1)**2
def zroof(s,d):return 3.47-.48*abs(d)+lift(s)
parts=[];stations=np.linspace(-.045,L+.045,36)
for s0,s1 in zip(stations[:-1],stations[1:]):
 poly=[(-.28,3.322),(.28,3.322),(.28,zroof((s0+s1)/2,.28)),(0,zroof((s0+s1)/2,0)),(-.28,zroof((s0+s1)/2,-.28))];parts.append(band(poly,float(s0)-.0003,float(s1)+.0003))
bed=union(parts);row,_=export('V26_1_Secondary_Wall_Shallow_Ceramic_Coping',finish(bed,CLAY,'continuous shallow tile bed'),'Shallow continuous ceramic coping on the registered wall axis; raised transverse gable retired');raw.append(row)
tiles=[]
for s in np.arange(.015,L,.14):
 for sg in [-1,1]:
  t0,t1=sorted([sg*.012,sg*.288]);a=p(s,t0,zroof(s,t0)-.005);b=p(s,t1,zroof(s,t1)-.005);axis=(b-a);ll=np.linalg.norm(axis);axis/=ll;lat=np.r_[U,0.];vertical=np.cross(axis,lat);vertical*=1 if vertical[2]>0 else-1;ang=np.linspace(0,math.pi,13);poly=[(.042*math.cos(q),.042*math.sin(q))for q in ang]+[(.032*math.cos(q),.032*math.sin(q))for q in ang[::-1]];tiles.append(section(poly,ll).transform(np.c_[lat,vertical,axis,a]));c=p(s,sg*.29,zroof(s,sg*.29)+.015);tiles.append(rod(c,c+np.r_[N*sg*.018,0],.040,24))
row,_=export('V26_1_Secondary_Wall_Cover_Tiles_And_Ends',finish(mf.Manifold.compose(tiles),CLAY,'photographed clay coping tiles'),'Cover tile and drip rhythm kept continuous on both sides');raw.append(row)
proof['secondary_wall']={'reference':'User 2026-10-23 020742 and 021028 photographs','registered_wall_axis_retained':[A.tolist(),(A+U*L).tolist()],'old_gable_and_low_frieze_archived':old,'brick_to_frieze_z_m':2.96,'white_frieze_z_m':[3.01,3.26],'cap_ridge_z_m':[3.47,3.498],'dimensions':'Photo-proportion fit to existing registered wall line; not newly surveyed dimensions','outer_lower_strata':['original photo rubble','dark dressed stone belt','limewash belt','antique blue brick']}
(D/'Prepared_Site.json').write_text(json.dumps({'objects':raw,'archive':sorted(set(archive)),'proof':proof},ensure_ascii=False,indent=2),encoding='utf8');print('SITE_PREPARED',len(raw),len(set(archive)),flush=True)
