import sys,json,math,copy,ast
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,shapely,manifold3d as mf,export_v5 as ex
from shapely.geometry import Polygon,box as shapebox
O=W/'v14';S=json.loads(Path(r'E:\jz\JIA\Rebuild_V13\08_Editable_Source\Architecture_Scene_V13.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:copy.deepcopy(e) for e in S['elements']};replace=[];add=[];remove=[]
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']],type_ignores=[]),'<solid_helpers>','exec'))
def part(g,m):return {'geometry':g,'material':m}
def box(x,y,z,w,d,h,m='M_Wall_Interior'):return part({'type':'box','origin':[x,y,z],'size':[w,d,h]},m)
def put(n,parts,**meta):
 e=E.get(n,{'name':n,'layer':'60_SITE','family':'SITE_MODEL','confidence':'MEDIUM'});e['parts']=parts;e.pop('definition',None);e.update(meta);e['source']='User 2026-10-12 photos; DJI_0508; MP4 0..64s';e['dimension_status']='Photo-fit; hidden joints and field dimensions unmeasured';(replace if n in E else add).append(e);E[n]=e;return e
def polys(g):return [g] if g.geom_type=='Polygon' else [q for q in getattr(g,'geoms',[]) if q.geom_type=='Polygon']
# Correct the terrace exit to the floor-supported hall, outside the staircase void.
# The latest photos show a room wall on one side and an open stairwell on the other.
e=E['PARTITIONS_JOINED_F3'];parts=[]
old_open=shapebox(3.79,7.55,4.01,8.45);new_open=shapebox(3.79,6.30,4.01,7.20);old_front=shapebox(4.10,7.19,8.91,7.41)
for p in e['parts']:
 g=p['geometry'];poly=Polygon(g['outer'],g['holes']);poly=poly.difference(old_front)
 if g['z']<9.6:poly=poly.difference(new_open)
 for q in polys(poly):
  if q.area>1e-10:parts.append(part({'type':'prism_holes','outer':list(q.exterior.coords)[:-1],'holes':[list(r.coords)[:-1] for r in q.interiors],'z':g['z'],'height':g['height']},p['material']))
# Close the old suspended exit opening and form the hall's room-side wall.
parts.append(box(3.8,7.55,7.5,.2,.9,2.1))
parts.extend([box(4.10,6.10,7.5,3.90,.20,2.1),box(8.90,6.10,7.5,.10,.20,2.1),box(4.10,6.10,9.6,4.90,.20,.75)])
put('PARTITIONS_JOINED_F3',parts,layer='11_WALL_INT',family='ARCH_MODEL',v14_circulation='Clear 1.0 m passage along y6.30..7.30; floor remains outside existing stair void')
for name,dy in [('DOOR_LAUNDRY_F3__FRAME',-1.25),('DOOR_LAUNDRY_F3__LEAF',-1.25),('DOOR_STUDY_F3__FRAME',-1.2),('DOOR_STUDY_F3__LEAF',-1.2)]:
 e=E[name];e['origin'][1]+=dy
 for key in ['pivot_world_m','hinge_origin_local_m']:
  if key in e:e[key][1]+=dy
 e.update(source='User 002238/002257 real F3 hall photos and 002422 correction',v14_route='F3 room door > supported hall > terrace exit; no door above stair void');replace.append(e)
rail=[]
for x in np.arange(4.14,7.82,.18):rail.append(box(float(x),7.305,7.5,.035,.035,.91,'M_Wood_Red'))
rail.extend([box(4.10,7.295,8.39,3.73,.055,.065,'M_Wood_Red'),box(4.10,7.295,7.49,.075,.075,1.11,'M_Wood_Red'),box(7.77,7.295,7.49,.075,.075,1.11,'M_Wood_Red')])
put('STAIR_V14_F3_HALL_OPEN_EDGE_GUARD',rail,layer='41_RAILING',family='ARCH_MODEL',classification='F3_PHOTO_HALL_BESIDE_STAIRWELL')
# Kitchen main room is retained. Replace the old isolated annex by a connected inner store.
for n in list(E):
 if n.startswith('SITE_SOUTH_EAST_ANNEX_') or n=='ANNEX_EXPOSED_GREY_BRICK_UNITS':remove.append(n)
# The connecting floor meets the retained main kitchen floor at x13.35 without a gap.
put('SITE_V14_INNER_STORAGE_FLOOR',[box(13.35,-16.2,-.52,5.55,6.5,.12,'M_Stone')],classification='INNER_STORAGE_CONNECTED_BLOCK')
walls=[]
# North wall, front wooden entry, east gable with an open portal to outer storage.
walls.extend([box(13.35,-9.95,-.4,5.55,.25,3.30,'M_Brick_Grey'),box(13.35,-16.20,-.4,2.40,.25,3.3,'M_Brick_Grey'),box(16.95,-16.20,-.4,1.95,.25,3.3,'M_Brick_Grey'),box(15.75,-16.20,1.70,1.2,.25,1.2,'M_Brick_Grey')])
walls.extend([box(18.65,-16.2,-.4,.25,2.75,3.3,'M_Brick_Grey'),box(18.65,-12.15,-.4,.25,2.45,3.3,'M_Brick_Grey'),box(18.65,-13.45,1.80,.25,1.30,1.10,'M_Brick_Grey')])
profile=[[18.65,-16.2,2.9],[18.65,-9.7,2.9],[18.65,-12.95,4.35]]
walls.append(part({'type':'prism','profile':profile,'vector':[.25,0,0]},'M_Brick_Grey'))
# Main-to-inner store doorway is within the shared wall, matching the linked blocks.
walls.extend([box(13.35,-16.2,-.4,.25,4.70,3.30,'M_Brick_Grey'),box(13.35,-11.5,1.75,.25,1.25,1.15,'M_Brick_Grey'),box(13.35,-10.25,-.4,.25,.55,3.30,'M_Brick_Grey')])
put('SITE_V14_INNER_STORAGE_MASONRY',walls,classification='CONNECTED_INNER_STORAGE_GABLE_AND_OPEN_PORTALS')
# Cut only the photographed shared portal through retained main kitchen masonry and finish.
cutter=manifold({'type':'box','origin':[13.1,-11.5,-.41],'size':[.75,1.25,2.16]})
for n in ['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES','SITE_KITCHEN_V11_VISIBLE_BARE_GRAY_BRICK_UNITS','SITE_KITCHEN_V11_VISIBLE_GRAY_MORTAR_BACKING']:
 changed=False;parts=[]
 for p in E[n]['parts']:
  v,_=ex.world_part(p,E[n]);hit=np.all(v.max(0)>[13.1,-11.5,-.41]) and np.all(v.min(0)<[13.85,-10.25,1.75])
  if not hit:parts.append(p);continue
  m=manifold(p['geometry']);r=m-cutter
  if abs(m.volume()-r.volume())>1e-10:
   changed=True
   if not r.is_empty():parts.append(part(fromman(r),p['material']))
  else:parts.append(p)
 if changed:put(n,parts,v14_shared_portal=[[13.35,-11.5,-.4],[13.6,-10.25,1.75]])
def beam(a,b,w,d,m='M_Wood_Honey'):
 a=np.array(a,float);b=np.array(b,float);u=(b-a)/np.linalg.norm(b-a);v=np.cross(u,[0,0,1])
 if np.linalg.norm(v)<1e-8:v=np.array([1,0,0.])
 v/=np.linalg.norm(v);n=np.cross(u,v);q=np.array([a-v*w/2-n*d/2,a+v*w/2-n*d/2,a+v*w/2+n*d/2,a-v*w/2+n*d/2]);return part({'type':'prism','profile':q.tolist(),'vector':(b-a).tolist()},m)
def timber_round(x,y,z,length,r):
 q=[[x,y+r*math.cos(t),z+r*math.sin(t)] for t in np.linspace(0,2*math.pi,16,endpoint=False)]
 return part({'type':'prism','profile':q,'vector':[length,0,0]},'M_Wood_Honey')
roof=[]
for y in [-16.45,-9.45]:
 q=[[13.30,y,2.83],[19.12,y,2.83],[19.12,-12.95,4.35],[13.30,-12.95,4.35]];roof.append(part({'type':'prism','profile':q,'vector':[0,0,.10]},'M_Roof'))
put('SITE_V14_INNER_STORAGE_GABLE_ROOF',roof,classification='INNER_STORE_TILE_GABLE_TRANSVERSE_RIDGE')
def tile(a,b,r=.055,th=.005):
 a=np.array(a,float);b=np.array(b,float);u=(b-a)/np.linalg.norm(b-a);v=np.array([1.,0,0]);n=np.cross(u,v)
 if n[2]<0:n=-n
 angles=np.linspace(0,math.pi,9);q=[a+v*(r*math.cos(t))+n*(r*.75*math.sin(t)) for t in angles];q +=[a+v*((r-th)*math.cos(t))+n*((r*.75-th)*math.sin(t)) for t in angles[::-1]]
 return part({'type':'prism','profile':np.array(q).tolist(),'vector':(b-a).tolist()},'M_Roof')
tiles=[]
for x in np.arange(13.4,19.08,.18):
 for side in [-1,1]:
  for s in np.arange(.02,3.46,.29):
   t=min(s+.315,3.50);a=[float(x),-12.95+side*s,4.457-s*1.52/3.50];b=[float(x),-12.95+side*t,4.457-t*1.52/3.50];tiles.append(tile(a,b))
put('SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES',tiles)
timber=[]
for x in [13.6,15.8,18.5]:
 timber.append(beam([x,-15.98,2.71],[x,-9.92,2.71],.18,.23));timber.append(beam([x,-15.98,2.71],[x,-12.95,4.14],.12,.16));timber.append(beam([x,-9.92,2.71],[x,-12.95,4.14],.12,.16));timber.append(beam([x,-12.95,2.71],[x,-12.95,4.14],.14,.14))
for y in [-15.90,-14.5,-12.95,-11.4,-10.0]:
 z=4.35-abs(y+12.95)*1.52/3.50-.13;timber.append(timber_round(13.35,y,z,5.55,.09))
for x in np.arange(13.4,18.95,.24):
 for side in [-1,1]:timber.append(beam([float(x),-12.95,4.24],[float(x),-12.95+side*3.45,2.74],.045,.06))
put('SITE_V14_INNER_STORAGE_TIMBER_ROOF_FRAME',timber,classification='INNER_STORE_EXPOSED_TIMBER_SUPPORTED_ROOF')
sheathing=[]
for y in [-16.45,-9.45]:
 q=[[13.30,y,2.755],[19.12,y,2.755],[19.12,-12.95,4.275],[13.30,-12.95,4.275]];sheathing.append(part({'type':'prism','profile':q,'vector':[0,0,.075]},'M_V12_Kitchen_HONEY_WOOD'))
put('SITE_V14_INNER_STORAGE_ROOF_WOOD_SHEATHING',sheathing,classification='WOOD_RAFTER_TO_TILE_ROOF_CONTINUOUS_BACKING')
put('SITE_V14_INNER_STORAGE_FRONT_DOOR',[box(15.75,-16.19,-.4,1.2,.055,2.1,'M_Wood_Red')],classification='INNER_STORE_FRONT_ENTRY')
# Exterior semi-octagonal storage: one metal lean-to roof and an open balustrade.
poly=[[18.9,-16.2],[20.2,-16.2],[21.30,-15.4],[21.45,-13.0],[20.95,-10.35],[18.9,-9.70]]
put('SITE_V14_OUTER_STORAGE_FLOOR',[part({'type':'prism_holes','outer':poly,'holes':[],'z':-.55,'height':.15},'M_Stone')],classification='EXTERNAL_STORAGE_HALF_OPEN_PROJECTING_BLOCK')
def zroof(x):return 2.74-(x-18.9)*.16
put('SITE_V14_OUTER_STORAGE_METAL_ROOF',[part({'type':'prism','profile':[[x,y,zroof(x)] for x,y in poly],'vector':[0,0,.055]},'M_Metal_Black')],classification='OUTER_STORAGE_METAL_LEAN_TO_NOT_CERAMIC_TILE')
supports=[];balustrade=[];stone=[];sheet_ribs=[]
for x,y in poly[1:-1]:supports.append(box(x-.035,y-.035,-.4,.07,.07,zroof(x)+.01+.4,'M_Metal_Black'))
for aa,bb in zip(poly[:-1],poly[1:]):
 a=np.array(aa,float);b=np.array(bb,float);L=np.linalg.norm(b-a);d=(b-a)/L
 supports.append(beam([*a,zroof(a[0])-.025],[*b,zroof(b[0])-.025],.075,.085,'M_Metal_Black'))
 balustrade.append(beam([*a,.48],[*b,.48],.14,.12,'M_Stone'))
 balustrade.append(beam([*a,-.18],[*b,-.18],.10,.11,'M_Stone'))
 for s in np.arange(0,L+.001,.80):
  q=a+d*min(s,L);balustrade.append(box(q[0]-.07,q[1]-.07,-.4,.14,.14,1.02,'M_Stone'))
 for s in np.arange(.10,L,.45):
  q=a+d*s;balustrade.append(beam([q[0],q[1],-.18],[q[0],q[1],.45],.065,.065,'M_Stone'))
 # Visible supporting stone plinth, photo-referenced exterior retaining face.
 stone.append(beam([*a,-1.15],[*b,-1.15],.28,1.50,'M_Stone'))
supports.append(beam([18.78,-16.2,2.715],[18.78,-9.7,2.715],.24,.09,'M_Metal_Black'))
for y in np.arange(-16.05,-9.90,.50):
 cross=Polygon(poly).intersection(shapely.LineString([[18.7,float(y)],[21.7,float(y)]]))
 if cross.is_empty:continue
 x1,x2=cross.bounds[0],cross.bounds[2];supports.append(beam([x1,float(y),zroof(x1)-.025],[x2,float(y),zroof(x2)-.025],.045,.06,'M_Metal_Black'))
for y in np.arange(-16.05,-9.85,.15):
 cross=Polygon(poly).intersection(shapely.LineString([[18.7,float(y)],[21.7,float(y)]]))
 if cross.is_empty:continue
 x1,x2=cross.bounds[0],cross.bounds[2];sheet_ribs.append(beam([x1,float(y),zroof(x1)+.06],[x2,float(y),zroof(x2)+.06],.022,.015,'M_Metal_Black'))
put('SITE_V14_OUTER_STORAGE_STEEL_BEARING_FRAME',supports)
put('SITE_V14_OUTER_STORAGE_STONE_BALUSTRADE',balustrade)
put('SITE_V14_OUTER_STORAGE_VISIBLE_STONE_PLINTH',stone,dimension_status='Visible plinth height fitted to retained stone base; not buried foundation design')
put('SITE_V14_OUTER_STORAGE_METAL_SEAMS',sheet_ribs)
for e in replace+add:
 for p in e['parts']:p['material']={'M_Wood_Red':'MAT_DOOR_FRAME_RED','M_Wood_Honey':'M_V12_Kitchen_HONEY_WOOD','M_Brick_Grey':'M_Grey_Brick'}.get(p['material'],p['material'])
qa={'replace':replace,'add':add,'remove':remove,'circulation':{'route_local_xy':[[8.45,6.8],[7.8,6.8],[5.2,6.8],[3.9,6.8],[3.3,6.8]],'clear_width_m':1.0,'stair_geometry_unchanged':True,'exit_original_y':7.55,'exit_revised_y':6.30},'storage':{'main_kitchen_retained':True,'inner_store_bounds':[[13.35,-16.2],[18.9,-9.7]],'outer_store_polygon':poly,'main_to_inner_portal_y':[-11.5,-10.25],'inner_to_outer_portal_y':[-13.45,-12.15],'evidence_mp4_seconds':[0,4,10,12,16,18,22,24,34,36,40,44,54,60],'concealed_structure':'not field measured; fitted visible assembly only'}}
(O/'Building_Mutation.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8');print('DONE',len(replace),len(add),len(remove),flush=True)
