"""V21 isolated main-house as-built correction; no delivery writes."""
import json,sys,ast,copy,math
from pathlib import Path
W=Path(__file__).parents[1];D=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf,export_v5 as ex,mapbox_earcut,shapely
from shapely.geometry import Polygon,box as pbox
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
B=Path('E:/jz/JIA/Rebuild_V20')
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V20.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
I=json.loads((B/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'));ii={r['name']:r for r in I}
for fn,names in [('v11_wall_junction/mutation.py',['triangles','oriented','manifold']),('v19_design.py',['fromman']),('v16_geometry.py',['polys','refine','volume_from_domain'])]:
 tree=ast.parse((W/fn).read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),fn,'exec'))
proof={};Q={'replace':[],'add':[],'remove':[],'materials':{},'cameras':[]};DU={'upsert':[],'remove':[]};AUD={'source_video':'E:/jz/VID_20260507_152114_00_001.insv','native_baseline':'V20','metric_positions':'Photo-fit from existing registered model; unmeasured','evidence':[],'checks':{}}
def part(g,m):return {'geometry':g,'material':m}
def box(x,y,z,w,d,h,m='M_Wall_Interior'):return part({'type':'box','origin':[x,y,z],'size':[w,d,h]},m)
def put(n,ps,**meta):
 e=copy.deepcopy(E.get(n,{'name':n,'layer':'11_WALL_INT','family':'ARCH_MODEL'}));e['parts']=ps
 for k in ['definition','origin','angle','external_native_cache','v20_native_cache_override','native_geometry_file']:e.pop(k,None)
 e.update(source='User annotated 2026-10-13 and original INSV 155..200/265 seconds',confidence='USER_CORRECTED_PHOTO_FIT',**meta)
 Q['replace' if n in E else 'add'].append(e);return e
def wparts(e):
 return [part({'type':'polyhedron','vertices':ex.world_part(p,e)[0].tolist(),'faces':ex.world_part(p,e)[1]},p['material']) for p in ex.expand_parts(e)]
def tv(ps,vec):
 out=copy.deepcopy(ps)
 for p in out:
  g=oriented(p['geometry']);g['vertices']=(np.asarray(g['vertices'])+np.array(vec)).tolist();p['geometry']=g
 return out
def turn(ps,pivot,deg):
 a=math.radians(deg);r=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);out=copy.deepcopy(ps)
 for p in out:
  g=oriented(p['geometry']);g['vertices']=((np.array(g['vertices'])-pivot)@r.T+pivot).tolist();p['geometry']=g
 return out
def unionps(ps):return mf.Manifold.batch_boolean([manifold(p['geometry']) for p in ps],mf.OpType.Add)
def native(n):
 d=np.load(B/'02_Data'/ii[n]['file']);return d['vertices'],d['faces']
def extruded(domain,lo,hi):
 rings=[]
 for pg in polys(domain):
  pg=orient(pg,1);rings.append(np.array(pg.exterior.coords[:-1],float));rings.extend(np.array(r.coords[:-1],float) for r in pg.interiors)
 mm=mf.CrossSection(rings,mf.FillRule.Positive).extrude(hi-lo).translate([0,0,lo]);assert mm.status()==mf.Error.NoError
 return fromman(mm)
def bboxps(ps):
 v=np.vstack([np.array(oriented(p['geometry'])['vertices']) for p in ps]);return np.array([v.min(0),v.max(0)])

# Verified 160/265s corner relationship: dark bedroom doorway next to light study
# door, south of the column. User's red X specifically rules out the north hole.
n='PARTITIONS_JOINED_F3';m=unionps(wparts(E[n]))
close=manifold({'type':'box','origin':[9.0,7.55,7.5],'size':[.20,.90,2.10]})
newcut=manifold({'type':'box','origin':[8.96,6.15,7.499],'size':[.28,.90,2.102]})
newwall=(m+close)-newcut
put(n,[part(fromman(newwall),'M_Wall_Interior')],v21_f3_correction={'old_wrong_aperture_xy':[9.0,7.55,9.2,8.45],'new_bedroom_aperture_xy':[9.0,6.15,9.2,7.05],'existing_study_door_retained':True,'stair_hall_retained':True})
n='DOOR_BED_F3_X9.1__FRAME';put(n,tv(wparts(E[n]),[0,-1.4,0]),role='FRAME',v21_opening='BEDROOM_DOOR_SOUTH_OF_COLUMN')
n='DOOR_BED_F3_X9.1__LEAF';old=E[n];pp=np.array(old['pivot_world_m']);closed=turn(wparts(old),pp,-old['open_angle_degrees']);closed=tv(closed,[0,-1.4,0]);npivot=(pp+[0,-1.4,0]).tolist();op=turn(closed,npivot,-90)
put(n,op,role='LEAF',interaction='HINGED_INWARD',pivot_world_m=npivot,open_angle_degrees=-90,inward_normal_local_xy=[1,0],current_pose='OPEN_INWARD',v21_door=True)
DU['upsert'].append({'name':n,'operation':'HINGED_INWARD','hinge_local_m':npivot,'open_angle_deg':-90,'inward_normal_local_xy':[1,0],'parent_door_id':None})
AUD['evidence'].append({'issue':'F3 incorrect bedroom door north of column','references':['150915 user marked left X/right red rectangle','original INSV 160s L0 and265s L1','new155s and165s L0'],'action':'Fill old doorway y7.55..8.45 and move existing frame/leaf to y6.15..7.05 south of pillar; study door and bathroom retained','confidence':'User-confirmed side; metric offsets fitted to retained wall and column'})

