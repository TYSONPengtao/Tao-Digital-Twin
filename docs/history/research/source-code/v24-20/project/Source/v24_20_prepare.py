"""Repair the photo-referenced walls, posts, floor and obsolete drains."""
from v24_20_common import *
from shapely.geometry import LineString,MultiPoint,box
from shapely.ops import unary_union

# Restore the exact original lower portions of the four load-bearing posts.
n='SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry'
oldi=next(r for r in json.loads((W/'v24_17/Inventory.json').read_text())if r['name']==n)
old=np.load(W/'v24_17'/oldi['file']);lower=solid(old['v'],old['f'])^cube([7,-11.68,-.42],[15,-2.88,1.8002])
fixed=union([load(n),lower]);from v24_20_posts import deform_frames,deform_roof_timber,YS,NEWX
storage_timber_exclusion=cube([13.23,-12.5,2.24],[15,-9.08,6])
fixed=deform_frames(fixed)-storage_timber_exclusion;put(n,fixed,'M_Timber_Honey',transfer=True)
OUT['objects'][-1]['transfer_file']=str(W/'v24_17'/oldi['file'])
OUT['objects'][-1]['frame_base_material_by_z']=True
for n in ['SITE_KITCHEN_V12_LONGITUDINAL_ROUND_PURLINS_Geometry','SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS_Geometry']:put(n,deform_roof_timber(n)-storage_timber_exclusion,'M_Timber_Honey',transfer=True)
OUT['proof']['kitchen_posts']={'cause':'V24.17 shared timber clipping box had a Z minimum of 1.8m, clipping load-bearing posts with roof trim.','restoration':'Restore post lower portions and bases, then refit east post axes to the inner outer-wall trace in photo 002312; keep column cross sections, floor feet and roof support connections.','axes_xy':[[float(x),float(y)]for x,y in zip(NEWX,YS)],'old_axes_x':13.060106,'nominal_column_centre_wall_offset_m':.125,'reference':'屏幕截图 2026-10-19 002312.jpg','original_stone_base_bottom_z':-.4,'original_wood_bottom_z':-.2,'whole_building_moved':False}

# Floor is fitted under the inner face of the curved eastern masonry.
n='SITE_KITCHEN_STONE_FLOOR_Geometry';floor=load(n)
infill=[(13.36,-8.55),(13.36,-8.25),(14.017,-3.02),(14.045,-2.60),(13.36,-2.60)]
patch=section(infill,.169922).translate([0,0,-.569946]);fixed=union([floor,patch]);put(n,fixed,'M_Concrete',transfer=True)
OUT['objects'][-1]['floor_infill']=True
OUT['proof']['kitchen_floor']={'cause':'The rectangular floor stopped at X=13.4218m; the inside of the bent wall continues east to about X=14.0m.','top_z':-.400024,'bottom_z':-.569946,'added_volume_m3':fixed.volume()-floor.volume(),'footprint_infill':infill,'continuous_solid':True}
# Remove the 20mm foundation lip only where the actual kitchen floor covers it.
# Exterior retaining faces and all subfloor foundation material stay in place.
floor_footprint=fixed.slice(-.45);lipcut=floor_footprint.extrude(1).translate([0,0,-.40010])
n='SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry';toe=load(n);trimmed=toe-lipcut;put(n,trimmed,INDEX[n]['materials'][0],transfer=True)
OUT['proof']['kitchen_floor'].update(interior_foundation_lip_lowered_to_z=-.40010,lip_removed_volume_m3=float(toe.volume()-trimmed.volume()),exterior_and_below_floor_foundation_retained=True)
OUT['material_edits'].extend([{'name':n,'kind':'kitchen_inner_white'}for n in ['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','V24_04_Kitchen_Perimeter_Upper_Return','V24_04_Kitchen_Perimeter_Upper_Return_Stone_Toe']if n in INDEX])
OUT['material_edits'].append({'name':'SITE_V18_CONTINUOUS_STORAGE_STONE_BASE_Geometry','kind':'kitchen_floor_toe'})

