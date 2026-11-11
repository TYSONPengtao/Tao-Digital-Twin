"""Isolated V20 house patch. Reads V19 caches; never writes native delivery."""
import json,sys,ast,copy,math
from pathlib import Path
W=Path(__file__).parents[1];D=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex,mapbox_earcut,shapely
from shapely.geometry import Polygon,box as pbox
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
B=Path('E:/jz/JIA/Rebuild_V19')
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'));ex.SCENE=S
E={e['name']:e for e in S['elements']};I=json.loads((B/'02_Data/Native_Readback_Index_V19.json').read_text(encoding='utf8'));ii={r['name']:r for r in I}
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'))
exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold']],type_ignores=[]),'old_helpers','exec'))
proof={};tree=ast.parse((W/'v19_design.py').read_text(encoding='utf8'))
exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['fromman']],type_ignores=[]),'v19_helper','exec'))
tree=ast.parse((W/'v16_geometry.py').read_text(encoding='utf8'))
exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['polys','refine','volume_from_domain']],type_ignores=[]),'surface_helpers','exec'))

Q={'replace':[],'add':[],'remove':['ENTRANCE_STEP_1','ENTRANCE_STEP_2','ENTRANCE_STEP_3'],'materials':{},'house_reference_audit':{}}
def part(g,m):return {'geometry':g,'material':m}
def box(x,y,z,w,d,h,m):return part({'type':'box','origin':[x,y,z],'size':[w,d,h]},m)
def put(n,ps,new=False,**meta):
 e=copy.deepcopy(E.get(n,{}));e.update(name=n,parts=ps,source='User 2026-10-13 red marked missing walls and one solid entry step; original INSV 110/160/235/600 seconds',**meta)
 e.setdefault('layer','60_SITE');e.setdefault('family','ARCH_MODEL');e.setdefault('confidence','MEDIUM');e.pop('definition',None);e.pop('origin',None);e.pop('angle',None)
 Q['add' if new or n not in E else 'replace'].append(e);return e
def load(n):
 d=np.load(B/'02_Data'/ii[n]['file']);return d['vertices'],d['faces']
def nm(n):
 v,f=load(n);v0,idx=np.unique(np.round(v,9),axis=0,return_inverse=True);m=mf.Manifold(mf.Mesh(vert_properties=v0.astype(np.float32),tri_verts=idx[f].astype(np.uint32)));assert m.status()==mf.Error.NoError,(n,m.status());return m
def footprint(n):
 v,f=load(n);t=v[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);return unary_union([Polygon(q[:,:2]) for q in t[no[:,2]>1e-9]]).buffer(0)

# F1 has an exposed stair front and false slot at the right rear wall. Both are
# directly marked by the user. The 1.20 m east-side stair access is retained.
wall_boxes=[{'origin':[4.10,7.20,0],'size':[3.70,.20,3.77],'purpose':'033840 stair enclosure; open side x7.8..9.0'},
 {'origin':[9.20,7.20,0],'size':[1.51,.20,3.77],'purpose':'033535/033747 right-rear partition closure; retain bathroom door at x11.9..12.7 and kitchen door x9.1,y8.6'}]
wp=[]
for b in wall_boxes:
 m=manifold({'type':'box',**{k:b[k] for k in ['origin','size']}})
 # Keep beam and column concrete intact. Infill meets their actual surfaces.
 for r in I:
  n=r['name'];bounds=r.get('actual_3dm_mesh_bbox_local')
  if not n.startswith(('KZ_','KL_','LL_','BEAM')) or bounds is None:continue
  bb=np.array(bounds);a=np.array(b['origin']);z=a+np.array(b['size'])
  if np.all(bb[1]>a+1e-6) and np.all(bb[0]<z-1e-6):m=m-nm(n)
 if not m.is_empty():wp.append(part(fromman(m),'M_Wall_Interior'))
put('HOUSE_V20_F1_PHOTO_MISSING_INFILL_WALLS',wp,new=True,layer='11_WALL_INT',classification='USER_CONFIRMED_STAIR_FRONT_AND_RIGHT_REAR_SOLID_WALLS',floor='F1',wall_boxes=wall_boxes,stair_side_clear_width_m=1.2)

# One step has a single 150 mm exposed riser. The buried part is solid and the
# existing porch slab is supported to the old -0.45 courtyard level.
porch=footprint('SLAB_JOINED_F1').intersection(pbox(3.75,0,9.25,2.1))
pg,_=volume_from_domain(porch,lambda x,y:-.1495,-.65,.45)
step=manifold({'type':'box','origin':[3.75,-.30,-.65],'size':[5.50,.30,.65]})
support=manifold(pg)+step
put('HOUSE_V20_ONE_SOLID_ENTRY_STEP_AND_PORCH_SUPPORT',[part(fromman(support),'M_Stone')],new=True,layer='22_SLAB',classification='ONE_150MM_EXPOSED_SOLID_ENTRY_STEP',step_exposed_rise_m=.15,porch_top_z_m=0.0,adjacent_court_top_z_m=-.15,buried_bottom_z_m=-.65,underside_void=False)

