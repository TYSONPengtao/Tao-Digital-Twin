"""V18 storage exterior, derived from 180115 real photo and INSV 950/972."""
import sys,json,math,copy,ast,hashlib,shutil
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex
from shapely.geometry import Polygon,LineString,Point,box as sbox
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from PIL import Image,ImageEnhance,ImageFilter
B=Path(r'E:/jz/JIA/Rebuild_V17');O=Path(r'E:/jz/JIA/Rebuild_V18');D=W/'v18';D.mkdir(exist_ok=True);T=O/'03_Textures/V18_Storage_AsBuilt';T.mkdir(parents=True,exist_ok=True)
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V17.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
for file,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold','fromman']),('v14_building.py',['part','beam','box'])]:
 tree=ast.parse((W/file).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'<helpers>','exec'))
Q={'replace':[],'add':[],'remove':[]};proof={'reference':'User real photo 180115; INSV 950/972 exterior; DJI_0525/0526 roof registration','dimension_status':'PHOTO_FIT; no independent dimensional survey','materials':[],'geometry':[]}
ref=Path(r'D:/Desktop/问题/屏幕截图 2026-10-12 180115.jpg');im=Image.open(ref).convert('RGB')
def rectified(label,quad,size):
 q=(quad[0][0],quad[0][1],quad[3][0],quad[3][1],quad[2][0],quad[2][1],quad[1][0],quad[1][1])
 a=im.transform(size,Image.Transform.QUAD,q,Image.Resampling.BICUBIC);a.save(T/(label+'.png'))
 proof['materials'].append({'texture':label,'source':str(ref),'source_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'source_quad_TL_TR_BR_BL_pixels':quad,'method':'Planar texture extraction; photograph lighting remains baked in color'})
 return a
# Actual rough stone/mortar proportions are extracted, without inventing new masonry art.
stone=rectified('Photo_Rubble_Stone',[[101,410],[501,445],[514,708],[114,676]],(1024,768))
def periodic_photo(a,label):
 # Periodic/smooth decomposition removes the photographed patch's boundary luminance step.
 # Stone pixels and mortar shapes remain sampled from the source; no new masonry is generated.
 v=np.asarray(a,dtype=float);hh,ww=v.shape[:2];b=np.zeros_like(v);b[0]=v[-1]-v[0];b[-1]=v[0]-v[-1];b[:,0]+=v[:,-1]-v[:,0];b[:,-1]+=v[:,0]-v[:,-1]
 den=2*np.cos(2*np.pi*np.arange(hh)[:,None]/hh)+2*np.cos(2*np.pi*np.arange(ww)[None,:]/ww)-4;den[0,0]=1
 ss=np.fft.fft2(b,axes=(0,1))/den[:,:,None];ss[0,0]=0;v=np.clip(v-np.fft.ifft2(ss,axes=(0,1)).real,0,255);out=Image.fromarray(v.astype(np.uint8));out.save(T/(label+'.png'));proof['materials'].append({'texture':label,'edge_continuity_mean_rgb_255':{'U':float(np.abs(v[:,0]-v[:,-1]).mean()),'V':float(np.abs(v[0]-v[-1]).mean())},'method':'Periodic boundary luminance correction for the real-photo material atlas'});return out
stone=periodic_photo(stone,'Photo_Rubble_Stone');gray=ImageEnhance.Contrast(stone.convert('L')).enhance(.45);gray.save(T/'Photo_Rubble_Microheight.png')
regular=rectified('Photo_Dark_Stone_Courses',[[190,351],[532,369],[532,424],[190,406]],(1536,192));regular=periodic_photo(regular,'Photo_Dark_Stone_Courses');regular.convert('L').filter(ImageFilter.GaussianBlur(1)).save(T/'Photo_Dark_Stone_Microheight.png')
panel=rectified('Photo_Stone_Rail_Panel',[[424,320],[530,323],[529,346],[424,343]],(768,192));panel=ImageEnhance.Contrast(ImageEnhance.Color(panel).enhance(.12)).enhance(.68)
# Atlas: real, shallow carved panel only; the remainder is plain weathered grey stone.
atlas=Image.new('RGB',(1024,512),(147,148,143));atlas.paste(panel.resize((768,384),Image.Resampling.LANCZOS),(32,96));atlas.save(T/'Stone_Guard_Photo_Atlas.png');atlas.convert('L').save(T/'Stone_Guard_Photo_Height.png')
M=json.loads((B/'02_Data/Native_Render_Materials.json').read_text(encoding='utf8'))
oldwood=Image.open(M['M_V12_Kitchen_HONEY_WOOD']['native_bitmap']).convert('RGB');w=np.asarray(oldwood,dtype=float);avg=w.mean((0,1));w=np.clip(w/avg*np.array([65.,47.,32.]),0,255).astype(np.uint8);Image.fromarray(w).save(T/'Aged_Storage_Timber.png');Image.fromarray(np.mean(w,2).astype(np.uint8)).save(T/'Aged_Storage_Timber_Height.png')
rng=np.random.default_rng(18115);noise=rng.normal(0,1,(512,512));soft=np.asarray(Image.fromarray(np.uint8(np.clip(noise*25+128,0,255))).filter(ImageFilter.GaussianBlur(10)),dtype=float)-128
road=np.clip(156+noise*5+soft*1.5,0,255).astype(np.uint8);Image.fromarray(np.stack([road,road,np.clip(road.astype(int)-5,0,255).astype(np.uint8)],2)).save(T/'Road_Shoulder_Microaggregate.png');Image.fromarray(road).save(T/'Road_Shoulder_Height.png')
proof['materials'].append({'texture':'Aged_Storage_Timber','method':'Existing timber grain recolored to the visible weathered brown finish; no change to other timber materials'})
materials={
 'M_V18_Storage_Rubble':{'bitmap':'Photo_Rubble_Stone.png','bump':'Photo_Rubble_Microheight.png','color':[255,255,255],'roughness':.96,'repeat_m':[3.2,2.3],'bump_distance_m':.003},
 'M_V18_Storage_Dark_Courses':{'bitmap':'Photo_Dark_Stone_Courses.png','bump':'Photo_Dark_Stone_Microheight.png','color':[255,255,255],'roughness':.94,'repeat_m':[4.3,.64],'bump_distance_m':.002},
 'M_V18_Storage_Stone_Guard':{'bitmap':'Stone_Guard_Photo_Atlas.png','bump':'Stone_Guard_Photo_Height.png','color':[255,255,255],'roughness':.89,'bump_distance_m':.001},
 'M_V18_Aged_Storage_Timber':{'bitmap':'Aged_Storage_Timber.png','bump':'Aged_Storage_Timber_Height.png','color':[255,255,255],'roughness':.87,'bump_distance_m':.0015},
 'M_V18_Road_Shoulder':{'bitmap':'Road_Shoulder_Microaggregate.png','bump':'Road_Shoulder_Height.png','color':[255,255,255],'roughness':.98,'bump_distance_m':.001},
 'M_V18_Metal_Weathered':{'color':[66,72,69],'roughness':.72,'metallic':.32},
 'M_V18_Exterior_White_Pipe':{'color':[205,206,195],'roughness':.72},
 'M_V18_Storage_Window_Glass':{'color':[53,63,58],'roughness':.32,'transparency':.12},
}
def put(n,parts,new=False,**meta):
 e=copy.deepcopy(E[n]) if not new else {'name':n,'layer':'60_SITE','family':'SITE_MODEL','confidence':'PHOTO_FIT'}
 e.update(parts=parts,source=proof['reference'],dimension_status=proof['dimension_status'],v18_storage_exterior=True,**meta);Q['add' if new else 'replace'].append(e);return e
def unite(parts,mat):
 a=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in parts],mf.OpType.Add);assert not a.is_empty();return part(fromman(a),mat)
