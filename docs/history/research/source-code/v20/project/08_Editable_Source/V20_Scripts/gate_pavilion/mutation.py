"""Isolated V20 pavilion/inner-gate parts patch. Never writes a native model."""
import sys,json,copy,math,ast,importlib.util
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
O=Path(__file__).parent;B=Path('E:/jz/JIA/Rebuild_V19')
S=json.loads((B/'08_Editable_Source/Architecture_Scene_V19.json').read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
Q={'replace':[],'add':[],'remove':[],'transforms':[],'materials':{},'qa':{}}
def pp(v,f,m):return {'geometry':{'type':'polyhedron','vertices':np.asarray(v).tolist(),'faces':f},'material':m}
def bx(x,y,z,w,d,h,m):return {'geometry':{'type':'box','origin':[x,y,z],'size':[w,d,h]},'material':m}
def put(n,parts,**meta):
 e=copy.deepcopy(E.get(n,{'name':n,'layer':'60_SITE','family':'SITE_MODEL','confidence':'MEDIUM'}))
 for k in ['definition','origin','angle','external_mesh_file']:e.pop(k,None)
 e.update(parts=parts,source='User 2026-10-13 redlines; original INSV 600/625/650/657 seconds; DJI_0303 / DJI_0525 aerial context',dimension_status='User-specified 5 cm deck clearance; other visual fit dimensions unmeasured');e.update(meta)
 (Q['replace'] if n in E else Q['add']).append(e)
 return e
# Courtyard central axis lies around x6.50. West wall inner face x0.125;
# keep its clearance, retract only the axis-side edge by 0.60 m.
anchor=.36;factor=3.6/4.2
def retract(v):
 v=np.array(v,float);v[:,0]=anchor+(v[:,0]-anchor)*factor;return v
deck_ground=-.43038;deck_bottom=deck_ground+.05;deck_top=deck_bottom+.025
for n,e in E.items():
 if not n.startswith('SITE_GAZEBO') or n in ['SITE_GAZEBO_V11_STONE_PLATFORM','SITE_GAZEBO_V11_POST_BASE_CONNECTORS']:continue
 parts=[]
 for p in e.get('parts',[]):
  v,f=ex.world_part(p,e);v=retract(v)
  # Keep member widths at columns, shoes, and ordinary beams by centre
  # displacement. Roof/lath strips use a continuous plan contraction.
  if n=='SITE_GAZEBO_POSTS':
   old,f=ex.world_part(p,e);c=old[:,0].mean();v[:,0]=old[:,0]+(anchor+(c-anchor)*factor-c)
   v[np.isclose(v[:,2],-.22,atol=1e-6),2]=deck_top+.025
  if n=='SITE_GAZEBO_V11_TIMBER_RAILS':v[:,2]+=deck_top-(-.25)
  mat='M_Timber_Dark_Eave' if p['material']=='M_Timber_Honey' else p['material']
  parts.append(pp(v,f,mat))
 put(n,parts,v20_axis_retraction={'axis_facing_edge_reduced_m':.6,'fixed_wall_side_x_m':anchor,'plan_scale_x':factor},v20_finish='Photo-observed dark timber; retained photographic asphalt-shingle roof type')
Q['remove']+=['SITE_GAZEBO_V11_STONE_PLATFORM']
# Individual wood strips, real open joints, lightweight joists and isolated
# feet; this is no longer a thick tiled concrete/stone plinth.
Q['materials']['M_V20_Weathered_Deck']={'color':[91,65,43],'roughness':.86,'role':'Weathered timber slat platform, material/board dimensions visually fitted','native_bitmap':str(B/'03_Textures/Modeled_PBR/M_Timber_Dark_Eave_BaseColor.png'),'native_bump':str(B/'03_Textures/Modeled_PBR/Wood_Relief.png')}
slats=[];y=-7.10;board=.138;gap=.006
while y < -3.60-1e-6:
 depth=min(board,-3.60-y);slats.append(bx(.36,y,deck_bottom,3.60,depth,.025,'M_V20_Weathered_Deck'));y+=board+gap
put('SITE_V20_PAVILION_RAISED_WOOD_SLATS',slats,classification='WOOD_SLAT_DECK_5CM_ABOVE_REFERENCE_PAVING',board_bottom_m=deck_bottom,board_top_m=deck_top,board_thickness_m=.025,nominal_ground_m=deck_ground,nominal_bottom_clearance_m=.05,clearance_interpretation='5 cm is taken as deck board underside clearance at central local paving datum; field wording does not specify top versus underside',wood_strip_count=len(slats),open_joint_m=gap)
support=[]
for x in [.44,1.20,2.16,3.12,3.88]:
 support.append(bx(x-.028,-7.07,deck_bottom-.04,.056,3.44,.041,'M_Timber_Dark_Eave'))
 for y in [-6.97,-5.35,-3.73]:support.append(bx(x-.035,y-.035,deck_ground-.002,.070,.070,.012,'M_Metal_Black'))
put('SITE_V20_PAVILION_DECK_JOISTS_AND_FEET',support,classification='LIGHTWEIGHT_WOOD_JOISTS_ON_SMALL_FOOT_PADS',dimension_status='Visible open deck reconstruction; hidden support spacing inferred')
shoe=[]
for x,y in [(.46,-7.0),(4.46,-7.0),(4.46,-3.70),(.46,-3.70)]:
 x=anchor+(x-anchor)*factor
 shoe.append(bx(x-.09,y-.09,deck_top-.006,.18,.18,.010,'M_Metal_Black'))
 for dx in [-.065,.061]:shoe.append(bx(x+dx,y-.065,deck_top+.004,.004,.130,.084,'M_Metal_Black'))
 for dy in [-.065,.061]:shoe.append(bx(x-.061,y+dy,deck_top+.004,.122,.004,.084,'M_Metal_Black'))
put('SITE_GAZEBO_V11_POST_BASE_CONNECTORS',shoe,classification='TIMBER_POST_SHOES_ON_WOOD_DECK',v20_deck_top_m=deck_top)
# A filled, smooth underside was filmed at 657 s, with narrow decorated
# exterior trim. Retire exposed separate modeled rafters/fly-rafters.
sp=importlib.util.spec_from_file_location('v20_gate_parameters',W/'v9_roof_relation/roof_parameters.py');P=importlib.util.module_from_spec(sp);sp.loader.exec_module(P)
tree=ast.parse((W/'v9_eave_layers/mutation.py').read_text(encoding='utf8'));exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='shell'],type_ignores=[]),'<gate_shell>','exec'))
xs=np.linspace(4.17,8.93,65);ys=np.unique(np.round(np.r_[np.linspace(-12.975,-10.265,39),-11.95,-11.62,-11.45],8))
def top(x,y):return P.zgate(x,y)-.55-.073
def underside(x,y):
 t=abs((x-6.55)/2.55)
 return 3.00+.18*t**6
