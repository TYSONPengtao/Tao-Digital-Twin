import sys,json,math,ast,copy
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,shapely,export_v5 as ex,manifold3d as mf
from shapely.geometry import Polygon,box as sb
O=W/'v14';S=json.loads(Path(r'E:/jz/JIA/Rebuild_V13/08_Editable_Source/Architecture_Scene_V13.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']};Q=json.loads((O/'Building_Mutation.json').read_text(encoding='utf8'));E.update({e['name']:e for e in Q['replace']+Q['add']})
tree=ast.parse((W/'v14_building.py').read_text(encoding='utf8'));scope=ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['part','box','polys','beam','tile','timber_round']],type_ignores=[]);exec(compile(scope,'helpers','exec'))
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']],type_ignores=[]),'solid','exec'))
changed={};added={}
def put(n,ps,**meta):
 e=copy.deepcopy(E.get(n,{'name':n,'layer':'60_SITE','family':'SITE_MODEL','confidence':'PHOTO_FIT'}));e['parts']=ps;e.update(meta);e['source']='DJI_0525.JPG / DJI_0526.JPG and registered actual OBJ roof planes';e['dimension_status']='Photo and registered mesh fitted; field dimensions unmeasured'
 for p in ps:p['material']={'M_Wood_Honey':'M_V12_Kitchen_HONEY_WOOD','M_Wood_Red':'MAT_DOOR_FRAME_RED','M_Brick_Grey':'M_Grey_Brick'}.get(p['material'],p['material'])
 (changed if n in E else added)[n]=e;E[n]=e
# Fit perpendicular tile roofs to the registered actual roof. Align their ridge
# intersection to the retained native main-roof plane, rather than overlaying slabs.
cm=np.array([-.440834917,.00312578606,9.36247826]);cn=np.array([-.02932971,-.44280862,-.52731456]);cs=np.array([.01557364,.42152804,9.19952894]);xr=11.515
def h(c,x,y):return float(c[0]*x+c[1]*y+c[2])
def ry(x):return float(-(cn[0]-cs[0])*x/(cn[1]-cs[1])-(cn[2]-cs[2])/(cn[1]-cs[1]))
yj=ry(xr);delta=h(cm,xr,yj)-h(cn,xr,yj);cn[2]+=delta;cs[2]+=delta
def vx(y,c):return float(-((cm[1]-c[1])*y+(cm[2]-c[2]))/(cm[0]-c[0]))
yn=-9.45;ye=float(-((cm[0]-cn[0])*13.6+(cm[2]-cn[2]))/(cm[1]-cn[1]));start=[xr,yj,h(cm,xr,yj)];end=[13.6,ye,h(cm,13.6,ye)]
# Registered silhouette: a broad L valley on the north slope, and a short return
# beside the main gable on the south slope. Separate the two eave lines.
npoly=Polygon([[xr,yj],[19.12,ry(19.12)],[19.12,yn],[vx(yn,cn),yn]])
spoly=Polygon([[xr,yj],[19.12,ry(19.12)],[19.12,-16.45],[13.30,-16.45],[13.30,-12.05],[vx(-12.05,cs),-12.05]])
plan=npoly.union(spoly).buffer(0);mask=plan.intersection(sb(11.45,-12.05,13.61,-2.15))
def cutter(poly,z=-2,height=10):return manifold({'type':'prism_holes','outer':list(poly.exterior.coords)[:-1],'holes':[],'z':z,'height':height})
cut=cutter(mask);tc=cutter(mask.buffer(.055));trim=[]
for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF','SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0','SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_1']:
 ps=[];count=0
 for p in E[n]['parts']:
  v,_=ex.world_part(p,E[n]);xy=Polygon(v[:,:2]).convex_hull
  if not mask.buffer(.06).intersects(xy):ps.append(p);continue
  m=manifold(p['geometry']);r=m-(cut if n.endswith('ROOF') else tc)
  if abs(m.volume()-r.volume())>1e-9:
   count+=1
   if not r.is_empty():ps.append(part(fromman(r),p['material']))
  else:ps.append(p)
 put(n,ps,v14_junction='Intersecting L roof with diagonal valley; overlapping tile portions cut back');trim.append({'node':n,'trimmed_parts':count})
