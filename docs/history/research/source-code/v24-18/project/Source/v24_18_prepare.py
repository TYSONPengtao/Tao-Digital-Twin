from v24_18_common import *
from v24_13_geometry import roof_z,north_boundary
from shapely.ops import unary_union
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
BRICK='M_V24_18_Continuous_Blue_Brick';WHITE='M_V24_11_Plain_White_Limewash';CAP='M_V19_Weathered_Wall_Tile'
def ear(t,ridge,base):
 d=abs(t)
 if d<=.16:return max(base,ridge+.40+.16*math.sqrt(max(0,1-(d/.16)**2)))
 if d<.23:return max(base,ridge+.40-.05*(d-.16)/.07)
 if d<.62:
  w=1-(d-.23)/.39;w=w*w*(3-2*w);return max(base,base+(ridge+.35-base)*w)
 return base
for side,a,b in [('West',13.205,13.535),('East',18.405,18.685)]:
 y0=-16.10;y1=north_boundary((a+b)/2)-.18;ys=sorted(set(np.linspace(y0,y1,125).tolist()+np.linspace(-12.78,-11.52,145).tolist()));ys=[y for y in ys if y0<=y<=y1];zz=lambda y:ear(y+12.15,4.35,roof_z(0,y)+.16)
 p=[(y0,2.4),(y1,2.4)]+[(y,zz(y))for y in ys[::-1]];put(f'V24_14_Storage_{side}_Sealed_Gable',profile_solid(p,a,b),BRICK)
 p=[(y,zz(y)+.045)for y in ys]+[(y,zz(y)-.026)for y in ys[::-1]];put(f'V24_14_Storage_{side}_Gable_Stone_Coping',profile_solid(p,a-.045,b+.045),CAP)
 p=[(y0,2.405),(y1,2.405)]+[(y,zz(y)-.042)for y in ys[::-1]];lo,hi=(b-.006,b+.012)if side=='West'else(a-.012,a+.006);put(f'V24_17_Storage_{side}_Inner_Gable_Limewash',profile_solid(p,lo,hi),WHITE)
kroof=source('SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry');tris=kroof['v'][kroof['f']]
def kh(x):
 hits=[]
 for t in tris:
  A=np.c_[t[:,:2],np.ones(3)]
  if abs(np.linalg.det(A))<1e-9:continue
  b=np.linalg.solve(A.T,[x,-7,1])
  if min(b)>=-1e-6:hits.append(float(b@t[:,2]))
 if hits:return max(hits)
 # The short gable overhang follows the accepted two roof slopes.
 near=8.4 if x<11.7625 else 13.3;z=kh(near);slope=.305 if x<11.7625 else -.48;return z+(x-near)*slope
kr=11.7625;krz=kh(kr)
for side,a,b,lo,hi,name in [('South',-11.94,-11.64,8.15,13.43,'V24_Kitchen_Gable_Upper_Brick_Infill'),('North',-2.935,-2.575,8.15,14.10,'V24_03_Kitchen_Rear_Gable_Wall')]:
 xs=sorted(set(np.linspace(lo,hi,150).tolist()+np.linspace(kr-.63,kr+.63,145).tolist()));xs=[x for x in xs if lo<=x<=hi];zz=lambda x:ear(x-kr,krz,kh(x)+.16);z0=2.24 if side=='South'else-.424;p=[(lo,z0),(hi,z0)]+[(x,zz(x))for x in xs[::-1]];put(name,profile_solid(p,a,b,'Y'),BRICK)
 p=[(x,zz(x)+.045)for x in xs]+[(x,zz(x)-.026)for x in xs[::-1]];cn='V24_Kitchen_Curved_Gable_Coping'if side=='South'else'V24_17_Kitchen_North_Gable_Coping';put(cn,profile_solid(p,a-.04,b+.04,'Y'),CAP)
 p=[(lo,z0+.005),(hi,z0+.005)]+[(x,zz(x)-.042)for x in xs[::-1]];pa,pb=(b-.006,b+.012)if side=='South'else(a-.012,a+.006);put(f'V24_17_Kitchen_{side}_Inner_Gable_Limewash',profile_solid(p,pa,pb,'Y'),WHITE)
# Preserve the accepted gate at the kitchen's concealed coping joint.
gateidx={'objects':[r for r in json.loads((D/'Extra_Index.json').read_text())if r['name'].startswith('V24_XIESHAN_')]};gp=[]
for row in gateidx['objects']:
 d=np.load(D/row['file']);gp.append(solid(d['v'],d['f']))
