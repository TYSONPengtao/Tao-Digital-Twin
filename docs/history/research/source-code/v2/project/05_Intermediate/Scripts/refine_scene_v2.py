import sys,json,math,csv,copy,collections
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,mapbox_earcut
from shapely.geometry import Polygon,LineString,Point,box as rect
from shapely.ops import unary_union
from shapely.ops import linemerge
from shapely.geometry.polygon import orient
from shapely import set_precision
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter
from scipy.ndimage import gaussian_filter1d
OLD=Path(r'E:\jz\JIA\Rebuild');OUT=Path(r'E:\jz\JIA\Rebuild_V2')
for d in ['01_Source','02_PDF_Reference','03_Insta360_Frames','04_ContextCapture','05_Intermediate','06_Rhino','07_SketchUp','08_Export','09_Report']:(OUT/d).mkdir(parents=True,exist_ok=True)
S=json.loads((OLD/'05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));old=copy.deepcopy(S['elements']);D=S['definitions'];M=S['materials']
M.update({'M_Wall_Exterior':{'color':[239,239,232],'roughness':.78},'M_Site_Paving':{'color':[153,153,144],'roughness':.82},'M_Stone_Rubble':{'color':[116,114,100],'roughness':1},'M_Blue_Sheet':{'color':[47,144,187],'roughness':.4,'metallic':.5},'M_Green_Sheet':{'color':[123,145,140],'roughness':.45,'metallic':.6},'M_Leaves':{'color':[63,98,48],'roughness':.9}})
def part(g,mat):return {'geometry':g,'material':mat}
def box(x,y,z,w,d,h):return {'type':'box','origin':[x,y,z],'size':[w,d,h]}
def prism(p,v):return {'type':'prism','profile':p,'vector':v}
def add(name,parts,layer='60_SITE',source='JIA.ccm linked OBJ2 / 3MX + supplied aerial views',confidence='MEDIUM',family='SITE_MODEL',**kw):
 e=dict(name=name,parts=parts,layer=layer,source=source,confidence=confidence,family=family,**kw);S['elements'].append(e);return e
def polys(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g] if g.area>1e-8 else []
 if not hasattr(g,'geoms'):return []
 return [x for x in g.geoms if x.geom_type=='Polygon' and x.area>1e-9]
def pg(g,z,h,mat):
 g=set_precision(g,1e-6).simplify(1e-7,preserve_topology=True)
 a=[]
 for p in polys(g):
  p=orient(p,1);outer=list(p.exterior.coords)[:-1];holes=[list(q.coords)[:-1] for q in p.interiors]
  a.append(part({'type':'prism_holes','outer':outer,'holes':holes,'z':z,'height':h},mat))
 return a
def gp(g):
 if g['type']=='box':x,y,z=g['origin'];w,d,h=g['size'];return rect(x,y,x+w,y+d),z,z+h
 if g['type']=='prism':p=np.array(g['profile']);return Polygon(p[:,:2]),float(p[0,2]),float(p[0,2]+g['vector'][2])
 raise ValueError(g['type'])
# Preserve the interiors and true grid; replace defective perimeter objects and proxies.
remove=lambda e:e['layer']=='60_SITE' or e['name'].startswith(('COURTYARD_WALL','SITE_TERRAIN','WALL_','BAY_WALL','SLAB_','ROOF_','GZY_','COLUMN_MOULD','FRONT_BAND','CANOPY_LEFT','TERRACE_'))
S['elements']=[e for e in old if not remove(e) and not e['name'].startswith('BALCONY_STONE')]
S['elements']=[e for e in S['elements'] if not(e['layer']=='11_WALL_INT' or e['name'].startswith('PARTITION_BED_F3_X3.9'))]
for f in range(3):
 z=[0,3.9,7.5][f];H=[3.77,3.47,3.17][f]
 ext=[e for e in old if e['name'].startswith(('WALL_','BAY_WALL')) and f'F{f+1}' in e['name']]
 ints=[e for e in old if (e['layer']=='11_WALL_INT' or e['name'].startswith('PARTITION_BED_F3_X3.9')) and f'F{f+1}' in e['name']]
 cols=[rect(e['origin'][0]-.2,e['origin'][1]-.2,e['origin'][0]+.2,e['origin'][1]+.2) for e in old if e['name'].startswith('KZ_') and f'F{f+1}' in e['name']]
 colunion=unary_union(cols)
 outside=[q for q in cols if q.bounds[0]<.01 or q.bounds[2]>12.99 or q.bounds[3]>9.79 or (q.bounds[1]<2.11 and not(f==2 and q.bounds[0]<.01))]
 sleeves=unary_union([q.buffer(.012,join_style=2).difference(q) for q in outside])
 # Slice at every opening head/sill, then union footprints and remove the core columns.
 ext_parts=[gp(p['geometry']) for e in ext for p in e['parts']]
 int_parts=[gp(p['geometry']) for e in ints for p in e['parts']]
 zs=sorted({round(t,6) for a,b,c in ext_parts+int_parts for t in [b,c]}|{z,z+H})
 ep=[];ip=[]
 for a,b in zip(zs[:-1],zs[1:]):
  if b-a<1e-6:continue
  mid=(a+b)/2
  exterior=unary_union([q for q,l,u in ext_parts if l-1e-8<mid<u+1e-8]).union(sleeves).difference(colunion)
  interior=unary_union([q for q,l,u in int_parts if l-1e-8<mid<u+1e-8]).difference(colunion).difference(exterior)
  ep+=pg(exterior,a,b-a,'M_Wall_Exterior');ip+=pg(interior,a,b-a,'M_Wall_Interior')
 add(f'FACADE_CONTINUOUS_F{f+1}',ep,'10_WALL_EXT','D03/D04 openings; V2 plan unions, corner sleeves and column cutouts','MEDIUM','ARCH_MODEL',junctions='Plan unions, no overlapping wall corners')
 add(f'PARTITIONS_JOINED_F{f+1}',ip,'11_WALL_INT','D03/D04; existing door openings retained','MEDIUM','ARCH_MODEL')
 floorpolys=[gp(p['geometry'])[0] for e in old if e['name'].startswith(f'SLAB_F{f+1}_') for p in e['parts']]
 floor=unary_union(floorpolys).union(colunion)
 # A narrow slab edge must remain below the rear wall around the stair well.
 floor=floor.union(rect(3.7,9.7,8.0,10.0)).union(rect(3.7,7.3,4.1,10.0))
 if f>0:floor=floor.difference(rect(4.1,7.4,7.8,9.7))
 floor=floor.buffer(0)
 thick=.15 if f==0 else .13
 add(f'SLAB_JOINED_F{f+1}',pg(floor,z-thick,thick,'M_Concrete'),'22_SLAB','D03,D04,D19-D21; joined plan boundary','HIGH' if f else 'MEDIUM','ARCH_MODEL',stair_opening='4.1..7.8 / 7.4..9.7; perimeter support retained')
 if f:
  fascia=floor.buffer(.055,join_style=2).difference(floor)
  add(f'FLOOR_FASCIA_CONTINUOUS_F{f+1}',pg(fascia,z-.25,.25,'M_Stone'),'51_CANOPY','D05 and video 79s; continuous offset of slab boundary','MEDIUM','ARCH_MODEL')
# Closed roofs share one set of eave/ridge vertices; there are no intersecting facet solids.
def roof(name,x0,y0,x1,y1,eave,ridge,kind='hip',mat='M_Roof',layer='50_ROOF',family='ARCH_MODEL',t=.1):
 if kind=='hip':
  cx=(x0+x1)/2;inset=min((x1-x0)/2,(y1-y0)*.24);top=[[x0,y0,eave],[x1,y0,eave],[x1,y1,eave],[x0,y1,eave],[cx,y0+inset,ridge],[cx,y1-inset,ridge]];ff=[[0,1,4],[1,2,5,4],[2,3,5],[3,0,4,5]]
 elif kind=='gable':
  cx=(x0+x1)/2;top=[[x0,y0,eave],[x1,y0,eave],[x1,y1,eave],[x0,y1,eave],[cx,y0,ridge],[cx,y1,ridge]];ff=[[0,4,5,3],[4,1,2,5]]
 else:top=[[x0,y0,eave],[x1,y0,eave],[x1,y1,ridge],[x0,y1,ridge]];ff=[[0,1,2,3]]
 # Gable roofs need two end slope edges as well as the four corner edges.
 perimeter=[0,4,1,2,5,3] if kind=='gable' else [0,1,2,3]
 N=len(top);v=top+[[x,y,z-t] for x,y,z in top];faces=ff+[[i+N for i in f[::-1]] for f in ff]+[[b,a,a+N,b+N] for a,b in zip(perimeter,perimeter[1:]+perimeter[:1])]
 e=add(name,[part({'type':'polyhedron','vertices':v,'faces':faces},mat)],layer,'D04/D05 + CCM orthographic actual roof; V2 joined shell','MEDIUM',family,roof_type=kind,thickness=t)
 # Closely spaced ceramic ridges, clipped to each top facet, are editable VIS details.
 if mat=='M_Roof':
  for fi,face in enumerate(ff):
   p=np.array([top[k] for k in face]);n=np.cross(p[1]-p[0],p[2]-p[0]);n=n/n[2];poly=Polygon(p[:,:2]);ribs=[]
   along_y=abs(n[0])>abs(n[1])
   low,high=(poly.bounds[1],poly.bounds[3]) if along_y else (poly.bounds[0],poly.bounds[2])
   for u in np.arange(low+.1,high,.20):
    line=LineString([(x0-1,u),(x1+1,u)]) if along_y else LineString([(u,y0-1),(u,y1+1)])
    hit=poly.intersection(line)
    if hit.is_empty or hit.geom_type!='LineString' or hit.length<.06:continue
    aa=np.array(hit.coords[0]);bb=np.array(hit.coords[-1]);a3=np.r_[aa,p[0,2]-np.dot(n[:2],aa-p[0,:2])+.012];b3=np.r_[bb,p[0,2]-np.dot(n[:2],bb-p[0,:2])+.012];v3=b3-a3;unit=v3/np.linalg.norm(v3);u3=np.cross(unit,[0,0,1]);u3/=np.linalg.norm(u3);vperp=np.cross(unit,u3)
    pr=[(a3+.018*(math.cos(q)*u3+math.sin(q)*vperp)).tolist() for q in np.linspace(0,2*math.pi,8,endpoint=False)]
    ribs.append(part(prism(pr,v3.tolist()),'M_Roof'))
   add(name+f'_TILE_ROWS_{fi}',ribs,layer,'CCM and supplied views; 200mm nominal tile pitch','MEDIUM','VIS_MODEL')
 return e
roof('ROOF_MAIN_JOINED',3.1,.6,13.8,10.6,10.6,12)
add('ROOF_EAVE_FASCIA',pg(rect(3.05,.55,13.85,10.65).difference(rect(3.18,.68,13.72,10.52)),10.42,.16,'M_Stone'),'50_ROOF','CCM roof eave; continuous closed ring','MEDIUM','ARCH_MODEL')
add('UTILITY_FLAT_ROOF_WEST',pg(rect(-.15,6.6,3.85,10.0),10.60,.20,'M_Concrete'),'50_ROOF','CCM visible utility terrace and water heater','MEDIUM','ARCH_MODEL')
add('UTILITY_PARAPET_WEST',pg(rect(-.15,6.6,3.85,10).difference(rect(.05,6.8,3.65,9.8)),10.8,.28,'M_Wall_Exterior'),'50_ROOF','CCM utility roof parapet','MEDIUM','ARCH_MODEL')
roof('TERRACE_METAL_CANOPY',-.2,1.0,3.45,6.65,10.22,10.40,'shed','M_Green_Sheet','51_CANOPY','ARCH_MODEL',.05)
for x in [0,3.3]:
 add(f'TERRACE_CANOPY_POST_{x}',[part(box(x-.025,1.1,7.5,.05,.05,2.673),'M_Metal_Black')],'51_CANOPY','CCM metal terrace canopy visible; 50mm section inferred','MEDIUM','ARCH_MODEL')
collector=[[.45,7.2,10.85],[2.9,7.2,10.85],[2.9,8.7,11.75],[.45,8.7,11.75]]
add('ROOF_SOLAR_COLLECTOR',[part(prism(collector,[0,0,-.06]),'M_Metal_Black')],'70_EQUIPMENT','CCM aerial solar hot-water collector; dimensions estimated','MEDIUM','ARCH_MODEL')
for x in [.5,2.85]:add(f'ROOF_SOLAR_SUPPORT_{x}',[part(box(x,8.55,10.8,.05,.05,.88),'M_Metal_Stainless')],'70_EQUIPMENT','CCM roof equipment','MEDIUM','ARCH_MODEL')
profile=[[.45,8.8+.20*math.cos(t),11.70+.20*math.sin(t)] for t in np.linspace(0,2*math.pi,32,endpoint=False)]
add('ROOF_SOLAR_WATER_TANK',[part(prism(profile,[2.45,0,0]),'M_Metal_Stainless')],'70_EQUIPMENT','CCM solar heater tank approximate','MEDIUM','ARCH_MODEL')
add('TERRACE_STONE_PARAPET',pg(LineString([(0,7.25),(0,1.1),(3.7,1.1)]).buffer(.10,cap_style=2,join_style=2),7.5,.90,'M_Stone'),'41_RAILING','CCM supplied front view; solid terrace parapet','MEDIUM','ARCH_MODEL')
# Roman columns: separate touching turned base, fluted tapered shaft and moulded capital.
for z,H in [(0,3.50),(3.9,3.20)]:
 key=f'ROMAN_FLUTED_D250_H{int(H*1000)}'
 base=[[.205,0],[.205,.055],[.215,.065],[.215,.11],[.198,.13],[.175,.16],[.175,.20],[.151,.25],[.145,.30]]
 shaft=[[.145,.30],[.146,H*.18],[.145,H*.38],[.139,H*.65],[.131,H-.34]]
 cap=[[.131,H-.34],[.151,H-.30],[.155,H-.26],[.177,H-.23],[.192,H-.18],[.192,H-.13],[.218,H-.11],[.218,H-.055],[.205,H]]
 D[key]={'parts':[part({'type':'lathe','profile':p,'segments':128,'flutes':fl},'M_Stone') for p,fl in [(base,0),(shaft,16),(cap,0)]],'parameters':{'StructuralDiameter':.25,'FinishedShaftDiameter':.29,'BaseDiameter':.43,'CapitalDiameter':.436,'Height':H,'Flutes':16,'GrooveDepth':.006},'source':'D22 structural D250; video79s/377s flutes and mouldings; finish dimensions estimated','confidence':'MEDIUM'}
 for x in [3.9,9.1]:add(f'ROMAN_COLUMN_X{x}_Z{z}',[],'20_COLUMN',D[key]['source'],'MEDIUM','ARCH_MODEL',definition=key,origin=[x,0,z],angle=0)
 # Shallow arch joins capital spring points to the underside of the balcony/canopy.
 top=z+H+.27;xx=np.linspace(3.9,9.1,49);under=[z+H+.23*math.sin((x-3.9)/5.2*math.pi) for x in xx];profile=[[3.9,-.12,top],[9.1,-.12,top]]+[[float(x),-.12,float(h)] for x,h in zip(xx[::-1],under[::-1])]
 add(f'PORCH_ARCH_BEAM_Z{z}',[part(prism(profile,[0,.24,0]),'M_Wall_Exterior')],'51_CANOPY','CCM entrance arch; PDF level datum, arch rise visually estimated','MEDIUM','ARCH_MODEL')
rail=LineString([(3.9,1.9),(3.9,0),(9.1,0),(9.1,1.9)]).buffer(.09,cap_style=2,join_style=2)
for x in [3.9,9.1]:rail=rail.difference(Point(x,0).buffer(.222,quad_segs=32))
add('BALCONY_STONE_JOINED',pg(rail,3.9,.92,'M_Stone'),'41_RAILING','Video377s stone parapet; joined corners and trimmed column seats','MEDIUM','ARCH_MODEL')
add('BALCONY_STONE_COPING_JOINED',pg(rail.buffer(.025,join_style=2),4.82,.13,'M_Stone'),'41_RAILING','Video377s coping width estimated','MEDIUM','ARCH_MODEL')
# Survey ground is rebuilt from samples at regular spacing, independently of source triangles.
a=np.load(OLD/'05_Intermediate/Reality_Geometry.npz');p=a['points'];theta=math.radians(19.65);R=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]]);p[:,:2]=(p[:,:2]-S['coordinate']['origin'][:2])@R;p[:,2]-=S['coordinate']['origin'][2]
q=p[(abs(a['normals'][:,2])>.75)&(p[:,2]<1.2)];tree=cKDTree(q[:,:2]);cache={}
def rawz(x,y):
 d,i=tree.query([x,y],k=96);return float(np.quantile(q[i,2],.05))