roof=[];wood=[]
for poly,c in [(npoly,cn),(spoly,cs)]:
 q=[[x,y,h(c,x,y)-.055] for x,y in list(poly.exterior.coords)[:-1]];roof.append(part({'type':'prism','profile':q,'vector':[0,0,.055]},'M_Roof'))
 q=[[x,y,h(c,x,y)-.085] for x,y in list(poly.exterior.coords)[:-1]];wood.append(part({'type':'prism','profile':q,'vector':[0,0,.030]},'M_V12_Kitchen_HONEY_WOOD'))
put('SITE_V14_INNER_STORAGE_GABLE_ROOF',roof,classification='TRANSVERSE_GABLE_L_ROOF_CUT_AT_ACTUAL_VALLEY')
put('SITE_V14_INNER_STORAGE_ROOF_WOOD_SHEATHING',wood)
tiles=[];tile_clips=0
for x in np.arange(xr+.05,19.09,.18):
 for side,poly,c,yend in [(1,npoly,cn,yn),(-1,spoly,cs,-16.45)]:
  y0=ry(x);dist=abs(yend-y0)
  for s in np.arange(.01,dist,.285):
   a=[float(x),y0+side*s,h(c,x,y0+side*s)-.003];b=[float(x),y0+side*min(s+.31,dist),h(c,x,y0+side*min(s+.31,dist))-.003];p=tile(a,b);v,_=ex.world_part(p,{'parts':[]});fp=Polygon(v[:,:2]).convex_hull
   if poly.covers(fp):tiles.append(p);continue
   if poly.intersects(fp):
    r=manifold(p['geometry'])^cutter(poly)
    if not r.is_empty() and r.volume()>1e-9:tiles.append(part(fromman(r),'M_Roof'));tile_clips+=1
put('SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES',tiles,classification='CURVED_COVER_TILES_TRIMMED_TO_L_ROOF_VALLEY')
# Keep the visible drainage junction narrow; backing continues below the cut tiles.
valley=[beam(np.array(start)+[0,0,.006],np.array(end)+[0,0,.006],.15,.012,'M_Roof')]
put('SITE_V14_KITCHEN_STORAGE_DIAGONAL_VALLEY',valley,classification='VISIBLE_DIAGONAL_WATERCOURSE_AT_TWO_TILE_ROOFS')
# Ridge caps start at the photographed inner-store gable, not at the valley's top.
ridge=[]
for x in np.arange(13.35,19.05,.29):
 b=min(x+.315,19.15);ridge.append(beam([float(x),ry(x),h(cn,x,ry(x))+.072],[float(b),ry(b),h(cn,b,ry(b))+.072],.14,.10,'M_Roof'))
put('SITE_V14_INNER_STORAGE_RIDGE_CAPS',ridge)
# Follow the real roof with masonry gables, so the former constant-height walls
# neither protrude through the roof nor stop below unsupported beams.
def wall_profile(x,ya,yb):return [[x,ya,-.4],[x,yb,-.4],[x,yb,h(cn,x,yb)-.28],[x,ry(x),h(cn,x,ry(x))-.28],[x,ya,h(cs,x,ya)-.28]]
walls=[]
for x in [13.35,18.65]:
 p={'type':'prism','profile':wall_profile(x,-16.2,-9.7),'vector':[.25,0,0]};m=manifold(p)
 if x<14:cu={'type':'box','origin':[13.1,-11.5,-.41],'size':[.75,1.25,2.16]}
 else:cu={'type':'box','origin':[18.6,-13.45,-.41],'size':[.4,1.30,2.21]}
 walls.append(part(fromman(m-manifold(cu)),'M_Grey_Brick'))
for y,c in [(-16.2,cs),(-9.95,cn)]:
 q=[[13.35,y,-.4],[18.9,y,-.4],[18.9,y,h(c,18.9,y)-.28],[13.35,y,h(c,13.35,y)-.28]];m=manifold({'type':'prism','profile':q,'vector':[0,.25,0]})
 walls.append(part(fromman(m),'M_Grey_Brick'))
put('SITE_V14_INNER_STORAGE_MASONRY',walls,classification='ROOF_FOLLOWING_MASONRY_WITH_LINKED_INTERIOR_AND_OUTER_PORTALS')
timber=[]
for x in [13.5,15.8,18.75]:
 y0=ry(x);ys=-16.05;yn2=-9.85;za=h(cs,x,ys)-.205;zb=h(cn,x,yn2)-.205;zp=h(cn,x,y0)-.205;tie=min(za,zb)-.20
 timber.extend([beam([x,ys,za],[x,y0,zp],.18,.15),beam([x,yn2,zb],[x,y0,zp],.18,.15),beam([x,ys,tie],[x,yn2,tie],.18,.22),beam([x,y0,tie],[x,y0,zp],.14,.14)])
 # Wall/roof bearing spacers under the primary beams at both ends.
 for y,z in [(ys,za),(yn2,zb)]:timber.append(box(x-.10,y-.10,h(cs if y<y0 else cn,x,y)-.29,.20,.20,.14,'M_V12_Kitchen_HONEY_WOOD'))