def prism(poly,z,h):
 poly=orient(poly,1);return {'type':'prism_holes','outer':list(poly.exterior.coords)[:-1],'holes':[list(q.coords)[:-1] for q in poly.interiors],'z':z,'height':h}
def footprint(n):
 p=E[n]['parts'][0]['geometry'];v,fs,_,_=ex.solid_data(p);t=v[triangles(v,fs)];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);return unary_union([Polygon(q[:,:2]) for q in t[no[:,2]>1e-9]]).buffer(0)
storepoly=Polygon([[13.35,-16.2],[20.2,-16.2],[21.3,-15.4],[21.45,-13],[20.95,-10.35],[18.9,-9.7],[13.35,-9.7]])
outerpoly=Polygon([[18.9,-16.2],[20.2,-16.2],[21.3,-15.4],[21.45,-13],[20.95,-10.35],[18.9,-9.7]])
wallplan=storepoly.union(outerpoly.buffer(.14,join_style=2)).union(sbox(13.35,-16.34,18.91,-15.97)).buffer(0)
# The exterior wall remains on ONE face from the rail to the road, replacing the stepped soil recess.
total=manifold(E['SITE_V17_KITCHEN_STORAGE_CONTINUOUS_STONE_BASE']['parts'][0]['geometry'])+manifold(prism(wallplan,-4.65,4.242))
total=total+manifold(E['SITE_V17_STORAGE_VERANDA_EDGE_BASE']['parts'][0]['geometry'])
lower=total^mf.Manifold.cube([100,100,30]).translate([-40,-40,-31.05]);upper=total-lower
assert len(total.decompose())==1 and (lower^upper).volume()<1e-7
newbase='SITE_V18_CONTINUOUS_STORAGE_STONE_BASE'
put(newbase,[part(fromman(lower),'M_V18_Storage_Rubble'),part(fromman(upper),'M_V18_Storage_Dark_Courses')],True,classification='CONTINUOUS_RUBBLE_RETAINING_PLINTH_WITH_DARK_STONE_TOP_COURSES',v18_band_joint_z=-1.05,v18_top_z=-.408,v18_foot_closure_z=-4.65,v18_exterior_plan=list(wallplan.exterior.coords)[:-1],v18_note='Hidden depth is display closure. Raised toe removed locally. No yellow soil exposed behind outer plinth.')
Q['remove']+=['SITE_V17_KITCHEN_STORAGE_CONTINUOUS_STONE_BASE','SITE_V17_OUTER_STORAGE_PLINTH_CAP_RETURN','SITE_V17_STORAGE_VERANDA_EDGE_BASE']
proof['geometry'].append({'node':newbase,'connected_bodies':len(total.decompose()),'upper_course_height_m':.642,'bottom_closure_z':-4.65,'plan_area_m2':wallplan.area})
# Remove the old ledge at z=-1.84 along the outer storage; seat the toe at the actual retained road grade.
outerchain=[[18.9,-9.7],[20.95,-10.35],[21.45,-13],[21.3,-15.4],[20.2,-16.2],[18.9,-16.2]]
segs=[s for s in json.loads((W/'v16/Drain_Segments.json').read_text(encoding='utf8')) if s['ci']==3];toemask=LineString(outerchain).buffer(.31,join_style=2,cap_style=2)
toe=manifold(E['SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE']['parts'][0]['geometry'])-manifold(prism(toemask,-6,8));patches=[];shoulders=[];toeproof=[]
for s in segs:
 a,b=np.array(s['a']),np.array(s['b']);oa=(np.array(s['outer_a'])-a)/1.05;ob=(np.array(s['outer_b'])-b)/1.05
 vs=[]
 for p,off,z in [(a,oa,s['za']),(b,ob,s['zb'])]:
  vs.extend([[*(p+off*d),z+dz] for d,dz in [(-.14,-.16),(.177,-.16),(.177,-.53),(-.14,-.53)]])
 g={'type':'polyhedron','vertices':vs,'faces':[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]};patches.append(manifold(g))
 shoulders.append(Polygon([a+oa*.431,b+ob*.431,b+ob*1.052,a+oa*1.052]))
 toeproof.append({'start':s['a'],'end':s['b'],'road_za':s['za'],'road_zb':s['zb'],'toe_top_offset_m':-.16})