sx=np.arange(-32,27,.75);sy=np.arange(-30,23,.75);zz=np.array([[rawz(x,y) for x in sx] for y in sy]);zz=gaussian_filter(zz,.85)
def gz(x,y):
 k=(round(x,5),round(y,5))
 if k not in cache:
  ix=max(0,min(len(sx)-2,int((x-sx[0])/.75)));iy=max(0,min(len(sy)-2,int((y-sy[0])/.75)));ax=(x-sx[ix])/.75;ay=(y-sy[iy])/.75;cache[k]=float(zz[iy,ix]*(1-ax)*(1-ay)+zz[iy,ix+1]*ax*(1-ay)+zz[iy+1,ix]*(1-ax)*ay+zz[iy+1,ix+1]*ax*ay)
 return cache[k]
def crest(x,y,default):
 near=p[(abs(p[:,0]-x)<.45)&(abs(p[:,1]-y)<.45)&(p[:,2]<4.0)]
 return float(np.quantile(near[:,2],.88)) if len(near)>20 else default
def xy(px,py):return [-29+px/1600*52,20-py/1600*52]
north_px=[(123,443),(218,424),(330,396),(447,359),(552,319),(655,283),(768,254),(865,245),(1023,250),(1190,267),(1370,295)]
west_px=[(123,443),(146,521),(195,640),(245,724),(286,795),(347,860),(423,936),(496,1007)]
south_px=[(496,1007),(643,1059),(796,1102),(929,1131),(985,1142),(1090,1144),(1220,1134),(1350,1120),(1468,1100)]
east_px=[(1370,295),(1355,432),(1340,573),(1335,675),(1330,790),(1340,870),(1475,891),(1485,995),(1468,1100)]
north=[xy(*c) for c in north_px];west=[xy(*c) for c in west_px];south=[xy(*c) for c in south_px];east=[xy(*c) for c in east_px]
control_outline=north+east[1:]+south[-2::-1]+west[-2:0:-1]
def curved_outline(control):
 pp=np.array(control);u=np.roll(pp,-1,axis=0)-pp;L=np.linalg.norm(u,axis=1);u=u/L[:,None];smooth=[]
 for i in range(len(pp)):
  angle=math.acos(np.clip(np.dot(u[i-1],u[i]),-1,1));smooth.append(angle<math.radians(32))
 result=[]
 for i in range(len(pp)):
  j=(i+1)%len(pp);ta=(u[i-1]+u[i])/np.linalg.norm(u[i-1]+u[i]) if smooth[i] else u[i];tb=(u[i]+u[j])/np.linalg.norm(u[i]+u[j]) if smooth[j] else u[i]
  for t in np.linspace(0,1,max(2,int(L[i]/1.0)+1),endpoint=False):result.append(((2*t**3-3*t*t+1)*pp[i]+(t**3-2*t*t+t)*L[i]*ta+(-2*t**3+3*t*t)*pp[j]+(t**3-t*t)*L[i]*tb).tolist())
 return result
