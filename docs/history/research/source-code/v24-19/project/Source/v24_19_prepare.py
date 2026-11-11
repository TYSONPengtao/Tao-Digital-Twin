"""Photo-led gable verges and correction of the assumed V16 house-side grade."""
from v24_19_common import *
from v24_13_geometry import roof_z,north_boundary
from shapely.geometry import Point,box
from shapely.ops import unary_union
from functools import lru_cache

BRICK='M_V24_18_Continuous_Blue_Brick';CAP='M_V19_Weathered_Wall_Tile'
ROOF='M_V24_17_Stable_Gray_Ceramic';WHITE='M_V24_11_Plain_White_Limewash'

def ear(t,ridge,base):
 # Faceted upright head, short flat crown and near-vertical neck; no dome.
 d=abs(t)
 if d<=.12:return ridge+.56
 if d<=.255:return ridge+.56-(d-.12)*(.18/.135)
 if d<=.273:return ridge+.38-(d-.255)*(.29/.018)
 if d<=.38:return max(base,ridge+.09-(d-.273)*(.11/.107))
 if d<.55:return max(base,ridge-.02-(d-.38)*.36)
 return base

def stations(lo,hi,centre):
 return sorted(set(np.linspace(lo,hi,160).tolist()+[centre+d for d in [-.55,-.38,-.273,-.255,-.12,0,.12,.255,.273,.38,.55]if lo<=centre+d<=hi]))

def border(poly,width,lo,hi,axis):
 p=Polygon(poly);q=p.buffer(-width,join_style=2)
 m=profile_solid(list(p.exterior.coords)[:-1],lo,hi,axis)
 return m-profile_solid(list(q.exterior.coords)[:-1],lo-.001,hi+.001,axis)

def head_frames(tag,centre,ridge,face,direction,axis):
 coords=[(-.38,-.02),(-.273,.09),(-.255,.38),(-.12,.56),(.12,.56),(.255,.38),(.273,.09),(.38,-.02),(.38,-.085),(-.38,-.085)]
 poly=Polygon([(centre+t,ridge+z)for t,z in coords]);rows=[]
 for i,(inset,width,depth,mat)in enumerate([(0,.038,.045,CAP),(.040,.026,.029,WHITE),(.068,.026,.017,CAP)]):
  q=poly.buffer(-inset,join_style=2);r=list(q.exterior.coords)[:-1]
  a,b=sorted([face-direction*.004,face+direction*depth]);m=border(r,width,a,b,axis)
  name=f'V24_19_{tag}_Faceted_Head_Frame_{i+1}';put(name,m,mat,True);rows.append(name)
 return rows

gables=[];meta=[]
for side,a,b in [('West',13.205,13.535),('East',18.405,18.685)]:
 y0=-16.10;y1=north_boundary((a+b)/2)-.18;ys=stations(y0,y1,-12.15)
 zz=lambda y:ear(y+12.15,4.35,roof_z(0,y)-.055)
 p=[(y0,2.4),(y1,2.4)]+[(y,zz(y))for y in ys[::-1]];m=profile_solid(p,a,b);gables.append(m);put(f'V24_14_Storage_{side}_Sealed_Gable',m,BRICK)
 # A thin mortar seat lies beneath the projecting clay cover. It is not
 # the former broad, smooth exposed rake cap.
 p=[(y,zz(y)+.014)for y in ys]+[(y,zz(y)-.015)for y in ys[::-1]];put(f'V24_14_Storage_{side}_Gable_Stone_Coping',profile_solid(p,a-.012,b+.012),CAP)
 p=[(y0,2.405),(y1,2.405)]+[(y,zz(y)-.042)for y in ys[::-1]];pa,pb=(b-.006,b+.012)if side=='West'else(a-.012,a+.006);put(f'V24_17_Storage_{side}_Inner_Gable_Limewash',profile_solid(p,pa,pb),WHITE)
 frames=head_frames('Storage_'+side,-12.15,4.35,a if side=='West'else b,-1 if side=='West'else 1,'X')
 meta.append({'tag':'Storage_'+side,'wall_normal_axis':'X','wall_outside':a if side=='West'else b,'overhang_edge':13.035 if side=='West'else 18.855,'projection_m':.17,'head_peak_z':4.91,'frames':frames})