toe=mf.Manifold.batch_boolean([toe]+patches,mf.OpType.Add);put('SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE',[part(fromman(toe),'M_Stone_Rubble')],v18_local_toe=toeproof,v18_note='Only outer storage toe height corrected to the existing graded road/channel; all other toe geometry retained')
drain=manifold(E['SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE']['parts'][0]['geometry']);shmask=unary_union(shoulders).buffer(0);shoulder=drain^manifold(prism(shmask,-6,8));gutter=drain-shoulder
put('SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE',[part(fromman(gutter),'M_V16_Drain_Concrete'),part(fromman(shoulder),'M_V18_Road_Shoulder')],v18_note='Outer storage road shoulder uses grey fine aggregate; retained 0.25 m gutter and scan cut edge have exactly the same geometry/elevations')
proof['geometry'].append({'toe_local_stations':toeproof,'road_geometry_symmetric_difference_m3':(drain-(gutter+shoulder)).volume()+((gutter+shoulder)-drain).volume()})
# Fewer and wider bays, square caps, and actual broad horizontal pierced openings.
STONE='M_V18_Storage_Stone_Guard';parts=[];bays=[];posts=[]
points=[[13.59,-16.10],[18.9,-16.2],[20.2,-16.2],[21.3,-15.4],[21.45,-13],[20.95,-10.35],[18.9,-9.7]]
for k,(a,b) in enumerate(zip(points[:-1],points[1:])):
 a,b=np.array(a,float),np.array(b,float);d=b-a;L=float(np.linalg.norm(d));d/=L;n=np.array([-d[1],d[0]]);count=3 if k==0 else 1
 for j in range(count):
  p=a+d*L*j/count;q=a+d*L*(j+1)/count;posts+=[p,q];ba=p+d*.058;bb=q-d*.058;clear=float(np.linalg.norm(bb-ba))
  for z,wd,dep in [(-.345,.155,.105),(.51,.145,.105)]:parts.append(beam([*ba,z],[*bb,z],wd,dep,STONE))
  parts.append(beam([*ba,-.03],[*bb,-.03],.077,.52,STONE))
  # A genuine pierced stone band, connected both to the lower panel and the coping.
  band=manifold(beam([*ba,.337],[*bb,.337],.078,.294,STONE)['geometry'])
  for ss in [.27,.73]:
   cen=ba+(bb-ba)*ss;hw=min(.32,clear*.17);zlo=.276;zhi=.431;bevel=.043
   profile=[[*(cen-d*(hw-bevel)-n*.08),zlo],[*(cen+d*(hw-bevel)-n*.08),zlo],[*(cen+d*hw-n*.08),zlo+bevel],[*(cen+d*hw-n*.08),zhi-bevel],[*(cen+d*(hw-bevel)-n*.08),zhi],[*(cen-d*(hw-bevel)-n*.08),zhi],[*(cen-d*hw-n*.08),zhi-bevel],[*(cen-d*hw-n*.08),zlo+bevel]]
   band=band-manifold({'type':'prism','profile':profile,'vector':[*(n*.16),0]})
  parts.append(part(fromman(band),STONE))
  for side in [-1,1]:
   oo=n*side*.043
   for z in [-.253,.194]:parts.append(beam([*(ba+oo),z],[*(bb+oo),z],.018,.020,STONE))
   for s0 in [.04,.96]:
    xy=ba+(bb-ba)*s0+oo;parts.append(beam([*xy,-.25],[*xy,.193],.018,.018,STONE))
  bays.append({'start':p.tolist(),'end':q.tolist(),'panel_start':ba.tolist(),'panel_end':bb.tolist(),'direction':d.tolist(),'normal':n.tolist(),'length_m':L/count,'openings_per_bay':2,'opening_z':[.276,.431]})