# Drain downpipes, gutters, brackets and receiver are removed by function/name.
remove=[n for n in INDEX if any(k in n for k in ['CONSTRUCTION_ROOF_DN100_','CONSTRUCTION_GUTTER_CONNECTOR_','CONSTRUCTION_MAIN_EAVE_GUTTER_'])]
remove += [n for n in INDEX if n.startswith(('V24_03_Kitchen_Rear_Corner_Downpipe','V24_03_Kitchen_Rear_Drain_Channel','V24_10_Exterior_Downpipe_'))]
remove += [n for n in ['SITE_GAZEBO_V11_METAL_GUTTERS_Geometry','SITE_V22_PAVILION_RAINWATER_DOWNPIPE_Geometry','CONSTRUCTION_COURTYARD_DRAINAGE_RECEIVER_Geometry']if n in INDEX]
OUT['remove']=sorted(set(remove))

def sloping_quad(a,b,oa,ob,lo,hi,za,zb,top,bottom):
 v=[]
 for dz in [bottom,top]:
  v += [[*(np.array(p)+np.array(o)*d),z+dz]for p,o,z,d in [(a,oa,za,lo),(b,ob,zb,lo),(b,ob,zb,hi),(a,oa,za,hi)]]
 f=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
 return solid(v,f)

# Keep the graded road tie; fill its former channel to a continuous ground surface.
segs=json.loads((W/'v16/Drain_Segments.json').read_text());fills=[]
for r in segs:
 if not r['roadzone']:continue
 a=np.array(r['a']);b=np.array(r['b']);oa=(np.array(r['outer_a'])-a)/1.05;ob=(np.array(r['outer_b'])-b)/1.05
 fills.append(sloping_quad(a,b,oa,ob,.179,.431,r['za'],r['zb'],-.020,-.185))
def footprint_mask(n):
 d=source(n);t=d['v'][d['f']];ps=[Polygon(p[:,:2])for p in t if abs(np.cross(p[1]-p[0],p[2]-p[0])[2])>1e-10];shape=unary_union(ps).buffer(.000001);polys=[shape]if shape.geom_type=='Polygon'else list(shape.geoms)
 return union([section(list(p.exterior.coords)[:-1],16).translate([0,0,-8])for p in polys])
n='SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE_Geometry';cutter=cube([12.5,-19.4,-7],[23.4,-8.65,-.65]);filled=union([load(n),(union(fills)-cutter)^footprint_mask(n)]);new='V24_20_Continuous_Graded_Road_Edge_0';put(new,filled,'M_V19_Perimeter_Road_Shoulder',True);OUT['remove'].append(n)
p=json.loads((W/'v24_10/Prepared_Geometry.json').read_text());fills=[]
for r in p['drain_stations']:
 a=np.array(r['a']);b=np.array(r['b']);u=(b-a)/np.linalg.norm(b-a);no=np.array([u[1],-u[0]])
 # Original mitred station offsets are recoverable from adjoining directions.
 route=np.array([p['drain_stations'][0]['a']]+[t['b']for t in p['drain_stations']]);dirs=np.diff(route,axis=0);dirs/=np.linalg.norm(dirs,axis=1)[:,None];ns=np.c_[dirs[:,1],-dirs[:,0]];i=len(fills);oa=ns[0]if i==0 else(ns[i-1]+ns[i])/(1+ns[i-1]@ns[i]);ob=ns[-1]if i==len(ns)-1 else(ns[i]+ns[i+1])/(1+ns[i]@ns[i+1]);fills.append(sloping_quad(a,b,oa,ob,.079,.331,r['grade_a'],r['grade_b'],-.015,-.25))