def variable_prism(poly,top,thick):
 # Extruded polygon triangulation, then lift both indexed rings to a plane.
 m=section(poly,thick);d=m.to_mesh64();v=np.array(d.vert_properties[:,:3]);f=np.array(d.tri_verts);v[:,2]+=np.array([top(x,y)-thick for x,y in v[:,:2]])
 return solid(v,f)

X0=13.035;X1=18.855
back=lambda x:north_boundary(x)+.38
ps=[[(X0,-16.48),(X1,-16.48),(X1,-12.15),(X0,-12.15)],[(X0,-12.15),(X1,-12.15)]+[(float(x),back(x))for x in np.linspace(X1,X0,130)]]
bed=union([variable_prism(p,lambda x,y:roof_z(x,y)-.022,.036)for p in ps]);G=union(gables)
# Tile-bed/masonry contacts remain concealed beneath the actual clay tiles.
put('SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry',bed-G,ROOF)

def curved_tile(transverse,a,b,height,axis='Y',pan=False):
 slope=(height(b)-height(a))/(b-a);along=np.array([0.,1.,slope])if axis=='Y'else np.array([1.,0.,slope]);along/=np.linalg.norm(along)
 across=np.array([1.,0.,0.])if axis=='Y'else np.array([0.,-1.,0.]);normal=np.cross(across,along);normal/=np.linalg.norm(normal)
 if pan:
  us=np.linspace(-.061,.061,9);p=[(float(u),-.012+.012*(u/.061)**2)for u in us];p+= [(u,z-.010)for u,z in p[::-1]]
 else:
  ang=np.linspace(0,math.pi,13);p=[(.054*math.cos(t),.054*math.sin(t)-.005)for t in ang]+[(.044*math.cos(t),.044*math.sin(t)-.005)for t in ang[::-1]]
 origin=[transverse,a,height(a)]if axis=='Y'else[a,transverse,height(a)]
 return section(p,math.hypot(b-a,height(b)-height(a))).transform(np.c_[across,normal,along,origin])

tiles=[];count=0
# Two actual edge rows beyond each brick outer face, carried by the roof bed.
for x in np.arange(X0+.063,X1-.018,.158):
 for ya,yb in [(-16.475,-12.15),(-12.15,back(x)-.02)]:
  num=math.ceil((yb-ya)/.32)
  for j in range(num):
   a=ya+(yb-ya)*j/num+.0015;b=ya+(yb-ya)*(j+1)/num-.0015;tiles.append(curved_tile(x,a,b,lambda y:roof_z(x,y)));count+=1
   if x+.079+.061<X1-.008:tiles.append(curved_tile(x+.079,a,b,lambda y:roof_z(x,y),pan=True))
tilemass=compose(tiles)-G;put('SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry',tilemass,ROOF)

# Kitchen: keep the accepted roof slopes and extend their end sections to
# produce real tiled verges outside the closed brick gables.
kroof=load('SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry');ktri=source('SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry');tt=ktri['v'][ktri['f']]
@lru_cache(maxsize=10000)
def kh(x):
 hits=[]
 for t in tt:
  A=np.c_[t[:,:2],np.ones(3)]
  if abs(np.linalg.det(A))<1e-9:continue
  b=np.linalg.solve(A.T,[x,-7,1])
  if min(b)>=-1e-6:hits.append(float(b@t[:,2]))
 if hits:return max(hits)
 near=8.4 if x<11.7625 else 13.3;return kh(near)+(x-near)*(.305 if x<11.7625 else-.48)