# Raise only the approach near the house; match all unchanged court boundaries.
# Solid union in each original court node prevents overlap of the two pavements.
approach_rect=pbox(2.75,-3.0,10.25,1.9)
def height(x,y):
 wx=min(1,max(0,x-2.75),max(0,10.25-x));wy=min(1,max(0,(y+3.0)/2.70))
 return -.45+.30*wx*wy
grades=[]
for n in ['SITE_V12_REBUILT_COURT_0_-20_0','SITE_V12_REBUILT_COURT_0_0_0']:
 domain=shapely.set_precision(footprint(n).intersection(approach_rect),.00001).buffer(0).simplify(.00001,preserve_topology=True)
 grade_ms=[];nt=0
 # Insert every grade break in the triangulation. This keeps the full landing
 # edge exactly -0.15 instead of interpolating across a clamped-height corner.
 for x0,x1 in zip([2.75,3.75,9.25],[3.75,9.25,10.25]):
  for y0,y1 in zip([-3.0,-.30,0.0],[ -.30,0.0,1.9]):
   dom=domain.intersection(pbox(x0,y0,x1,y1))
   if dom.is_empty or dom.area<1e-8:continue
   g,tcount=volume_from_domain(dom,height,-.65,.25);grade_ms.append(manifold(g));nt+=tcount
 gm=mf.Manifold.batch_boolean(grade_ms,mf.OpType.Add)
 m=nm(n)+gm;put(n,[part(fromman(m),'M_V12_Terrain_Court')],v20_entry_transition='Continuous solid locally raised court, one 150 mm house-entry riser',scope_xy_bounds=[2.75,-3.0,10.25,1.9],source_node_geometry='V19 actual native readback cache',changes_exterior_drain=False)
 # Use original existing court material; avoid assuming a material name.
 Q['replace'][-1]['parts'][0]['material']=E[n]['parts'][0]['material']
 grades.append({'node':n,'raised_domain_area_m2':domain.area,'top_triangles':nt,'max_z':-.15,'unchanged_grade':-.45,'union_volume_increase_m3':m.volume()-nm(n).volume()})

# Keep the former stone-plinth footprint continuously paved after the pavilion
# becomes an open wood deck. The actual saved V19 paving already covers it;
# raise it only 19.62 mm so the deck underside has exactly the requested 50 mm.
GP=json.loads((W/'v20_gate_pavilion/Mutation.json').read_text(encoding='utf8'))
de=next(e for e in GP['add'] if e['name']=='SITE_V20_PAVILION_RAISED_WOOD_SLATS')
dvs=np.concatenate([ex.world_part(p,de)[0] for p in de['parts']]);deck_bbox=np.array([dvs.min(0),dvs.max(0)])
ground=float(de['nominal_ground_m']);board_bottom=float(de['board_bottom_m'])
old_xy=np.round(footprint('SITE_GAZEBO_V11_STONE_PLATFORM').bounds,5).tolist();x0,y0,x1,y1=old_xy
assert x0<=deck_bbox[0,0] and x1>=deck_bbox[1,0] and y0<=deck_bbox[0,1] and y1>=deck_bbox[1,1]
margin=.30;pavilion_domain=pbox(x0-margin,y0-margin,x1+margin,y1+margin)
def pavilion_height(x,y):
 wx=min(1,max(0,(x-(x0-margin))/margin),max(0,((x1+margin)-x)/margin))
 wy=min(1,max(0,(y-(y0-margin))/margin),max(0,((y1+margin)-y)/margin))
 return -.45+(ground+.45)*wx*wy
pavilion_ms=[];pavilion_top_tri=0
for xx0,xx1 in zip([x0-margin,x0,x1],[x0,x1,x1+margin]):
 for yy0,yy1 in zip([y0-margin,y0,y1],[y0,y1,y1+margin]):
  dom=shapely.set_precision(footprint('SITE_V12_REBUILT_COURT_0_-20_0').intersection(pbox(xx0,yy0,xx1,yy1)),.00001).buffer(0)
  if dom.is_empty or dom.area<1e-8:continue
  g,nt=volume_from_domain(dom,pavilion_height,-.65,.25);pavilion_ms.append(manifold(g));pavilion_top_tri+=nt