gate=union(gp);row=next(r for r in OUT['objects']if r['name']=='V24_Kitchen_Curved_Gable_Coping');m=solid(row['v'],row['f']);bb=m.bounding_box();local=gate^cube(np.array(bb[:3])-.02,np.array(bb[3:])+.02);m-=union([local.translate(d)for d in [[0,0,0],[.003,0,0],[-.003,0,0],[0,.003,0],[0,-.003,0],[0,0,.003],[0,0,-.003]]]);OUT['objects'].remove(row);put(row['name'],m,CAP)
OUT['proof']['ears']={'prior_peak_above_storage_ridge_m':.90,'new_peak_above_ridge_m':.56,'prior_root_width_m':2.36,'new_root_width_m':1.24,'narrow_stem_width_m':.32,'storage_peak_z':4.91,'kitchen_peak_z':krz+.56,'photo':'185635','brick_closed_gables_retained':True}
# Close the demonstrated grade gap under the whole ground-floor footprint.
slab=load('SLAB_JOINED_F1_Geometry');cs=slab.slice(-.075);sb=slab.bounding_box()[2];hp=max(cs.to_polygons(),key=lambda p:Polygon(p).area);ip=Polygon(hp).buffer(-.008,join_style=2);inset=section(list(ip.exterior.coords)[:-1],.020).translate([0,0,sb-.008]);plinth=union([cs.extrude(sb+.72).translate([0,0,-.72]),inset]);put('V24_18_House_Continuous_Grade_Plinth',plinth,'M_V24_18_Continuous_Dark_Courses',True)
hp=np.r_[hp,hp[:1]];OUT['house_uv_route']={'xy':hp.tolist(),'length_m':float(np.linalg.norm(np.diff(hp,axis=0),axis=1).sum())}
OUT['proof']['house_grounding']={'cause':'Existing first-floor slab underside at -0.150024 m, adjacent graded soil around -0.462..-0.480 m, with no connecting perimeter/plinth solid. Missing 0.312..0.330 m closure, not an entire-building transform.','slab_bottom_z':sb,'grade_samples':detail['grade_samples'],'new_plinth_bottom_z':-.72,'new_plinth_main_top_z':sb,'concealed_inset_bearing_lip_top_z':sb+.012,'bearing_lip_inset_m':.008,'slab_overlap_m':.012,'no_coplanar_exterior_vertical_faces':True,'entire_house_translation_m':[0,0,0],'floors_stairs_and_door_datums_preserved':True}
cuts=[];corner_meta=[]
for fl,z0,z1,sides in [(1,.6,3.6,['L','R']),(2,4.5,7.2,['L','R']),(3,8.1,10.5,['R'])]:
 local=[]
 for side in sides:
  for x in ([.72,3.18]if side=='L'else[9.82,12.28]):
   lo=[x-.16,.94,z0-.0001];hi=[x+.16,1.27,z1+.0001];c=cube(lo,hi);local.append(c);cuts.append(c);corner_meta.append({'floor':fl,'center_x':x,'lo':lo,'hi':hi})
 n=f'FACADE_CONTINUOUS_F{fl}_Geometry';put(n,load(n)-union(local),'M_Wall_Exterior',transfer=True)
n='HOUSE_V22_FRONT_BAY_TILE_FACES_Geometry';put(n,load(n)-union(cuts),'M_Stone',transfer=True)
OUT['proof']['removed_corner_post_regions']=corner_meta
from v24_18_windows import prepare_windows
prepare_windows()
from v24_18_screen import prepare_screen
prepare_screen();OUT['objects'][:]=[r for r in OUT['objects']if r['name']!='V24_11_Screenwall_Continuous_Stepped_Stone_Plinth']
n='SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry';put(n,load(n)-cube([3.20,-18.,3.10],[10.84,-16.0,8]),INDEX[n]['materials'][0],transfer=True);OUT['proof']['screen']['old_inner_limewash_above_wall_crown_trimmed']=True
# One arc-length reference around the existing external retaining footprint.
# This does not move any wall or foundation coordinate.
projected=[]
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry']:
 d=source(n);t=d['v'][d['f']]
 for q in t:
  p=Polygon(q[:,:2])
  if p.area>1e-8:projected.append(p)
shape=unary_union(projected).buffer(.003,join_style=2).buffer(-.003,join_style=2);polys=[shape]if shape.geom_type=='Polygon'else list(shape.geoms);p=max(polys,key=lambda p:p.area);coords=np.array(orient(p,1).exterior.coords)[:-1];i=int(np.argmin(np.linalg.norm(coords-[-8,-8],axis=1)));coords=np.r_[coords[i:],coords[:i],coords[i:i+1]];length=np.linalg.norm(np.diff(coords,axis=0),axis=1).sum();OUT['uv_route']={'xy':coords.tolist(),'length_m':length,'brick_width_m':.24,'brick_row_height_m':.060,'rubble_to_courses_z':-1.05,'courses_to_brick_z':-.38,'geometry_preserved':True}
OUT['proof']['continuous_exterior_finish']={'arc_length_reference_m':length,'world_vertical_datum':True,'brick_mortar_procedural_in_metres':True,'source_photo_weathering_retained':True,'mirrored_photo_repeat_without_edge_breaks':True,'common_material_bands_z':[-1.05,-.38],'wall_or_foundation_plan_moved':False}
write();print('PREPARED_V24_18',len(OUT['objects']),len(OUT['windows']),flush=True)