for d in [-3.90,-2.50,-1.10,0,1.10,2.10]:
 a=[13.35,ry(13.35)+d,h(cs if d<0 else cn,13.35,ry(13.35)+d)-.205];b=[18.90,ry(18.90)+d,h(cs if d<0 else cn,18.90,ry(18.90)+d)-.205];timber.append(beam(a,b,.14,.14))
for x in np.arange(13.4,18.97,.24):
 for y,c in [(-16.4,cs),(-9.5,cn)]:timber.append(beam([float(x),ry(x),h(c,x,ry(x))-.110],[float(x),y,h(c,x,y)-.110],.045,.06))
# Valley bearer bears on the original kitchen frame and the adjoining store wall.
boundarybody=cutter(plan)
clipped_timber=[]
for p in timber:
 v,_,_,_=ex.solid_data(p['geometry']);fp=Polygon(np.asarray(v)[:,:2]).convex_hull
 if plan.covers(fp):clipped_timber.append(p)
 elif plan.intersects(fp):
  r=manifold(p['geometry'])^boundarybody
  if not r.is_empty() and r.volume()>1e-9:clipped_timber.append(part(fromman(r),p['material']))
timber=clipped_timber
timber.append(beam(np.array(start)-[0,0,.20],np.array(end)-[0,0,.20],.18,.18))
timber.append(beam(np.array(start)-[0,0,.105],np.array(end)-[0,0,.105],.18,.075))
put('SITE_V14_INNER_STORAGE_TIMBER_ROOF_FRAME',timber,classification='PURLINS_RAFTERS_TRUSSES_AND_VALLEY_BEARER')
# Actual metal-roof plane is near z2.0 m in local coordinates. Move its roof,
# seams and upper steel members together, keeping all column feet on the floor.
oldz=lambda x:2.74-(x-18.9)*.16
newz=lambda x,y:2.58988663-.0292431454*x-.00117201994*y
for name in ['SITE_V14_OUTER_STORAGE_METAL_ROOF','SITE_V14_OUTER_STORAGE_METAL_SEAMS','SITE_V14_OUTER_STORAGE_STEEL_BEARING_FRAME']:
 ps=[]
 for p in E[name]['parts']:
  v,f,_,_=ex.solid_data(p['geometry']);v=np.array(v,float);q=v.copy();keep=v[:,2]>1.0
  q[keep,2]+=np.array([newz(x,y)-oldz(x) for x,y in v[keep,:2]])
  ps.append(part({'type':'polyhedron','vertices':q.tolist(),'faces':[list(a) for a in f]},p['material']))
 put(name,ps,classification='OUTER_METAL_ROOF_FITTED_TO_ORIGINAL_SURVEY_UNDER_TILE_EAVE')
Q['replace']=[changed.pop(e['name'],e) for e in Q['replace']];Q['add']=[changed.pop(e['name'],e) for e in Q['add']];Q['replace']+=list(changed.values());Q['add']+=list(added.values());Q['add']=[e for e in Q['add'] if e['name']!='SITE_V14_INNER_STORAGE_FRONT_DOOR'];Q['roof_junction']={'references':['DJI_0525.JPG','DJI_0526.JPG'],'main_top_plane':cm.tolist(),'inner_north_top_plane':cn.tolist(),'inner_south_top_plane':cs.tolist(),'registered_plane_vertical_fit_m':delta,'valley_start':start,'valley_end':end,'inner_ridge_y_at_x13_35':ry(13.35),'trim':trim,'inner_edge_tile_clips':tile_clips,'metal_roof_plane':[-.0292431454,-.00117201994,2.58988663],'measurement_status':'Photo/registered source fitted; not measured construction drawing'}
(O/'Building_Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');(O/'Roof_Junction_QA.json').write_text(json.dumps(Q['roof_junction'],indent=2),encoding='utf8');print('DONE ROOF',Q['roof_junction'],flush=True)