# F3 west end corridor is a plain, unleafed opening to the covered terrace.
for n in ['DOOR_LAUNDRY_F3__LEAF','DOOR_LAUNDRY_F3__FRAME']:Q['remove'].append(n)
DU['remove'].append('DOOR_LAUNDRY_F3__LEAF')
# Retain original white partition jamb/soffit. Duplicate coplanar reveal skins
# caused black self-shadow artifacts; no extra geometry and no aperture narrowing.
AUD['evidence'].append({'issue':'Fictional timber leaf/casing at F3 terrace exit','references':['download.jfif','INSV165s L0 plain white passage','INSV170s L1 and185s L0'],'action':'Remove inferred timber leaf and frame; retain plain white plaster opening and supported corridor'})

# A dark narrow plinth visible in the 160/165/265s walk follows the supported
# hall wall; stop at each doorway, leaving all entries open.
Q['materials']['M_V21_Dark_Stone_Skirting']={'color':[45,46,45],'roughness':.55,'source':'INSV160/165s F3 landing visible dark baseboard'}
ps=[box(4.002,6.153,7.50,3.99,.012,.082,'M_V21_Dark_Stone_Skirting'),box(8.901,6.153,7.50,.096,.012,.082,'M_V21_Dark_Stone_Skirting')]
put('HOUSE_V21_F3_LANDING_STONE_SKIRT',ps,classification='PHOTO_OBSERVED_LANDING_BASEBOARD')

# Reconstruct the as-built sliding action. Both storeys' center glazing use
# parallel tracks; they retract behind the fixed sidelights with physical depth.
for floor in [1,2]:
 row=[]
 for j in [1,2]:
  n=f'DOOR_FRONT_CENTER_F{floor}__'+(f'LEAF_{j}' if floor==1 else f'SLIDE_{j}')
  old=E[n];closed=turn(wparts(old),old['pivot_world_m'],-old['open_angle_degrees']);bb=bboxps(closed)
  # Both tracks clear stationary 2.150m frame depth by 45mm; same panel plane
  # allows the two center panels to meet when closed and retract to each side.
  closed=tv(closed,[0,2.195-bb[0,1],0]);off=[-1.14 if j==1 else 1.14,0,0];op=tv(closed,off);b0=bboxps(closed);pivot=[6.5,2.195,float(b0[0,2])]
  e=put(n,op,role='LEAF',interaction='SLIDING',operation='SLIDING',pivot_world_m=pivot,open_angle_degrees=0,open_translation_m=off,inward_normal_local_xy=[0,1],current_pose='OPEN_SLIDING',v21_door=True,dimension_status='Existing center aperture and glazing retained; parallel sliding tracks per user')
  e.pop('v20_role',None)
  DU['upsert'].append({'name':n,'operation':'SLIDING','hinge_local_m':pivot,'open_angle_deg':0,'open_translation_m':off,'inward_normal_local_xy':[0,1],'parent_door_id':None})
  row.append({'name':n,'closed_bbox':b0.tolist(),'open_bbox':bboxps(op).tolist(),'travel_m':1.14})
 bottom=0 if floor==1 else 3.9;top=2.10 if floor==1 else 6.0
 ps=[box(4.14,2.13,top-.004,4.72,.18,.028,'MAT_DOOR_FRAME_RED'),box(4.14,2.20,bottom+.005,4.72,.10,.014,'MAT_DOOR_FRAME_RED')]
 put(f'HOUSE_V21_F{floor}_SLIDING_DOOR_TRACKS',ps,layer='30_DOOR',classification='CENTER_GLASS_SLIDING_TRACKS',fixed=True)
 AUD['checks'][f'F{floor}_slides']={'panels':row,'clear_center_width_m':row[1]['open_bbox'][0][0]-row[0]['open_bbox'][1][0]}

