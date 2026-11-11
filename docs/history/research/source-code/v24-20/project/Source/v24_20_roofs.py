from v24_20_common import *
from shapely.geometry import LineString,MultiPoint,box
from shapely.ops import unary_union

MAT='M_V24_20_Unified_Weathered_Gray_Clay'
PITCH=.158;EXPOSE=.30
def tile(transverse,a,b,h,axis,pan=False):
 slope=(h(b)-h(a))/(b-a);along=np.array([0.,1.,slope])if axis=='Y'else np.array([1.,0.,slope]);length=np.linalg.norm(along)*(b-a);along/=np.linalg.norm(along);across=np.array([1.,0.,0.])if axis=='Y'else np.array([0.,-1.,0.]);normal=np.cross(across,along);normal/=np.linalg.norm(normal)
 if pan:
  us=np.linspace(-.061,.061,9);p=[(float(u),-.012+.012*(u/.061)**2)for u in us];p += [(u,z-.010)for u,z in p[::-1]]
 else:
  ts=np.linspace(0,math.pi,13);p=[(.054*math.cos(t),.054*math.sin(t)-.005)for t in ts]+[(.044*math.cos(t),.044*math.sin(t)-.005)for t in ts[::-1]]
 origin=[transverse,a,h(a)]if axis=='Y'else[a,transverse,h(a)]
 body=section(p,length)
 if not pan:
  ts=np.linspace(0,math.pi,13);lip=[(.059*math.cos(t),.059*math.sin(t)-.005)for t in ts]+[(.045*math.cos(t),.045*math.sin(t)-.005)for t in ts[::-1]]
  body=union([body,section(lip,min(.020,length)).translate([0,0,max(0,length-.020)])])
 return body.transform(np.c_[across,normal,along,origin])

def planes(names):
 groups={}
 for n in names:
  d=source(n);t=d['v'][d['f']]
  for tri in t:
   no=np.cross(tri[1]-tri[0],tri[2]-tri[0]);area=np.linalg.norm(no)/2
   if area<1e-8:continue
   no/=2*area
   if no[2]<.35:continue
   # A few millimetres of native float precision must not create separate roofs.
   co=np.array([-no[0]/no[2],-no[1]/no[2],no@tri[0]/no[2]])
   key=tuple(np.round(co,3));g=groups.setdefault(key,{'co':co,'polys':[],'area':0});g['polys'].append(Polygon(tri[:,:2]));g['area']+=area
 return [dict(g,poly=unary_union(g['polys']).buffer(0))for g in groups.values()if g['area']>.8]

def roof_tiles(tag,gs,cutter=None):
 rows=[];count=0
 for k,g in enumerate(gs):
  poly=g['poly'];co=g['co'];axis=g.get('axis','X'if abs(co[0])>abs(co[1])else'Y');crossax=1 if axis=='X'else 0;alongax=1-crossax;lo,hi=poly.bounds[crossax],poly.bounds[crossax+2];parts=[]
  phase=g.get('phase',lo+.061);start=phase+math.ceil((lo+.061-phase)/PITCH-1e-6)*PITCH
  for s in np.arange(start,hi-.01,PITCH):
   for pan,offset in [(False,0),(True,PITCH/2)]:
    ss=s+offset
    if ss+.061>hi+.001:continue
    line=LineString([[poly.bounds[0]-1,ss],[poly.bounds[2]+1,ss]])if axis=='X'else LineString([[ss,poly.bounds[1]-1],[ss,poly.bounds[3]+1]])
    hit=poly.intersection(line);lines=[hit]if hit.geom_type=='LineString'else list(hit.geoms)if hasattr(hit,'geoms')else[]
    for segment in lines:
     if segment.length<.025:continue
     qq=np.array(segment.coords);a=qq[:,alongax].min();b=qq[:,alongax].max();L=(b-a)*math.sqrt(1+co[alongax]**2);num=max(1,math.ceil(L/EXPOSE));step=(b-a)/num
     for j in range(num):
      aa=a+j*step;bb=min(b,aa+step+.016);aa+=.001;bb-=.001
      if bb-aa<.008:continue
      native_height=g.get('height')
      height=lambda t:(native_height(t,ss)if native_height else co[alongax]*t+co[crossax]*ss+co[2])+.023+.005*(bb-t)/(bb-aa)
      parts.append(tile(ss,aa,bb,height,axis,pan));count+=1
  if not parts:continue
  m=compose(parts)
  # Trim only the roof footprint edge; all unit seams retain a tiny shingled step.
  polys=[poly]if poly.geom_type=='Polygon'else list(poly.geoms);mask=union([section(list(p.exterior.coords)[:-1],20).translate([0,0,-2])for p in polys]);m=m^mask
  if cutter is not None:m=m-cutter
  name=f'V24_20_{tag}_Unified_Pan_Barrel_Slope_{k}';put(name,m,MAT,True);rows.append(name)
 return {'tag':tag,'objects':rows,'tile_units':count,'pitch_m':PITCH,'exposed_unit_length_m':EXPOSE,'segment_overlap_m':.014}