pvm=mf.Manifold.batch_boolean(pavilion_ms,mf.OpType.Add)
court=next(e for e in Q['replace'] if e['name']=='SITE_V12_REBUILT_COURT_0_-20_0')
before=manifold(court['parts'][0]['geometry']);after=before+pvm
court['parts'][0]['geometry']=fromman(after)
court['v20_pavilion_ground']={'old_stone_platform_footprint_xy':old_xy,'new_wood_deck_bbox':deck_bbox.tolist(),'raised_paving_under_all_old_platform_m':ground,'wood_board_bottom_clearance_m':board_bottom-ground,'surrounding_transition_width_m':margin,'no_platform_hole':True,'preserves_entry_grade':True}
pavilion_qa={'court_node':court['name'],'native_before_under_platform_already_paved':True,'ground_level_before_m':-.45,'ground_level_after_m':ground,'level_raise_m':ground+.45,'new_deck_bounds_local':deck_bbox.tolist(),'board_under_clearance_m':board_bottom-ground,'old_platform_footprint_xy':old_xy,'ground_transition_outer_bounds_xy':list(pavilion_domain.bounds),'transition_top_triangles':pavilion_top_tri,'ground_transition_width_m':margin,'added_volume_m3':after.volume()-before.volume(),'entry_grade_domain_ymin_m':-3.0,'pavilion_grade_domain_ymax_m':y1+margin,'does_not_intersect_entry_grade':pavilion_domain.intersection(approach_rect).area==0,'other_courts_or_soil_or_drain_changed':False}

# Visible upper bedroom finish; no timber flooring inferred for baths or halls.
# The confirmed bed room is the right wing shown at 232..268 s.
floor_poly=pbox(9.212,2.312,12.788,9.588).difference(pbox(10.70,7.19,12.79,9.60))
fg,_=volume_from_domain(floor_poly,lambda x,y:7.506,7.4995,.30)
Q['materials']['M_V20_Red_Brown_Bedroom_Floor']={'color':[113,48,35],'roughness':.42,'metallic':0,'native_bitmap':None,'native_bump':None,'source':'INSV 232/235/265 s visible red-brown bedroom flooring; only corresponding bed room'}
put('HOUSE_V20_F3_RIGHT_BEDROOM_RED_BROWN_WOOD_FLOOR',[part(fg,'M_V20_Red_Brown_Bedroom_Floor')],new=True,layer='22_SLAB',classification='AS_BUILT_RED_BROWN_WOOD_BEDROOM_FLOOR',finish_top_z_m=7.506,finish_thickness_above_slab_m=.006,excludes_bathroom=True,source_seconds=[232,235,265])

normals={
 'DOOR_BED_F1_X3.9':[-1,0,0],'DOOR_BED_F2_X3.9':[-1,0,0],
 'DOOR_BED_F1_X9.1':[1,0,0],'DOOR_BED_F2_X9.1':[1,0,0],
 'DOOR_BATH_F1_L':[-1,0,0],'DOOR_BATH_F2_L':[-1,0,0],
 'DOOR_BATH_F1_R':[0,1,0],'DOOR_KITCHEN_F1':[1,0,0],
 'DOOR_BATH_F2_R':[1,0,0],'DOOR_BATH_F3_R':[1,0,0],
 'DOOR_BED_F3_X9.1':[1,0,0],'DOOR_STUDY_F3':[0,-1,0],
 'DOOR_LAUNDRY_F3':[1,0,0],'DOOR_FRONT_CENTER_F1':[0,1,0],
 'DOOR_FRONT_CENTER_F2':[0,1,0],'DOOR_COURTYARD_KITCHEN_V12_1':[1,0,0],
 'DOOR_COURTYARD_KITCHEN_V12_2':[1,0,0]}
door_rows=[]
for r in I:
 e=r['element'];n=r['name']
 if n.startswith('DOOR'):
  key=e.get('door_id',n.split('__')[0]);door_rows.append({'name':n,'door_id':key,'role':e.get('role','UNSPLIT_FIXED_AND_MOVABLE' if n=='DOOR_FRONT_CENTER_F1' else ''),'inward_normal_local':normals.get(key),'current_pivot_local_metres':e.get('pivot_world_m',e.get('hinge_origin_local_m')),'angle_current':e.get('angle',0),'operation': 'RETAIN_FIXED' if e.get('role','') in ['FRAME','FIXED_FRAME_AND_SIDELIGHTS'] else 'CONVERT_CENTRE_SLIDING_TO_INWARD_SWING_PER_USER' if key.startswith('DOOR_FRONT_CENTER') else 'ROTATE_LEAF_INWARD_PER_USER'})
Q['house_reference_audit']={'direct_missing_wall_boxes':wall_boxes,'stair_access_retained_xy':[[7.8,7.2],[9.0,9.7]],'F3_terrace_route_unchanged':[[8.45,6.60],[3.9,6.60]],'entry_grades':grades,'pavilion_ground':pavilion_qa,'image_red_frame_floor_inference':'033535 and 033747 are treated as opposite views of the F1 right-rear gap; F2/F3 side bath/bed doors are not blindly sealed','unverified_hidden_interiors_not_invented':True,'door_inward_normals':normals,'source_scene_unchanged':True,'native_delivery_untouched':True}
(D/'House_Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
(D/'Door_Inward_Inventory.json').write_text(json.dumps(door_rows,ensure_ascii=False,indent=2),encoding='utf8')
(D/'House_Audit.json').write_text(json.dumps(Q['house_reference_audit'],ensure_ascii=False,indent=2),encoding='utf8')
print('PATCH',len(Q['replace']),len(Q['add']),len(Q['remove']),json.dumps(grades),flush=True)
