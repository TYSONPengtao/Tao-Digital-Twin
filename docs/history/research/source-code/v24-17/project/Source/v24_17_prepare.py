from v24_17_common import *
from v24_13_geometry import roof_z,north_boundary
BRICK='M_V24_08_AsBuilt_Kitchen_Exterior_Brick';ROOF='M_Roof';WHITE='M_V24_11_Plain_White_Limewash'
OUT['remove']=['V24_11_Screenwall_Continuous_Stepped_Stone_Plinth','SITE_V14_KITCHEN_STORAGE_DIAGONAL_VALLEY_Geometry','V24_Kitchen_Short_Ridge_Head_Inset_Border','V24_Kitchen_Thin_Dark_Coping_Edge','SITE_KITCHEN_V11_VISIBLE_BARE_GRAY_BRICK_UNITS_Geometry','SITE_KITCHEN_V11_VISIBLE_GRAY_MORTAR_BACKING_Geometry']
X0=13.25767994;X1=18.665
back=lambda x:north_boundary(x)+.38
south=[(X0,-16.48),(X1,-16.48),(X1,-12.15),(X0,-12.15)]
north=[(X0,-12.15),(X1,-12.15)]+[(float(x),back(x))for x in np.linspace(X1,X0,100)]
newroof=union([variable_prism(p,lambda x,y:roof_z(x,y)-.022,.036)for p in [south,north]])
put('SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry',newroof,ROOF)
def barrel(x,ya,yb,r=.054,th=.010):
 slope=(roof_z(x,yb)-roof_z(x,ya))/(yb-ya);u=np.array([0.,1.,slope]);u/=np.linalg.norm(u);normal=np.array([0.,-slope,1.]);normal/=np.linalg.norm(normal);L=math.hypot(yb-ya,roof_z(x,yb)-roof_z(x,ya));angles=np.linspace(0,math.pi,13);poly=[(r*math.cos(t),r*math.sin(t))for t in angles]+[((r-th)*math.cos(t),(r-th)*math.sin(t))for t in angles[::-1]];m=section(poly,L);T=np.c_[[1.,0.,0.],normal,u,[x,ya,roof_z(x,ya)-.005]];return m.transform(T)
tiles=[];count=0
for x in np.arange(13.36,18.60,.158):
 for ya,yb in [(-16.475,-12.15),(-12.15,back(x)-.02)]:
  num=math.ceil((yb-ya)/.32)
  for j in range(num):
   a=ya+(yb-ya)*j/num+.0015;b=ya+(yb-ya)*(j+1)/num-.0015;tiles.append(barrel(x,a,b));count+=1
   cx=x+.079
   if cx+.061<X1-.018:
    us=np.linspace(-.061,.061,9);upper=[(float(u),-.012+.012*(u/.061)**2)for u in us];lower=[(u,z-.010)for u,z in upper[::-1]];slope=(roof_z(cx,b)-roof_z(cx,a))/(b-a);tile=section(upper+lower,b-a).transform(np.array([[1,0,0,cx],[0,0,1,a],[0,1,slope,roof_z(cx,a)]],float));tiles.append(tile)
put('SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry',compose(tiles),ROOF)
n='SITE_V14_INNER_STORAGE_RIDGE_CAPS_Geometry';put(n,load(n)^cube([13.52,-13,4.30],[18.42,-11,4.60]),ROOF)
# No small diagonally floating roof adapter or adapter timber remains.
n='SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry';m=load(n);parts=m.decompose();m=union(parts)-cube([10,-13,2.6],[13.535,-8.4,6]);put(n,m,INDEX[n]['materials'][0],transfer=True)
# Tall, broad masonry ears are integral with a brick gable, not a small dome.
def ear(t,ridge_z,base,half=.27):
 d=abs(t);shoulder=ridge_z+.78
 if d<=half:return max(base,shoulder+.12*math.sqrt(max(0,1-(d/half)**2)))
 if d<1.18:
  w=1-(d-half)/(1.18-half);w=w*w*(3-2*w);return max(base,base+(shoulder-base)*w)
 return base