outline=curved_outline(control_outline);plot=Polygon(outline).buffer(0)
maincourt=Polygon([[0,1.1],[13.2,1.1],[14.6,-11.7],[13.6,-16.4],[3,-17.1],[-12.9,-12.7],[-17.7,-7.95],[-11.4,-8.6],[-5,-10.5],[0,-10.7]]).intersection(plot)
house=unary_union([gp(pp['geometry'])[0] for e in old if e['name'].startswith('SLAB_F1') for pp in e['parts']])
kitchen=rect(7.7,-11.6,13.35,-2.6);annex=rect(13.8,-16.2,18.9,-9.7)
gazebo=rect(-.7,-7.3,4.15,-2.7)
shed1=Polygon([xy(150,456),xy(548,356),xy(590,527),xy(217,594)])
shed2=Polygon([xy(532,353),xy(597,342),xy(633,521),xy(565,535)])
shed3=Polygon([xy(249,682),xy(395,621),xy(481,841),xy(354,861)])
pergola=rect(-11.5,-10.4,-6.6,-5.9)
footprints=unary_union([house,kitchen,annex,gazebo,shed1,shed2,shed3,pergola])
roadline=LineString(list(reversed(north))+west[1:]+south[1:])
# Outward road follows the actual wall and has one continuous unioned outline.
road=roadline.buffer(5.1,cap_style=2,join_style=1).difference(plot.buffer(.22)).intersection(rect(-29,-24,23,19))
eastgarden=Polygon([[15.6,10.4],[23,11],[23,-9.7],[18.9,-9.7],[14.7,-8.3]]).difference(plot)
context=rect(-29,-27,23,19).difference(unary_union([plot,road,eastgarden]))
def terrain(name,poly,mat,step=1.2,flat=None):
 verts=[];faces=[];index={}
 def vi(x,y):
  key=(round(x,7),round(y,7))
  if key not in index:index[key]=len(verts);verts.append([key[0],key[1],float(flat if flat is not None else gz(*key))])
  return index[key]
 for component in polys(poly):
  x0,y0,x1,y1=component.bounds
  for x in np.arange(math.floor(x0/step)*step,x1,step):
   for y in np.arange(math.floor(y0/step)*step,y1,step):
    cell=component.intersection(rect(x,y,x+step,y+step))
    for pp in polys(cell):
     pp=orient(pp,1);rings=[list(pp.exterior.coords)[:-1]]+[list(h.coords)[:-1] for h in pp.interiors];v=np.array([u for ring in rings for u in ring]);ends=np.cumsum([len(ring) for ring in rings]).astype(np.uint32);ts=mapbox_earcut.triangulate_float64(v,ends).reshape(-1,3);ids=[vi(*u) for u in v]
     faces.extend([[ids[j] for j in t] for t in ts])
 return add(name,[part({'type':'terrain','vertices':verts,'faces':faces},mat)],surface_only=True,ground_method='1.2m clipped grid; nearest ground samples lower quantile, no original source triangles',area_m2=poly.area)