n='SITE_V20_STORAGE_FRONT_GUTTER_AND_ROAD_SHOULDER_Geometry';put('V24_20_Continuous_Graded_Road_Edge_1',union([load(n),union(fills)^footprint_mask(n)]),'M_V19_Perimeter_Road_Shoulder',True);OUT['remove'].append(n)
# Close the small receiver recess with matching courtyard paving.
n='CONSTRUCTION_COURTYARD_DRAINAGE_FINISH_Geometry';put(n,union([load(n),cube([.215,-11.085,-.96],[.585,-10.715,-.41125])]),'M_V22_Courtyard_Stone_0',transfer=True)
OUT['proof']['drainage']={'removed':OUT['remove'][:],'road_channels_filled':2,'courtyard_paving_retained':True,'smoke_and_exhaust_flues_retained':True}

# Shared source photo finish and a low stone/brick boundary following the wall base.
scene=json.loads(Path('E:/jz/JIA/Rebuild_V23/08_Editable_Source/Architecture_Scene_V23.json').read_text(encoding='utf8'));ee={e['name']:e for e in scene['elements']};bottom=[]
for i in range(2):
 e=ee[f'SITE_PERIMETER_JOINED_RETAINING_WALL_{i}']
 for p in e['parts']:
  if 'Rubble'not in p['material']and 'RUBBLE'not in p['material']:continue
  v=np.array(p['geometry']['vertices']);xy,ii=np.unique(np.round(v[:,:2],7),axis=0,return_inverse=True);zz=np.array([v[ii==j,2].min()for j in range(len(xy))]);centre=xy.mean(0);order=np.argsort(np.arctan2(xy[:,1]-centre[1],xy[:,0]-centre[0]));q=np.c_[xy[order],zz[order]]
  for j in range(1,len(q)-1):bottom.append([q[0].tolist(),q[j].tolist(),q[j+1].tolist()])
assert bottom,'Missing wall base planes'
OUT['wall_base_triangles']=bottom;OUT['wall_boundary_height_m']=.20;OUT['wall_uv_route']=json.loads((W/'v24_18/Prepared_Geometry.json').read_text())['uv_route'];OUT['wall_grade_segments']=segs
for i in range(2):
 name=f'SITE_PERIMETER_JOINED_RETAINING_WALL_{i}_Geometry';e=ee[name.removesuffix('_Geometry')];parts=[]
 for p in e['parts']:
  g=p['geometry'];ff=[]
  for face in g['faces']:
   for j in range(1,len(face)-1):ff.append([face[0],face[j],face[j+1]])
  parts.append(solid(g['vertices'],ff))
 m=union(parts)
 if i==0:m=m^cube([-30,-22,-8],[25,15,3.10])
 put(name,m,'M_V24_20_Continuous_AsBuilt_Perimeter');OUT['objects'][-1]['wall_closed_source_parts']=len(parts)
OUT['proof']['perimeter_finish']={'walls':[f'SITE_PERIMETER_JOINED_RETAINING_WALL_{i}_Geometry'for i in range(2)],'toe':'SITE_V16_CONTINUOUS_WALL_TOE_CLOSURE_Geometry','preferred_material_source':'M_V19_Perimeter_Brick','texture_image':'Perimeter_Actual_Gray_Brick.png','brick_stone_division':'0.20m above the retained road-edge grade, fitted to 225227 red line; applies continuously over the wall foot.','uv':'Shared perimeter arc length and world height; shared photo and shader with a continuous height attribute.','wall_geometry_displaced':False,'topology_repair':'Union the original closed V23 masonry parts; remove internal station/material caps. Do not cut mesh faces at the finish division.'}
corner=[]
for i in range(2):
 d=source(f'SITE_PERIMETER_JOINED_RETAINING_WALL_{i}_TILE_COPING_Geometry');v=d['v'];corner.extend(v[np.linalg.norm(v[:,:2]-[-25.0025,5.6025],axis=1)<.15].tolist())
put('V24_20_Perimeter_Corner_Closed_Ceramic_Mitre',mf.Manifold.hull_points(np.array(corner)).translate([0,0,.003]),'M_V24_20_Unified_Weathered_Gray_Clay',True)

# Roof geometry module uses the same grey barrel/pan tile module across buildings.
import v24_20_roofs
import v24_20_wc
write();print('V20_PREPARED',len(OUT['objects']),len(OUT['remove']),flush=True)