for x,y in {tuple(np.round(p,8)) for p in posts}:
 parts.extend([box(x-.099,y-.099,-.410,.198,.198,.112,STONE),box(x-.077,y-.077,-.322,.154,.154,.913,STONE),box(x-.094,y-.094,.57,.188,.188,.070,STONE)])
guard=unite(parts,STONE);a=manifold(guard['geometry']);assert len(a.decompose())==1,len(a.decompose());assert (a^total).volume()>1e-6
put('SITE_V17_CONTINUOUS_STORAGE_STONE_GUARD',[guard],classification='PHOTO_FITTED_WIDE_STONE_PANELS_AND_HORIZONTAL_HEXAGON_PIERCING',v18_bays=bays,v18_guard_top=.64,v18_surface_detail='Real panel photograph in shallow atlas; no invented diamond ornaments')
proof['geometry'].append({'stone_guard_bays':len(bays),'wide_gallery_bays':3,'stone_guard_connected_bodies':len(a.decompose()),'base_overlap_m3':(a^total).volume()})
# Timber assembly and roof bearing geometry remain as fitted; finish is restricted to storage timber.
e=copy.deepcopy(E['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY']);e['parts'][0]['material']='M_V18_Aged_Storage_Timber';put(e['name'],e['parts'],v18_finish='Aged dark brown corresponding to the real recess; all beam/rafter/column joints retained')
e=copy.deepcopy(E['SITE_V17_STORAGE_VERANDA_TIMBER_ENTRY_FRONT'])
for p in e['parts']:p['material']='M_V18_Storage_Window_Glass'
put(e['name'],e['parts'],v18_finish='Restrained dark grey glass as visible under the real eave; aperture and lattice geometry preserved')
# A thin continuous sheet with attached rim/purlins/posts replaces the oversized metal framework.
vg,fg,_,_=ex.solid_data(E['SITE_V14_OUTER_STORAGE_METAL_ROOF']['parts'][0]['geometry']);vg=np.asarray(vg);zsorted=np.argsort(vg[:,2]);# First half is the original profile, upper duplicate is last half.
half=len(vg)//2;top=vg[half:];coef=np.linalg.lstsq(np.c_[top[:,:2],np.ones(len(top))],top[:,2],rcond=None)[0]
def hm(p):return float(np.dot([*p,1],coef))
roofpoly=list(outerpoly.exterior.coords)[:-1];roofpart=part({'type':'prism','profile':[[*p,hm(p)-.025] for p in roofpoly],'vector':[0,0,.025]},'M_V18_Metal_Weathered');metal=[roofpart]
for a0,b0 in zip(outerchain[:-1],outerchain[1:]):metal.append(beam([*a0,hm(a0)-.037],[*b0,hm(b0)-.037],.045,.054,'M_V18_Metal_Weathered'))
metal.append(beam([18.745,-16.23,hm([18.745,-16.23])-.037],[18.745,-9.66,hm([18.745,-9.66])-.037],.055,.054,'M_V18_Metal_Weathered'))
for y in np.arange(-16.06,-9.72,.55):
 intersection=outerpoly.intersection(LineString([[18.73,float(y)],[22,float(y)]]));xy=list(intersection.coords);end=xy[-1];start=[18.725,float(y)];metal.append(beam([*start,hm(start)-.037],[*end,hm(end)-.037],.034,.045,'M_V18_Metal_Weathered'))