terrain('SITE_MAIN_COURTYARD_PAVING',maincourt.difference(footprints).difference(rect(4,-17.6,10,-12)),'M_Site_Paving',.9,flat=-.45)
terrain('SITE_WEST_EARTH_COURTYARD',plot.difference(unary_union([maincourt,footprints])),'M_Soil',1.0)
terrain('SITE_CURVED_PUBLIC_ROAD',road,'M_Asphalt',1.3)
terrain('SITE_EAST_GARDEN',eastgarden,'M_Grass',1.6)
terrain('SITE_CONTEXT_TERRAIN',context,'M_Grass',2.0)
# Retaining walls share clipped plan boundaries and measured coping levels.
def wallchain(name,pts,width=.32,stone=True,height=None):
 parts=[];caps=[]
 pts=np.array(pts,float);us=np.diff(pts,axis=0);us/=np.linalg.norm(us,axis=1)[:,None];norms=np.c_[-us[:,1],us[:,0]];offsets=[]
 for j in range(len(pts)):
  n=norms[0] if j==0 else norms[-1] if j==len(pts)-1 else (norms[j-1]+norms[j])/2
  if 0<j<len(pts)-1:n=n/max(.15,np.dot(n,norms[j]))
  offsets.append(n*width/2)
 zbase=[];ztop=[]
 for aa,nn in zip(pts,offsets):
  zz=min(gz(*aa),gz(*(aa+nn*6)),gz(*(aa-nn*6)));tt=crest(*aa,.55) if height is None else zz+height;zbase.append(zz);ztop.append(max(tt,zz+.8))
 if height is None:ztop=gaussian_filter1d(np.array(ztop),1.4).tolist()
 paintheights=[min(.9,(tt-zz)*.6) for tt,zz in zip(ztop,zbase)]
 for i,(a0,b0) in enumerate(zip(pts[:-1],pts[1:])):
  a=np.array(a0);b=np.array(b0);u=(b-a)/np.linalg.norm(b-a);na=offsets[i];nb=offsets[i+1];za,zb=zbase[i:i+2];ta,tb=ztop[i:i+2]
  pa,pb=paintheights[i:i+2]
  v=[[*a-na,za],[*b-nb,zb],[*b+nb,zb],[*a+na,za],[*a-na,ta-pa],[*b-nb,tb-pb],[*b+nb,tb-pb],[*a+na,ta-pa]]
  ff=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
  parts.append(part({'type':'polyhedron','vertices':v,'faces':ff},'M_Stone_Rubble' if stone else 'M_Wall_Exterior'))
  # White render upper strip and tile coping are separate materials, with matching bases.
  v2=[[*a-na,ta-pa],[*b-nb,tb-pb],[*b+nb,tb-pb],[*a+na,ta-pa],[*a-na,ta],[*b-nb,tb],[*b+nb,tb],[*a+na,ta]]
  parts.append(part({'type':'polyhedron','vertices':v2,'faces':ff},'M_Wall_Exterior'))
  # Gable tile cap cross sections follow the sloping wall crest.
  va=[[*a-na*1.25,ta],[*a+na*1.25,ta],[*a,ta+.17]];vb=[[*b-nb*1.25,tb],[*b+nb*1.25,tb],[*b,tb+.17]]
  caps.append(part({'type':'polyhedron','vertices':va+vb,'faces':[[2,1,0],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]]},'M_Roof'))
 add(name,parts,retaining_wall=True,plan_width=width);add(name+'_TILE_COPING',caps)