kr=11.7625;krz=kh(kr);kg=[]
for side,a,b,lo,hi,name in [('South',-11.94,-11.64,8.15,13.43,'V24_Kitchen_Gable_Upper_Brick_Infill'),('North',-2.935,-2.575,8.15,14.10,'V24_03_Kitchen_Rear_Gable_Wall')]:
 xs=stations(lo,hi,kr);zz=lambda x:ear(x-kr,krz,kh(x)-.035);z0=2.24 if side=='South'else-.424;p=[(lo,z0),(hi,z0)]+[(x,zz(x))for x in xs[::-1]];body=profile_solid(p,a,b,'Y');kg.append(body);put(name,body,BRICK)
 p=[(x,zz(x)+.014)for x in xs]+[(x,zz(x)-.015)for x in xs[::-1]];cn='V24_Kitchen_Curved_Gable_Coping'if side=='South'else'V24_17_Kitchen_North_Gable_Coping';put(cn,profile_solid(p,a-.012,b+.012,'Y'),CAP)
 p=[(lo,z0+.005),(hi,z0+.005)]+[(x,zz(x)-.042)for x in xs[::-1]];pa,pb=(b-.006,b+.012)if side=='South'else(a-.012,a+.006);put(f'V24_17_Kitchen_{side}_Inner_Gable_Limewash',profile_solid(p,pa,pb,'Y'),WHITE)
 frames=head_frames('Kitchen_'+side,kr,krz,a if side=='South'else b,-1 if side=='South'else 1,'Y')
 meta.append({'tag':'Kitchen_'+side,'wall_normal_axis':'Y','wall_outside':a if side=='South'else b,'overhang_edge':-12.13 if side=='South'else-2.385,'projection_m':.19,'head_peak_z':krz+.56,'frames':frames})
KG=union(kg)
gate=union([load(n)for n in INDEX if n in ['V24_XIESHAN_01_Upper_Two_Main_Slopes','V24_XIESHAN_02_Four_Lower_Hipped_Eaves','V24_XIESHAN_07_Closed_Pale_Ceiling','V24_XIESHAN_08_Five_Continuous_Stepped_Eave_Bands','V24_XIESHAN_09_Continuous_Eave_Bearing_Core']])
guard=union([gate.translate(v)for v in [[0,0,0],[.003,0,0],[-.003,0,0],[0,.003,0],[0,-.003,0],[0,0,.003],[0,0,-.003]]])
ends=[]
for y,lo,hi in [(-11.675,-12.13,-11.673),(-2.885,-2.887,-2.385)]:
 cs=kroof.rotate([90,0,0]).slice(y);ext=cs.extrude(hi-lo).translate([0,0,lo]).rotate([-90,0,0]);ends.append(ext)
put('SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry',(union([kroof]+ends)-KG)-guard,ROOF)
endtiles=[]
for lo,hi in [(-12.13,-11.52),(-3.02,-2.385)]:
 for y in np.arange(lo+.063,hi+.12,.158):
  for xa,xb in [(7.445,kr),(kr,13.64)]:
   num=math.ceil((xb-xa)/.30)
   for j in range(num):
    a=xa+(xb-xa)*j/num+.0015;b=xa+(xb-xa)*(j+1)/num-.0015;endtiles.append(curved_tile(y,a,b,lambda x:kh(x)+.027,'X'))
    if y+.079+.061<hi+.015:endtiles.append(curved_tile(y+.079,a,b,lambda x:kh(x)+.027,'X',True))
endmask=union([cube([7,-12.13,1],[14.2,-11.52,6]),cube([7,-3.02,1],[14.2,-2.385,6])]);inside_storage=cube([13.23,-12.5,2.24],[15,-9.08,6]);endtiles=((compose(endtiles)^endmask)-inside_storage)-KG-guard
put('V24_19_Kitchen_True_Tiled_Verge_Courses',endtiles,ROOF,True)
for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0_Geometry','SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_1_Geometry']:
 put(n,load(n)-endmask-KG,ROOF)