gs=planes(['ROOF_MAIN_JOINED_Geometry']);main=roof_tiles('House',gs)
OUT['remove'] += [n for n in INDEX if n.startswith('ROOF_MAIN_JOINED_TILE_ROWS_')]
# The kitchen's eastern return is part of the same tiled roof, not a different tile gauge.
tri=[]
for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','SITE_KITCHEN_V11_REGISTERED_EAST_EAVE_STRIP_Geometry']:
 d=source(n)
 for t in d['v'][d['f']]:
  nn=np.cross(t[1]-t[0],t[2]-t[0]);ll=np.linalg.norm(nn)
  if ll>1e-8 and nn[2]>.35*ll:tri.append(t)
tri=np.array(tri);aa=np.array([np.c_[t[:,:2],np.ones(3)].T for t in tri]);ok=abs(np.linalg.det(aa))>1e-9;tri=tri[ok];inv=np.linalg.inv(aa[ok]);co=np.array([np.linalg.solve(np.c_[t[:,:2],np.ones(3)],t[:,2])for t in tri]);centres=tri[:,:,:2].mean(1)
from functools import lru_cache
@lru_cache(maxsize=30000)
def kitchen_height(x,y):
 q=np.array([x,y,1.]);bc=np.einsum('nij,j->ni',inv,q);hits=(bc.min(1)>=-1e-5)
 if hits.any():return float(np.max(co[hits]@q))
 i=np.argmin(np.linalg.norm(centres-[x,y],axis=1));return float(co[i]@q)
poly=unary_union([Polygon(t[:,:2])for t in tri]).buffer(0)
# DJI_0598 / DJI_0525: a diagonal concave intersection of the two pitches.
# Both fields reach the same continuous bed instead of a rectangular notch.
kc=np.array([-.487509082361,.003126681698,10.020600366289])
sd=source('SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry');sv=sd['v']
sc=np.array([0.,-.4243148162,4.35-.022-.4243148162*12.15])
southco=np.array([0.,(4.35-3.03)/4.33,4.35-.022+(4.35-3.03)/4.33*12.15])
from v24_11_geometry import north_boundary
x0=float(sv[:,0].min());x1=float(sv[:,0].max());back=[(float(x),north_boundary(x)+.38)for x in np.linspace(x0,x1,130)]
spoly=Polygon([(x0,-12.15),(x1,-12.15)]+back[::-1]).buffer(0)
southpoly=box(x0,-16.48,x1,-12.15)
J=unary_union([spoly,box(11.7625,-12.15,x0+.002,-8.4697)]).intersection(box(11.7625,-12.15,15.30,-8.40)).buffer(0)
diff=kc-sc

def half_poly(co,positive=True):
 pts=[[-30.,-30.],[30.,-30.],[30.,20.],[-30.,20.]];out=[]
 if not positive:co=-co
 for a,b in zip(pts,pts[1:]+pts[:1]):
  a=np.array(a);b=np.array(b);da=np.dot(co,[*a,1]);db=np.dot(co,[*b,1]);ina=da>=0;inb=db>=0
  if ina:out.append(a)
  if ina!=inb:out.append(a+(b-a)*da/(da-db))
 return Polygon(out)

def footprint_solid(p,lo=-2.,hi=8.):
 ps=[p]if p.geom_type=='Polygon'else list(p.geoms)
 return union([section(list(q.exterior.coords)[:-1],hi-lo).translate([0,0,lo])for q in ps if q.area>1e-9])

def plane_bed(p,co,thick=.065):
 ps=[p]if p.geom_type=='Polygon'else list(p.geoms);ms=[]
 for q in ps:
  if q.area<1e-9:continue
  m=section(list(q.exterior.coords)[:-1],thick);ms.append(m.transform(np.array([[1,0,0,0],[0,1,0,0],[co[0],co[1],1,co[2]-thick]])))
 return union(ms)