Q['materials']['M_V20_GATE_CLOSED_SOFFIT']={'color':[188,184,172],'roughness':.82,'role':'Continuous pale underside filmed at 657 seconds; substrate hidden and unmeasured'}
filled=shell(xs,ys,top,bottom=underside)
put('SITE_GATEHOUSE_VISIBLE_SOFFIT_BOARD',[{'geometry':filled,'material':'M_V20_GATE_CLOSED_SOFFIT'}],classification='CONTINUOUS_CLOSED_GATE_EAVE_BODY_AND_SMOOTH_UNDERSIDE',underside_status='Closed filled volume beneath retained roof; no hollow open rafter stack',reference_seconds=[650,657],hidden_substrate='Not asserted; visible closed surface only')
Q['remove']+=['SITE_GATEHOUSE_VISIBLE_RAFTER_HEADS','SITE_GATEHOUSE_VISIBLE_FLY_RAFTER_ENDS']
Q['qa']={'pavilion':{'old_axis_edge_x_m':4.56,'new_axis_edge_x_m':3.96,'roof_edge_retracted_m':.60,'old_stone_platform_removed':True,'reference_ground_m':deck_ground,'board_under_clearance_m':.05,'board_thickness_m':.025,'deck_top_m':deck_top,'reference_footage_seconds':[600,625],'metric_fit_status':'User 5 cm intent implemented; 0.60 m plan retraction and other dimensions are photograph-fit estimates'},'inner_gate':{'old_exposed_layer_nodes_removed':['SITE_GATEHOUSE_VISIBLE_RAFTER_HEADS','SITE_GATEHOUSE_VISIBLE_FLY_RAFTER_ENDS'],'preserved_real_visible_narrow_trim':['SITE_GATEHOUSE_FASCIA_BOARD','SITE_GATEHOUSE_EAVE_FRIEZE','SITE_GATEHOUSE_HANGING_TOOTH_ORNAMENT'],'closed_soffit_body_bounds_xy':[4.17,-12.975,8.93,-10.265],'reference_footage_seconds':[650,657],'field_substrate_unmeasured':True},'perimeter':'V19 calibrated perimeter walls, drainage, screenwall and outer gate geometry unchanged; root owns inward-opening doors'}
(O/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
(O/'Audit.json').write_text(json.dumps(Q['qa'],ensure_ascii=False,indent=2),encoding='utf8')
print('PATCH',len(Q['replace']),'replace',len(Q['add']),'add',len(Q['remove']),'remove',len(slats),'wood strips')