# Also trim the concealed mortar cap to the unchanged gate.
for n in ['V24_Kitchen_Curved_Gable_Coping']:
 row=next(r for r in OUT['objects']if r['name']==n);OUT['objects'].remove(row);put(n,solid(row['v'],row['f'])-guard,CAP)
OUT['proof']['photo_gables']={'references':['211108','211128','211336'],'faceted_upright_heads':True,'peak_above_bare_ridge_m':.56,'former_broad_rake_coping_removed':True,'thin_buried_mortar_seat_m':.029,'real_clay_pan_and_cover_tiles':True,'storage_cover_tile_count':count,'closed_brick_exterior_retained':True,'no_new_exposed_timber':True,'gables':meta,'unchanged_inner_gate':True}

# The uniform V16 grade was an assumption, not a measured house datum. Remove
# the rejected brick ring and meet the native floor at a 60 mm threshold.
slab=load('SLAB_JOINED_F1_Geometry');hp=max(slab.slice(-.075).to_polygons(),key=lambda p:Polygon(p).area);house=Polygon(hp).simplify(1e-5,preserve_topology=True)
entry=box(3.75,-1.25,9.25,2.10)
@lru_cache(maxsize=300000)
def grade_weight(x,y):
 p=Point(x,y);d=p.distance(house);u=max(0.,min(1.,(d-.10)/1.65));w=1-3*u*u+2*u*u*u
 # Keep the existing entry steps and their approach level intact. The house
 # itself is still supported by its native step-and-porch solid here.
 if entry.covers(p):return 0.
 if -1.7<y<.90:
  q=p.distance(entry);s=max(0.,min(1.,q/.65));a=max(0.,min(1.,(y+.10)/1.0));fade=1-(3*a*a-2*a*a*a);w*=1-fade*(1-(3*s*s-2*s*s*s))
 return w

def refine(v,f,mi,uv):
 V=v.tolist();F=f.tolist();MI=mi.tolist();UV=uv.tolist()
 for step in range(18):
  mids={}
  for ids in F:
   t=np.array([V[i]for i in ids]);p=t.mean(0)
   if not(-2.5<p[0]<15.7 and-2.5<p[1]<11.9)or max(t[:,2])<-.9:continue
   if not any(grade_weight(*q[:2])>1e-5 for q in list(t)+[p]):continue
   for a,b in zip(ids,ids[1:]+ids[:1]):
    key=tuple(sorted([a,b]))
    if key not in mids and np.linalg.norm(np.array(V[a])[:2]-np.array(V[b])[:2])>.28:
     mids[key]=len(V);V.append(((np.array(V[a])+V[b])/2).tolist())
  if not mids:break
  nf=[];nm=[];nu=[]
  for ids,mat,tuv in zip(F,MI,UV):
   a,b,c=ids;ab=mids.get(tuple(sorted([a,b])));bc=mids.get(tuple(sorted([b,c])));ca=mids.get(tuple(sorted([c,a])));k=sum(s is not None for s in [ab,bc,ca]);parts=[]
   if k==0:parts=[ids]
   elif k==3:parts=[[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]]
   elif k==1:
    parts=[[a,ab,c],[ab,b,c]]if ab is not None else[[b,bc,a],[bc,c,a]]if bc is not None else[[c,ca,b],[ca,a,b]]
   elif ca is None:parts=[[a,ab,c],[ab,bc,c],[ab,b,bc]]
   elif ab is None:parts=[[b,bc,a],[bc,ca,a],[bc,c,ca]]
   else:parts=[[c,ca,b],[ca,ab,b],[ca,a,ab]]
   um={q:np.array(u)for q,u in zip(ids,tuv)}
   for q,i,j in [(ab,a,b),(bc,b,c),(ca,c,a)]:
    if q is not None:um[q]=(um[i]+um[j])/2
   for q in parts:nf.append(q);nm.append(mat);nu.append([um[i].tolist()for i in q])
  F,MI,UV=nf,nm,nu
 else:raise RuntimeError('grade refinement did not converge')
 return np.array(V),np.array(F),np.array(MI),np.array(UV)