# Gray-white rear/side mineral finish only. Project actual existing native outer
# faces into thin closed finish skins: openings and interior white finish remain.
Q['materials']['M_V21_House_Exterior_Grey_White']={'color':[198,198,201],'roughness':.89,'source':'User150622 rear scan facade gray-white; photo-fit daylight base color, not a measured albedo','bitmap':None}
Q['materials']['M_V21_Terrace_Tile']={'color':[204,207,202],'roughness':.60,'source':'INSV170/185s and download.jfif terrace rectangular gray-white tiles'}
Q['materials']['M_V21_Terrace_Grout']={'color':[91,94,90],'roughness':.90,'source':'INSV170/185s visible dark horizontal/vertical tile joints'}
# avoid bitmap key None (assembler copies only actual texture paths)
Q['materials']['M_V21_House_Exterior_Grey_White'].pop('bitmap')
all_geo=[]
for n in E:
 if n.startswith(('FACADE_CONTINUOUS','KZ_','KL_','LL_','SLAB_JOINED')):
  try:v,f=native(n)
  except KeyError:continue
  all_geo.append((n,v,f))
finrows=[]
for side,axis,planes,sgn in [('rear',1,[9.90,10.0,10.012],1),('west',0,[-.1,-.2,-.212],-1),('east',0,[13.1,13.2,13.212],1)]:
 other=1-axis;extent=(.99,10.015) if axis==0 else (-.213,13.213)
 floorps={fi:[] for fi in [1,2,3]};floorareas={fi:[] for fi in [1,2,3]}
 for plane in planes:
  pol=[]
  for n,v,f in all_geo:
   t=v[f];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(nn,axis=1);good=(nn[:,axis]*sgn>length*.995)&(abs(t.mean(1)[:,axis]-plane)<.0001)
   for tri in t[good]:
    poly=Polygon(tri[:,[other,2]])
    if poly.area>1e-9:pol.append(poly)
  if not pol:continue
  dom=shapely.set_precision(unary_union(pol).buffer(0),.00001).buffer(0)
  dom=dom.intersection(pbox(extent[0],0,extent[1],10.6701))
  for fi,(z0,z1) in enumerate([(0,3.9),(3.9,7.5),(7.5,10.6701)],1):
   dd=dom.intersection(pbox(extent[0],z0,extent[1],z1))
   if dd.is_empty or dd.area<1e-8:continue
   lo=plane-.001 if sgn>0 else plane-.004;hi=plane+.004 if sgn>0 else plane+.001
   g=extruded(dd,lo,hi)
   vv=np.array(g['vertices']);ww=np.zeros_like(vv);ww[:,other]=vv[:,0];ww[:,2]=vv[:,1];ww[:,axis]=vv[:,2];g['vertices']=ww.tolist();g=oriented(g)
   floorps[fi].append(part(g,'M_V21_House_Exterior_Grey_White'));floorareas[fi].append({'original_native_face_plane':plane,'outward_offset_m':.004,'back_embed_m':.001,'source_projected_area_m2':dd.area})
 for fi in [1,2,3]:
  if not floorps[fi]:continue
  n=f'HOUSE_V21_{side.upper()}_GREY_WHITE_F{fi}';put(n,floorps[fi],layer='10_WALL_EXT',classification='THIN_CLOSED_EXTERIOR_FINISH_ONLY',side=side,finish_depth_m=.005,native_outer_face_projection=True,preserves_recessed_wall_and_column_planes=True)
  finrows.append({'node':n,'source_projected_area_m2':sum(r['source_projected_area_m2'] for r in floorareas[fi]),'retains_existing_apertures':True,'planes':floorareas[fi]})
AUD['checks']['exterior_finish']=finrows

# Visible third-floor covered terrace wall: rectangular tiles, with modelled
# narrow grout and solid tile surfaces, clipped to actual partition silhouette.
wallp=[]
v,f=native('PARTITIONS_JOINED_F3');t=v[f];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ll=np.linalg.norm(nn,axis=1);good=(nn[:,0]<-.995*ll)&(abs(t.mean(1)[:,0]-3.8)<.006)
for tri in t[good]:
 pg=Polygon(tri[:,[1,2]])
 if pg.area>1e-9:wallp.append(pg)
dom=shapely.set_precision(unary_union(wallp).buffer(0),.00001).intersection(pbox(2.3,7.5,7.1,10.40)).buffer(0)
# Replace earlier guessed tile placement in this terrace sector; retain beyond
# the verified y7.1 boundary so two generations of tiles cannot overlap.
oldtiles=[];cut=manifold({'type':'box','origin':[3.70,2.299,7.49],'size':[.20,4.802,3.0]})
for pp in wparts(E['TERRACE_SIDE_CERAMIC_PANEL_GRID']):
 mm=manifold(pp['geometry'])-cut
 if not mm.is_empty() and mm.volume()>1e-10:oldtiles.append(part(fromman(mm),pp['material']))