JK=J.intersection(half_poly(diff));JS=J.difference(JK);jmask=footprint_solid(J)
SG=union([load(n)for n in ['V24_14_Storage_West_Sealed_Gable','V24_14_Storage_East_Sealed_Gable']])
kg=union([load(n)for n in ['V24_Kitchen_Gable_Upper_Brick_Infill','V24_03_Kitchen_Rear_Gable_Wall']])
jointbed=union([plane_bed(JK,kc),plane_bed(JS,sc)])-kg-SG
put('V24_20_Two_Rooms_Continuous_Valley_Roof_Bed',jointbed,MAT,True)
for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','SITE_KITCHEN_V11_REGISTERED_EAST_EAVE_STRIP_Geometry','SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry']:
 put(n,load(n)-jmask,MAT)
# Close only the actual wall footprints up to the new roof underside.
n='SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry';m=load(n);wallplan=m.slice(1.).extrude(5)
roofunder=union([plane_bed(JK,kc-np.array([0,0,.062]),2.5),plane_bed(JS,sc-np.array([0,0,.062]),2.5)])
seal=(wallplan^roofunder)^cube([11.75,-12.16,2.23],[15.31,-8.39,4.4]);put(n,union([m,seal])-kg-SG,INDEX[n]['materials'][0],transfer=True)
# A narrow sunken clay seam remains over the continuous, closed bed.
dk=diff.copy();dk[2]-=.018;ds=diff.copy();ds[2]+=.018
kpoly=unary_union([poly.difference(J),J.intersection(half_poly(dk))]).buffer(0)
storagepoly=unary_union([spoly.difference(J),J.intersection(half_poly(ds,False))]).buffer(0)
native_kitchen_height=kitchen_height
def joined_kitchen_height(x,y):
 return float(kc@np.array([x,y,1.]))if x>=11.76249 and y<-8.40 else native_kitchen_height(x,y)
gs=[{'poly':kpoly,'co':np.array([.42,0,0]),'axis':'X','height':joined_kitchen_height}]
gate=union([load(n)for n in ['V24_XIESHAN_01_Upper_Two_Main_Slopes','V24_XIESHAN_02_Four_Lower_Hipped_Eaves','V24_XIESHAN_07_Closed_Pale_Ceiling','V24_XIESHAN_08_Five_Continuous_Stepped_Eave_Bands','V24_XIESHAN_09_Continuous_Eave_Bearing_Core']]);guard=union([gate.translate(v)for v in [[0,0,0],[.003,0,0],[-.003,0,0],[0,.003,0],[0,-.003,0],[0,0,.003],[0,0,-.003]]]);k=roof_tiles('Kitchen',gs,union([kg,SG,guard]))
storage=roof_tiles('Storage',[
 {'poly':southpoly,'co':southco,'axis':'Y','phase':13.098},
 {'poly':storagepoly,'co':sc,'axis':'Y','phase':13.098}],union([kg,SG]))
rows=[r for r in OUT['objects']if r['name']in storage['objects']]
stiles=compose([solid(r['v'],r['f'])for r in rows])
for r in rows:OUT['objects'].remove(r)
put('SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry',stiles,MAT)
storage['objects']=['SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry']
line=J.intersection(LineString([[float((diff[1]*y+diff[2])/-diff[0]),y]for y in [-13.,-7.]]))
OUT['proof']['two_room_roof_junction']={'references':['DJI_0598.JPG','DJI_0525.JPG'],'cause':'A rectangular kitchen/storage exclusion left an abrupt open roof edge and exposed relocated timber.','method':'Replace that cut with the upper envelope of the existing kitchen east and storage north pitches, and terminate the two tiled fields on their diagonal concave intersection. The original ridge heads remain.','kitchen_plane':kc.tolist(),'storage_plane':sc.tolist(),'junction_polygon':list(J.exterior.coords),'valley_line_xy':list(line.coords)if line.geom_type=='LineString'else[str(line)],'clay_seam_height_difference_m':.036,'bed_object':'V24_20_Two_Rooms_Continuous_Valley_Roof_Bed','wall_top_infill_m3':float(seal.volume()),'timber_exclusion_reapplied_after_post_refit':True,'added_pipes_or_external_gutters':False,'fit_from_existing_model_and_photos':True}
OUT['remove'] += [n for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0_Geometry','SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_1_Geometry','V24_19_Kitchen_True_Tiled_Verge_Courses','V24_08_Registered_Kitchen_East_Eave_Ceramic_Courses']if n in INDEX]
OUT['proof']['roof_tiles']={'main':main,'kitchen':k,'storage':dict(storage,object='SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry'),'material':MAT,'reference':'DJI_0016.JPG','existing_roof_pitches_preserved_and_extended_into_junction':True,'metal_awnings_and_pavilion_shingles_preserved':True,'coplanar_tile_overlaps_avoided_by_unit_step':True}