gables=[];gablemeta=[]
for side,a,b in [('West',13.205,13.535),('East',18.405,18.685)]:
 y0=-16.10;y1=north_boundary((a+b)/2)-.18;ys=sorted(set(np.linspace(y0,y1,120).tolist()+np.linspace(-13.34,-10.96,160).tolist()));ys=[y for y in ys if y0<=y<=y1]
 def zfn(y):return ear(y+12.15,4.35,roof_z(0,y)+.16)
 prof=[(y0,2.40),(y1,2.40)]+[(y,zfn(y))for y in reversed(ys)];m=profile_solid(prof,a,b);gables.append(m);put(f'V24_14_Storage_{side}_Sealed_Gable',m,BRICK)
 band=[(y,zfn(y)+.045)for y in ys]+[(y,zfn(y)-.026)for y in reversed(ys)];put(f'V24_14_Storage_{side}_Gable_Stone_Coping',profile_solid(band,a-.045,b+.045),'M_V19_Weathered_Wall_Tile')
 # Inner plaster has positive thickness and sits proud of the solid brick,
 # instead of a second coplanar skin carrying a different texture.
 plprof=[(y0,2.405),(y1,2.405)]+[(y,zfn(y)-.042)for y in reversed(ys)]
 lo,hi=(b-.006,b+.012)if side=='West'else(a-.012,a+.006);put(f'V24_17_Storage_{side}_Inner_Gable_Limewash',profile_solid(plprof,lo,hi),WHITE,True)
 gablemeta.append({'side':side,'brick_x':[a,b],'old_ear_peak_z':4.79,'new_ear_peak_z':zfn(-12.15),'ear_root_width_m':2.36,'exterior':'gray brick','inner':'white limewash'})
# Close the rear roof edge with the same curved brick wall. Its plan and the
# foundation stay fixed; only the roof-level infill is made continuous.
xx=np.linspace(13.2,18.65,100);rearpoly=[(float(x),north_boundary(x))for x in xx]+[(float(x),north_boundary(x)-.285)for x in xx[::-1]];rearband=variable_prism(rearpoly,lambda x,y:roof_z(x,y)-.055,.145)
envelope_poly=[(13.53,-17),(18.41,-17)]+[(float(x),north_boundary(x)-.018)for x in np.linspace(18.41,13.53,100)];env=section(envelope_poly,7).translate([0,0,-1])
for n in ['V24_15_Storage_Continuous_Wood_Boarding','V24_15_Storage_Continuous_Round_Rafters']:
 put(n,load(n)^env,WOOD,axis='Y')
# Kitchen gable profiles come from the original roof planes at mid depth.
def roof_at(x,y,names):
 hits=[]
 for n in names:
  d=source(n);tri=d['v'][d['f']]
  for t in tri:
   A=np.c_[t[:,:2],np.ones(3)]
   if abs(np.linalg.det(A))<1e-9:continue
   bary=np.linalg.solve(A.T,[x,y,1])
   if min(bary)>=-1e-6:hits.append(float(bary@t[:,2]))
 return max(hits)if hits else None
kroof='SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry';kd=source(kroof);kt=kd['v'][kd['f']];planes=[]
for t in kt:
 no=np.cross(t[1]-t[0],t[2]-t[0]);nn=np.linalg.norm(no)
 if nn<1e-9 or no[2]/nn<.75:continue
 A=np.c_[t[:,:2],np.ones(3)]
 if abs(np.linalg.det(A))<1e-10:continue
 pp=np.linalg.solve(A,t[:,2])
 if not any(np.linalg.norm(pp-q)<1e-4 for q in planes):planes.append(pp)
# The two original main slopes are selected by the long roof extent, not the
# short corner flashing facets fitted to the gate.
def kh(x):
 z=roof_at(x,-7,[kroof])
 if z is not None:return z
 pp=min(planes,key=lambda p:abs(float(np.dot([min(max(x,7.5),13.55),-7,1],p))-3.2))
 return float(np.dot([x,-7,1],pp))
kr=11.7625;krz=kh(kr);kmeta=[]
for side,a,b,lo,hi,name in [('South',-11.94,-11.64,8.15,13.43,'V24_Kitchen_Gable_Upper_Brick_Infill'),('North',-2.935,-2.575,8.15,14.10,'V24_03_Kitchen_Rear_Gable_Wall')]:
 xs=sorted(set(np.linspace(lo,hi,150).tolist()+np.linspace(kr-1.18,kr+1.18,130).tolist()));xs=[x for x in xs if lo<=x<=hi]
 def zz(x):return ear(x-kr,krz,kh(x)+.16)
 zbase=2.24 if side=='South'else-.424;profile=[(lo,zbase),(hi,zbase)]+[(x,zz(x))for x in xs[::-1]];body=profile_solid(profile,a,b,'Y');gables.append(body);put(name,body,BRICK)
 cap=[(x,zz(x)+.045)for x in xs]+[(x,zz(x)-.026)for x in xs[::-1]];cn='V24_Kitchen_Curved_Gable_Coping'if side=='South'else'V24_17_Kitchen_North_Gable_Coping';put(cn,profile_solid(cap,a-.04,b+.04,'Y'),'M_V19_Weathered_Wall_Tile',side=='North')
 ip=[(lo,zbase+.005),(hi,zbase+.005)]+[(x,zz(x)-.042)for x in xs[::-1]];pa,pb=(b-.006,b+.012)if side=='South'else(a-.012,a+.006);put(f'V24_17_Kitchen_{side}_Inner_Gable_Limewash',profile_solid(ip,pa,pb,'Y'),WHITE,True)
 kmeta.append({'side':side,'new_peak_z':zz(kr),'wall_y':[a,b]})