perimeter_line=linemerge(LineString(outline+[outline[0]]).difference(rect(3.6,-18,10.6,-15)))
wallchain('SITE_PERIMETER_JOINED_RETAINING_WALL',list(perimeter_line.coords))
wallchain('SITE_INTERNAL_YARD_DIVIDER',[[0,1],[0,-10.7],[-5,-10.5],[-11.4,-8.6],[-17.7,-7.95]],.25,False,2.25)
wallchain('SITE_INNER_ENTRY_WALL',[[0,-11.7],[4.1,-11.7]],.25,False,2.4)
wallchain('SITE_GATE_TO_KITCHEN_WALL',[[9.2,-11.7],[13.3,-11.7]],.25,False,2.4)
# Buildings are clean wall groups with openings, floors, beams and closed roofs.
def smallbuilding(name,foot,z,eave,ridge,kind='gable',openfront=True,mat='M_Wall_Exterior'):
 x0,y0,x1,y1=foot.bounds;wall=foot.difference(foot.buffer(-.22,join_style=2));opening=rect((x0+x1)/2-.55,y0-.3,(x0+x1)/2+.55,y0+.5)
 add(name+'_FLOOR',pg(foot,z-.12,.12,'M_Concrete'))
 if name=='SITE_KITCHEN':
  cy=(y0+y1)/2;door=rect(x0-.3,cy-1.1,x0+.5,cy+1.1);win=rect(x0-.3,y1-2.2,x0+.5,y1-.8)
  parts=pg(wall.difference(door),z,.70,mat)+pg(wall.difference(door.union(win)),z+.70,1.3,mat)+pg(wall.difference(door),z+2.0,.2,mat)+pg(wall,z+2.2,eave-z-2.2,mat)
  add(name+'_WALLS',parts,source='CCM footprint and video79s west-facing timber door/window; clear sizes estimated')
  woodparts=[part(box(0,-.04,0,.06,.08,2.2),'M_Wood'),part(box(2.14,-.04,0,.06,.08,2.2),'M_Wood'),part(box(.06,-.04,2.14,2.08,.08,.06),'M_Wood')]
  for j in range(2):
   xx=.06+j*1.04;woodparts.append(part(box(xx,-.027,0,1.04,.054,1.0),'M_Wood'))
   for u in np.linspace(xx+.04,xx+1.0,9):woodparts.append(part(box(float(u),-.027,1.0,.025,.054,1.14),'M_Wood'))
  D['KITCHEN_TIMBER_LATTICE_DOOR']={'parts':woodparts,'parameters':{'Width':2.2,'Height':2.2,'Finish':'wood','Confidence':'estimated'},'source':'Video79s timber lattice entrance in west kitchen facade','confidence':'MEDIUM'}
  add(name+'_WOOD_LATTICE_DOOR',[],'60_SITE','Video79s; width and height estimated','MEDIUM','SITE_MODEL',definition='KITCHEN_TIMBER_LATTICE_DOOR',origin=[x0,cy-1.1,z],angle=math.pi/2)
  add(name+'_WOOD_WINDOW',[part(box(x0-.055,y1-2.2,z+.7,.11,.06,1.3),'M_Wood'),part(box(x0-.055,y1-.86,z+.7,.11,.06,1.3),'M_Wood'),part(box(x0-.055,y1-2.14,z+.7,.11,1.28,.06),'M_Wood'),part(box(x0-.055,y1-2.14,z+1.94,.11,1.28,.06),'M_Wood'),part(box(x0-.003,y1-2.14,z+.76,.006,1.28,1.18),'M_Glass_Clear')],source='Video79s west kitchen window; opening size and position approximated')
 else:
  add(name+'_WALLS',pg(wall.difference(opening) if openfront else wall,z,2.05,mat)+pg(wall,z+2.05,max(.12,eave-z-2.05),'M_Wall_Exterior' if mat=='M_Wall_Exterior' else mat))
  if openfront:add(name+'_DOOR',[part(box((x0+x1)/2-.55,y0+.02,z,1.1,.055,2.05),'M_Wood')])
 roof(name+'_ROOF',x0-.25,y0-.3,x1+.25,y1+.3,eave,ridge,kind,'M_Roof','60_SITE','SITE_MODEL')