for x,y in [[20.2,-16.2],[21.3,-15.4],[21.45,-13],[20.95,-10.35]]:
 metal.append(box(x-.0275,y-.0275,-.404,.055,.055,hm([x,y])+.373,'M_V18_Metal_Weathered'))
for y in np.arange(-16.05,-9.80,.15):
 line=outerpoly.intersection(LineString([[18.895,float(y)],[22,float(y)]]));xy=list(line.coords)
 if len(xy)>1:
  aa,bb=xy[0],xy[-1];metal.append(beam([*aa,hm(aa)+.001],[*bb,hm(bb)+.001],.009,.007,'M_V18_Metal_Weathered'))
metal=unite(metal,'M_V18_Metal_Weathered');ma=manifold(metal['geometry']);assert len(ma.decompose())==1,len(ma.decompose())
put('SITE_V18_OUTER_STORAGE_THIN_METAL_CANOPY',[metal],True,classification='CONTINUOUS_THIN_METAL_SHEET_WITH_SUPPORTED_RIM_AND_POSTS',v18_registered_top_plane=coef.tolist(),v18_sheet_thickness_m=.025,v18_post_size_m=.055,v18_note='Original roof outline and top plane retained. Sheet/frame contacts have positive overlap; lower beams and columns are photo fitted.')
Q['remove']+=['SITE_V14_OUTER_STORAGE_METAL_ROOF','SITE_V14_OUTER_STORAGE_STEEL_BEARING_FRAME','SITE_V14_OUTER_STORAGE_METAL_SEAMS']
proof['geometry'].append({'metal_connected_bodies':len(ma.decompose()),'registered_top_plane':coef.tolist(),'sheet_thickness_m':.025})
# Two exterior white pipe/pole lines visibly documented in the new photograph.
def round_member(a,b,r):
 a,b=np.array(a,float),np.array(b,float);d=(b-a)/np.linalg.norm(b-a);u=np.cross(d,[0,0,1])
 if np.linalg.norm(u)<1e-8:u=np.array([1.,0,0])
 u/=np.linalg.norm(u);v=np.cross(d,u);q=[a+r*(u*math.cos(t)+v*math.sin(t)) for t in np.linspace(0,2*math.pi,16,endpoint=False)];return part({'type':'prism','profile':np.array(q).tolist(),'vector':(b-a).tolist()},'M_V18_Exterior_White_Pipe')
pipes=[round_member([18.54,-16.38,-3.96],[18.54,-16.38,2.37],.024),round_member([20.80,-16.31,-4.03],[21.19,-15.50,2.065],.029)]
put('SITE_V18_PHOTO_EXTERIOR_WHITE_PIPE_LINES',pipes,True,classification='VISIBLE_PHOTO_PIPE_OR_POLE_LINES_FUNCTION_UNCONFIRMED',v18_note='Photo fitted visible lines only. Their service function and exact diameter have not been independently established.')
(D/'Materials.json').write_text(json.dumps(materials,ensure_ascii=False,indent=2),encoding='utf8');(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');(D/'Design_Control.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
print('V18 DESIGN READY',{'replace':[e['name'] for e in Q['replace']],'add':[e['name'] for e in Q['add']],'remove':Q['remove']},flush=True)