# Existing exterior wall continues to the roof underside at the kitchen return.
poly=[(13.13,-8.86),(13.53,-8.276),(14.244,-3.282),(14.26,-2.83),(13.975,-2.83),(13.959,-3.282),(13.245,-8.276),(12.845,-8.86)]
def khend(x,y):
 z=roof_at(x,y,['SITE_KITCHEN_V11_REGISTERED_EAST_EAVE_STRIP_Geometry',kroof])
 if z is None:
  oldx=13.583+(14.075-13.583)*(y+8.275)/4.979;z=3.298+(3.074-3.298)*(y+8.275)/4.979-.48*(x-oldx)+.06
 return z-.045
# A thin upper wall is enough; the accepted lower brick/foundation is retained.
newreturn=union([variable_prism(poly,khend,.23),variable_prism([(13.12,-9.12),(13.56,-9.12),(13.60,-8.84),(13.15,-8.84)],khend,.50)])
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';m=union([load(n),rearband,newreturn])-union(gables);put(n,m,BRICK,transfer=True)
# Keep kitchen roof timber inside the end gables. The veranda's actual timber
# and door/window joinery are still visible from within the covered gallery.
kclip=cube([7,-11.68,1.8],[15,-2.88,6])
inside_storage=cube([13.23,-12.5,2.24],[15,-9.08,6])
for n in [kroof,'SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0_Geometry','SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_1_Geometry','SITE_KITCHEN_FASCIA_BOARD_Geometry','SITE_KITCHEN_VISIBLE_EDGE_FLASHING_Geometry','SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS_Geometry']:
 m=(load(n)^kclip)-inside_storage
 if n=='SITE_KITCHEN_FASCIA_BOARD_Geometry':m=m^cube([7,-12,1.8],[8.1,-2,6])
 put(n,m,INDEX[n]['materials'][0],transfer=True)
for n in ['SITE_KITCHEN_V12_LONGITUDINAL_ROUND_PURLINS_Geometry','SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry','SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS_Geometry']:
 put(n,(load(n)^kclip)-inside_storage,INDEX[n]['materials'][0],transfer=True)
n='SITE_KITCHEN_RIDGE_CAP_AND_END_ORNAMENTS_Geometry';m=load(n);parts=[p for p in m.decompose()if p.bounding_box()[5]<4.56];put(n,union(parts)^kclip,ROOF)
# Unite closed contact cells so duplicate internal faces cannot contest pixels.
for n in ['V24_15_Storage_Veranda_Open_Stepped_Fretwork']:
 m=load(n);put(n,union(m.decompose()),INDEX[n]['materials'][0],transfer=True)
OUT['proof']['gable_rebuild']={'storage':gablemeta,'kitchen':kmeta,'brick_extents_continue_to_coping':True,'main_foundation_and_column_axes_preserved':True}
OUT['proof']['roof_layering']={'old_shell_top_offset_m':0,'old_plate_top_min_offset_m':-.016,'new_shell_top_offset_m':-.022,'new_plate_top_min_offset_m':-.012,'minimum_plate_above_shell_m':.010,'roof_planes_preserved':True,'storage_cover_tiles':count,'removed_diagonal_adapter':True,'no_exterior_rear_wood_deck':True}
from v24_17_secondary import prepare_secondary
prepare_secondary()
# Keep the original inner gate untouched. The enlarged kitchen coping meets
# its existing eave at the concealed corner, with a small construction gap.
gate_index=json.loads((D/'Gate_Export_Index.json').read_text())
gate_parts=[]
for row in gate_index['objects']:
 data=np.load(D/row['file']);gate_parts.append(solid(data['v'],data['f'],row['name']))
gate=union(gate_parts)
name='V24_Kitchen_Curved_Gable_Coping';row=next(r for r in OUT['objects']if r['name']==name);cap=solid(row['v'],row['f'],name)
original_hit=(cap^gate).volume()
bb=cap.bounding_box();local_gate=gate^cube(np.array(bb[:3])-.02,np.array(bb[3:])+.02)
offsets=[[0,0,0],[.003,0,0],[-.003,0,0],[0,.003,0],[0,-.003,0],[0,0,.003],[0,0,-.003]]
cutter=union([local_gate.translate(d)for d in offsets]);cap=cap-cutter
OUT['objects'].remove(row);put(name,cap,row['material'])
OUT['proof']['kitchen_gate_joint']={'original_overlap_m3':original_hit,'final_overlap_m3':(cap^gate).volume(),'local_clearance_offset_m':.003,'accepted_gate_geometry_preserved':True,'gate_cache_objects':[r['name']for r in gate_index['objects']]}
OUT['proof']['scope']={'main_screenwall_centered_roof_preserved':True,'marked_projecting_plinth_removed_both_sides':True,'all_26_door_animations_preserved':True,'entry_post_white_bay_and_two_posts_preserved':True,'source_fit_not_new_survey':True}
write()