smallbuilding('SITE_KITCHEN',kitchen,-.40,2.95,4.65)
smallbuilding('SITE_SOUTH_EAST_ANNEX',annex,-.40,2.90,4.45,'hip')
for i,foot in enumerate([shed1,shed2,shed3]):
 base=-.45;parts=[]
 for x,y in list(foot.exterior.coords)[:-1]:parts.append(part(box(x-.07,y-.07,base,.14,.14,2.55),'M_Wood'))
 add(f'SITE_SHED_{i+1}_POSTS',parts)
 # Extrude the actual oblique footprint to a single sloped sheet roof.
 co=list(orient(foot,1).exterior.coords)[:-1];yy=[p[1] for p in co];lo,hi=min(yy),max(yy)
 roofp=[[x,y,2.25+.45*(y-lo)/(hi-lo)] for x,y in co]
 add(f'SITE_SHED_{i+1}_ROOF',[part(prism(roofp,[0,0,-.065]),'M_Blue_Sheet' if i==1 else 'M_Metal_Stainless')],shed_type='open-sided farm shed')
 back=LineString(co[:2]).buffer(.1,cap_style=2);add(f'SITE_SHED_{i+1}_BACK_WALL',pg(back,base,1.15,'M_Stone_Rubble'))
for name,foot,eave,ridge,mat in [('SITE_GAZEBO',gazebo,2.6,3.20,'M_Green_Sheet'),('SITE_WEST_PERGOLA',pergola,1.75,2.0,'M_Wood')]:
 parts=[]
 for x,y in list(foot.exterior.coords)[:-1]:parts.append(part(box(x-.05,y-.05,-.45,.1,.1,eave+.45),'M_Wood'))
 add(name+'_POSTS',parts)
 x0,y0,x1,y1=foot.bounds;roof(name+'_ROOF',x0,y0,x1,y1,eave,ridge,'hip',mat,'60_SITE','SITE_MODEL',.06)