ground=[]
def source_top_sampler(d):
 t=d['v'][d['f']];A=t[:,1,:2]-t[:,0,:2];B=t[:,2,:2]-t[:,0,:2];det=A[:,0]*B[:,1]-A[:,1]*B[:,0];keep=abs(det)>1e-10;t=t[keep];A=A[keep];B=B[keep];det=det[keep];xyz=d['v'][d['v'][:,2]>-1.1]
 def sample(x,y):
  q=np.array([x,y])-t[:,0,:2];a=(q[:,0]*B[:,1]-q[:,1]*B[:,0])/det;b=(A[:,0]*q[:,1]-A[:,1]*q[:,0])/det;ok=(a>=-2e-5)&(b>=-2e-5)&(a+b<=1+2e-5)
  if ok.any():return float((t[:,0,2]+a*(t[:,1,2]-t[:,0,2])+b*(t[:,2,2]-t[:,0,2]))[ok].max())
  ds=((xyz[:,:2]-[x,y])**2).sum(1);ii=np.argsort(ds)[:8];return float(xyz[ii,2].max())
 return sample
for n in INDEX:
 if not any(k in n for k in ['GRADED_INTERIOR_SOIL','REBUILT_COURT']):continue
 print('GRADE_REFINE',n,flush=True)
 d=source(n);v,f,mi,uv=refine(d['v'],d['f'],d['mi'],d['uv']);old=v.copy()
 upper={};sample=source_top_sampler(d)
 for i,(x,y,z)in enumerate(old):
  key=(round(float(x),8),round(float(y),8));w=grade_weight(float(x),float(y))
  if w<1e-12:continue
  if key not in upper:upper[key]=sample(float(x),float(y))
  top=upper[key];delta=max(0.,-.060-top)*w
  if 'SOIL'in n:delta*=max(0.,min(1.,(z+4.800000190735)/(top+4.800000190735)))if top>-4.799 else 0
  v[i,2]+=delta
 moved=np.linalg.norm(v-old,axis=1)>1e-8
 assert (v-old)[:,2].max()<.45,(n,'unexpected grade displacement',(v-old)[:,2].max())
 if not moved.any():continue
 row={'name':n,'new':False,'v':v.tolist(),'f':f.tolist(),'mi':mi.tolist(),'uv':uv.tolist(),'materials':INDEX[n]['materials'],'smooth_top':'SOIL'in n};OUT['raw_objects'].append(row);ground.append({'object':n,'changed_vertices':int(moved.sum()),'maximum_raise_m':float((v-old)[:,2].max()),'outside_influence_unchanged':True,'original_plan_preserved':True})
OUT['proof']['house_grade']={'rejected_object_removed':OUT['remove'][0],'cause':'V16 assumed -0.48 m interior grade without tying it to the native first-floor datum. V18 invented a visible brick skirt rather than resolving that mismatch.','first_floor_top_z':0.,'first_floor_bottom_z':slab.bounding_box()[2],'new_wall_contact_grade_z':-.060,'transition_width_m':1.65,'outer_flat_contact_band_m':.10,'entry_step_approach_preserved':True,'building_translation_m':[0,0,0],'new_visible_brick_or_stone_skirt':False,'house_footprint':list(house.exterior.coords),'ground_objects':ground,'first_floor_vertical_edge_finish':'Match existing plain exterior wall, no new masonry course','dimensions_basis':'Native floor datum and user photographs; local grade fit, not a new measured survey'}
write();print('V19_PREPARED',len(OUT['objects']),len(OUT['raw_objects']),flush=True)