put('TERRACE_SIDE_CERAMIC_PANEL_GRID',oldtiles,v21_review='Remove prior guessed tiles over corrected terrace sector; remaining y7.1..9.59 tiles unchanged')
# Actual exit void remains in this silhouette. Tiles meet the existing white jamb.
ps=[]
for yi in range(8):
 for zi in range(10):
  dd=dom.intersection(pbox(2.3+yi*.6+.002,7.5+zi*.3+.002,2.3+(yi+1)*.6-.002,7.5+(zi+1)*.3-.002))
  if dd.area<1e-6:continue
  g=extruded(dd,3.794,3.801);v=np.array(g['vertices']);g['vertices']=v[:,[2,0,1]].tolist();ps.append(part(oriented(g),'M_V21_Terrace_Tile'))
put('HOUSE_V21_F3_TERRACE_RECTANGULAR_TILE_FINISH',ps,layer='10_WALL_EXT',classification='PHOTO_VISIBLE_COVERED_TERRACE_TILE',tile_modules_m=[.60,.30],joint_width_m=.004)
# Joint network as a 3 mm inner backing follows exactly the silhouette and is
# a closed plaster-backed strip, rather than open black planes.
tile_domains=[]
for yi in range(8):
 for zi in range(10):tile_domains.append(pbox(2.3+yi*.6+.002,7.5+zi*.3+.002,2.3+(yi+1)*.6-.002,7.5+(zi+1)*.3-.002))
grd=dom.difference(unary_union(tile_domains));g=extruded(grd,3.797,3.801);v=np.array(g['vertices']);g['vertices']=v[:,[2,0,1]].tolist()
put('HOUSE_V21_F3_TERRACE_TILE_GROUT',[part(oriented(g),'M_V21_Terrace_Grout')],layer='10_WALL_EXT',classification='CLIPPED_4MM_RECESSED_TILE_JOINTS')
AUD['checks']['terrace_tile_area_m2']=dom.area
AUD['checks']['terrace_floor_retained']={'node':'CONSTRUCTION_TERRACE_SLOPED_FINISH','finish_material':'M_Floor','base_color':[168,174,169],'reason':'Existing gray stone textured floor matches170/185s visible gray-veined surface; retain fitted drainage slope and avoid duplicate floor overlay'}
AUD['evidence'].append({'issue':'Ground-floor red missing wall repeat','references':['033535/033747 geometric bathroom door orientation','INSV90/100/110/120 new ground-floor contact'], 'finding':'100sL1 shows narrow beam/partition arrangement;110sL0 confirms rear bathroom adjacency to staircase, unlike F2/F3 east-facing bathroom layout. F1 gap already closed by V20; retained exact solid and revalidated.'})
AUD['checks']['prior_red_F1_missing_wall_patches_retained']='Identified by right wing bathroom glazed door oriented along y7.3 (F1 only; F2/F3 bathroom doors are x10.8 plane), adjacent x9.1/y7.3 pillar, rear window beyond slot. The two red screenshots show opposite sides of F1 rear partition gap. Existing V20 actual infill spans x9.2..10.71/y7.2..7.4; retained and separately probed. Upper-level passage location is geometrically different and retained.'

Q['cameras']=[['V21_F3_Corrected_Door_Landing',[6.8,8.65,9.0],[9.1,7.0,8.55],86],['V21_F3_Doorless_Terrace',[1.45,4.2,8.95],[3.82,6.30,8.70],78],['V21_House_Rear_Facade',[19,19,8.3],[6.5,8.8,5.4],60],['V21_House_Sliding_Entry',[6.5,-1.5,1.1],[6.5,2.25,1.0],75]]
Q['change_notes']=['Correct F3 bedroom door to column south side and seal wrong former north doorway','Remove fictional F3 terrace leaf and timber casing; retain plain white plaster opening','Restore F1 and F2 center glazing sliding doors with independent tracks and default-open panels','Apply thin gray-white exterior finish only to rear and sides using actual native apertures','Add observed F3 covered-terrace rectangular tile/grout and landing baseboard']
(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');(D/'Door_Updates.json').write_text(json.dumps(DU,ensure_ascii=False,indent=2),encoding='utf8');(D/'Design_Control.json').write_text(json.dumps(AUD,ensure_ascii=False,indent=2),encoding='utf8')
print('HOUSE PATCH',len(Q['replace']),len(Q['add']),len(Q['remove']),flush=True)