# Inner red gate and outer tiled portal, allowing the actual entry passage.
def gate(name,x0,x1,y,z,H,depth=.55):
 b=.28;pp=[part(box(x0,y-depth/2,z,b,depth,H),'M_Wall_Exterior'),part(box(x1-b,y-depth/2,z,b,depth,H),'M_Wall_Exterior'),part(box(x0+b,y-depth/2,z+H-.3,x1-x0-2*b,depth,.3),'M_Wall_Exterior')]
 add(name+'_FRAME',pp)
 add(name+'_RED_DOORS',[part(box(x0+b,y-.06,z,x1-x0-2*b,.08,H-.3),'MAT_DOOR_FRAME_RED')])
 roof(name+'_TILED_ROOF',x0-.3,y-.75,x1+.3,y+.75,z+H,z+H+.55,'gable','M_Roof','60_SITE','SITE_MODEL')
gate('SITE_INNER_RED_GATE',4.1,9.2,-11.7,-.45,2.65)
gate('SITE_OUTER_ENTRY_PORTAL',3.6,10.6,-16.7,-2.7,3.5)
# Entry ramp follows the measured road-to-courtyard rise.
rp=[[4.0,-17.6,gz(4,-17.6)],[10,-17.6,gz(10,-17.6)],[10,-12,-.45],[4,-12,-.45]]
add('SITE_ENTRY_RAMP',[part({'type':'terrain','vertices':rp,'faces':[[0,1,2],[0,2,3]]},'M_Site_Paving')],surface_only=True)
# Observable vegetation and garden beds are modest, editable contextual geometry.
for i,(x,y,r,H) in enumerate([(16,5,1.15,3),(18,1,1.3,3.4),(20,-4,1.4,3.2),(16,-8,1.1,2.5),(-4,-13.5,.9,2),(0,-15.2,.9,2.1)]):
 z=gz(x,y);trunk={'type':'cylinder','origin':[x,y,z],'radius':.065,'height':H*.65,'segments':16};vs=[];fs=[]
 vs.append([x,y,z+H*.65+r])
 for j in range(1,6):
  a=math.pi*j/6
  for k in range(16):v=2*math.pi*k/16;vs.append([x+r*math.sin(a)*math.cos(v),y+r*math.sin(a)*math.sin(v),z+H*.65+r*math.cos(a)])
 vs.append([x,y,z+H*.65-r]);bottom=len(vs)-1
 for k in range(16):fs.append([0,1+k,1+(k+1)%16]);fs.append([bottom,65+(k+1)%16,65+k])
 for j in range(4):
  for k in range(16):fs.append([1+j*16+k,1+(j+1)*16+k,1+(j+1)*16+(k+1)%16,1+j*16+(k+1)%16])
 add(f'SITE_TREE_{i+1}',[part(trunk,'M_Wood'),part({'type':'polyhedron','vertices':vs,'faces':fs},'M_Leaves')],vegetation='Observed positions approximate canopy volume, no species claim')
for i,(x,y) in enumerate([(1,-1),(10.5,-1),(3.2,-7.5)]):add(f'SITE_PLANTER_{i}',[part({'type':'cylinder','origin':[x,y,-.45],'radius':.25,'height':.35,'segments':24},'M_Wood')])
# PDF boundary remains a documentary overlay, rather than being confused with surveyed title limits.
pdfline=[[0,9.8],[13,9.8],[13,-14],[0,-14],[0,9.8]]
add('PDF_D01_SCOPE_REFERENCE',[part({'type':'line','points':[[x,y,.03] for x,y in pdfline]},'M_Uncertain')],'00_REFERENCE','D01 main house and south courtyard schematic scope; no boundary dimensions','LOW','REFERENCE',status='SCHEMATIC_SCOPE_NOT_TITLE_BOUNDARY')
S['cameras']=[dict(name=n,position=p,target=t,fov=f,status='REVIEW_CAMERA') for n,p,t,f in [
 ('CAM_01_Entrance',[6.5,-1.3,2.6],[6.5,2.1,2.1],70),('CAM_02_Front',[28,-22,14],[6.5,2.8,5.4],45),('CAM_03_Back',[24,25,15],[6.5,5,5.5],45),('CAM_04_Courtyard',[-27,-25,15],[-2,-3,3],50),('CAM_05_Aerial',[33,-45,48],[-4,-2,1],48),('CAM_06_Whole_Site',[-41,-49,36],[-4,-2,2],50),('CAM_07_Column',[4.5,-1.5,1.9],[9.1,0,1.75],65),('CAM_08_Junction',[16,-1,6],[10.5,1.5,4.5],40)]]
S['name']='Production_1QK_Rebuild_V2';S['status']='V2_BUILDING_AND_SITE_RECONSTRUCTION; DESIGN_DIMENSIONS_AND_REALITY_TRACED_SITE; NOT_SURVEY_CERTIFIED'
S['site']={'survey_plot_outline':outline,'area_m2':plot.area,'source_ground_datum':S['coordinate']['origin'][2],'ground_sample_count':len(q),'ccm_native_file':r'E:\jz\JIA\JIA.ccm','ccm_role':'Native project index; geometry taken from its linked Production_OBJ (2) and Production_1QK scene','trace_image':'CCM_Orthographic_Local.png; 52m extent, local aligned axes','grid_step_m':'0.9 courtyard / 1 roads / 2 context','known_limitations':'Context low envelope can contain vegetation remnants. Inside covered buildings ground is inferred. Property legal dimensions absent from D01.'}
S['definitions']={k:v for k,v in D.items() if any(e.get('definition')==k for e in S['elements'])}
(OUT/'05_Intermediate/Architecture_Scene.json').write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'09_Report/Element_Register.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Element','Layer','Family','Source','Confidence']);w.writerows([[e[k] for k in ['name','layer','family','source','confidence']] for e in S['elements']])
print('V2',len(S['elements']),'elements',len(S['definitions']),'definitions','site area',round(plot.area,1));print(collections.Counter(e['layer'] for e in S['elements']))
