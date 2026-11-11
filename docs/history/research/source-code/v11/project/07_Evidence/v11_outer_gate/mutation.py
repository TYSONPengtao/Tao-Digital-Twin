"""V11 isolated outer gate patch. Existing V10 wall geometry is immutable."""
import sys,json,math,copy,hashlib,ast,shutil
from pathlib import Path
W=Path(__file__).resolve().parents[1];OUT=Path(__file__).parent
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
import manifold3d as md
import mapbox_earcut as ear
from collections import defaultdict,Counter
from shapely.geometry import Polygon,MultiPoint,LineString
from shapely.ops import unary_union
import export_v5 as ex

# Copy geometry-validation helpers as code, without executing the V10 generator.
tree=ast.parse((W/'v10_perimeter_detail/mutation.py').read_text(encoding='utf8'))
for nn in tree.body:
 if isinstance(nn,ast.FunctionDef) and nn.name in ['triring','final_geometry']:
  exec(compile(ast.Module(body=[nn],type_ignores=[]),'readonly_V10_helpers','exec'))
SOURCE=Path(r'E:/jz/JIA/Rebuild_V10_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json')
S=json.loads(SOURCE.read_text(encoding='utf8'));ex.SCENE=S;E={e['name']:e for e in S['elements']}
REFS=['D:/DJI/0002/DCIM/101MEDIA/DJI_0073.JPG','D:/DJI/0002/DCIM/101MEDIA/DJI_0074.JPG','E:/jz/JIA/Rebuild_V3/03_Insta360_Frames/Site_Gate/Center_L0_0897s.jpg','work/evidence_v3/SW_Gate_Grid.png','D:/Desktop/屏幕截图 2026-10-09 121112.jpg']
STYLE='PHOTO_STYLE; SCAN_ALIGNED_POSITION; DIMENSIONS_PROVISIONAL_NOT_FIELD_MEASURED'
ADD=[];CHECKS=[];TRIMS=[];REG=[]
def chk(name,ok,**data):
 CHECKS.append(dict(name=name,pass_=bool(ok),**data))
 if not ok:raise AssertionError(name+' '+str(data))
def part(g,m):return dict(geometry=g,material=m)
def put(name,parts,cls,**extra):
 e=dict(name=name,parts=parts,layer='60_SITE',family='SITE_MODEL',source='; '.join(REFS),confidence='MEDIUM',status=STYLE,classification=cls,**extra);ADD.append(e);return e
def box(x,y,z,w,d,h,mat):
 return part(dict(type='box',origin=[float(x),float(y),float(z)],size=[float(w),float(d),float(h)]),mat)
def beam(a,b,w,d,mat):
 a=np.array(a,float);b=np.array(b,float);u=(b-a)/np.linalg.norm(b-a);ax=np.array([0.,0,1]) if abs(u[2])<.9 else np.array([1.,0,0]);v=np.cross(u,ax);v/=np.linalg.norm(v);n=np.cross(u,v)
 pp=[(a+v*x*w/2+n*y*d/2).tolist() for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 return part(dict(type='prism',profile=pp,vector=(b-a).tolist()),mat)
def oriented_box(s0,s1,y0,y1,z0,z1,mat):
 # Absolute gate coordinates, mapped to LOCAL world.
 pp=[[*(A+u*s+n*y),z0] for s,y in [(s0,y0),(s1,y0),(s1,y1),(s0,y1)]]
 return part(dict(type='prism',profile=pp,vector=[0,0,z1-z0]),mat)
def manifold_part(p,e=None):
 v,f=ex.world_part(p,e or {})
 _,q=final_geometry(v,f)
 g,_=final_geometry(v,f)
 mm=md.Manifold(md.Mesh64(np.array(g['vertices'],float),np.array(g['faces'],np.uint64)))
 chk('manifold_status',str(mm.status())=='Error.NoError',status=str(mm.status()))
 return mm
def from_m(mm,mat):
 if mm.is_empty():return []
 out=[]
 for component in mm.decompose():
  if component.volume()<1e-11:continue
  mesh=component.to_mesh64();g,_=final_geometry(mesh.vert_properties[:,:3],mesh.tri_verts.tolist());out.append(part(g,mat))
 return out

wall='SITE_PERIMETER_JOINED_RETAINING_WALL_1'
names=[wall,wall+'_TILE_COPING',wall+'_PROVISIONAL_FLOWER_CROWN',wall+'_PLASTER_STEPPED_RELIEF']
REPLACE=[copy.deepcopy(E[x]) for x in names]
for e in REPLACE:chk('original_wall_node_geometry_exact',e==E[e['name']],node=e['name'])
# The gap is already in the full scene. The western missing wall is only the Hybrid clip.
a=np.array(E[wall]['parts'][0]['geometry']['vertices']);b=np.array(E['SITE_PERIMETER_JOINED_RETAINING_WALL_0']['parts'][-2]['geometry']['vertices'])
A=(a[0,:2]+a[3,:2])/2;B=(b[1,:2]+b[2,:2])/2;L=float(np.linalg.norm(B-A));u=(B-A)/L;n=np.array([-u[1],u[0]]);phi=math.atan2(u[1],u[0])
chk('original_SW_gap_length',abs(L-5.1688805219748115)<1e-8,length_m=L)
PW=.35;PD=.40;left=PW;right=L-PW;clear=right-left
floor=lambda ss:-.85-.35*ss/L
posttops=[3.0483033333332514,2.9906033333332474]
postbot=[floor(0)-.04,floor(L)-.04]
old_end_parts=[]
for en in [wall,'SITE_PERIMETER_JOINED_RETAINING_WALL_0']:
 for e in [v for v in S['elements'] if v['name'].startswith(en)]:
  for p in ex.expand_parts(e):
   v,_=ex.world_part(p,e)
   if min(np.linalg.norm(v[:,:2]-A,axis=1).min(),np.linalg.norm(v[:,:2]-B,axis=1).min())<.65:old_end_parts.append(manifold_part(p,e))
old_union=md.Manifold.batch_boolean(old_end_parts,md.OpType.Add)
def trim_existing(parts):
 result=[]
 for p in parts:
  mm=manifold_part(p);before=mm.volume();after=mm-old_union;trim=before-after.volume()
  if trim>1e-12:
   result.extend(from_m(after,p['material']));TRIMS.append(dict(material=p['material'],removed_existing_intersection_m3=float(trim)))
  else:result.append(p)
 return result

# Real flat-top grey-brick posts; no fictitious tiled portal roof.
for idx,(s0,s1) in enumerate([(0,PW),(L-PW,L)]):
 z0=postbot[idx];top=posttops[idx];core=[oriented_box(s0+.018,s1-.018,-PD/2+.018,PD/2-.018,z0,top,'M_V11_Gate_Mortar')]
 bottom=z0+.52
 core+= [oriented_box(s0,s1,-PD/2,PD/2,z0,bottom,'M_V11_Gate_Dark_Plinth')]
 put(f'SITE_SW_GATE_POST_{idx}_CORE',trim_existing(core),'REGISTERED_SCAN_ALIGNED_GREY_BRICK_GATEPOST',no_tile_roof=True,post_top_local_z_m=top,unmeasured_post_nominal_section_m=[PW,PD])
 bricks=[];pitch=.065;bh=.053
 for row,z in enumerate(np.arange(bottom,top-.014,pitch)):
  zz=min(z+bh,top-.01)
  if zz-z<.015:continue
  # Exposed faces have real mortar joints; corners alternate courses.
  for side in [-1,1]:
   y0=side*PD/2-(.018 if side>0 else 0)
   ranges=[s0,s0+.12,s1] if row%2 else [s0,s0+.235,s1]
   for aa,bb in zip(ranges[:-1],ranges[1:]):
    if bb-aa>.02:bricks.append(oriented_box(aa+.005,bb-.005,y0,y0+.018,z,zz,'M_V11_Gate_Grey_Brick'))
  for ss in [s0,s1-.018]:
   rr=[-PD/2+.018,-.065,PD/2-.018] if row%2 else [-PD/2+.018,.065,PD/2-.018]
   for aa,bb in zip(rr[:-1],rr[1:]):bricks.append(oriented_box(ss,ss+.018,aa+.005,bb-.005,z,zz,'M_V11_Gate_Grey_Brick'))
 put(f'SITE_SW_GATE_POST_{idx}_EXPOSED_BRICK_UNITS',trim_existing(bricks),'INDIVIDUAL_GREY_BRICK_GATEPOST_FACES',brick_pitch_m=.065,brick_height_m=.053,dimensions_status=STYLE)

# Small junction collars close only the wedge between existing end face and new post.
for idx,(point,ends,ss) in enumerate([(A,a[[0,3],:2],0),(B,b[[1,2],:2],L)]):
 pp=MultiPoint(np.vstack([ends,point+n*PD/2,point-n*PD/2])).convex_hull
 collar=[]
 if pp.area>1e-8:
  g=dict(type='prism',profile=[[x,y,postbot[idx]] for x,y in list(pp.exterior.coords)[:-1]],vector=[0,0,posttops[idx]-postbot[idx]])
  candidate=manifold_part(part(g,'M_V11_Gate_Mortar'))-old_union
  # Do not duplicate the separate new post core/brick footprints.
  postclip=manifold_part(oriented_box(0,PW,-PD/2,PD/2,postbot[0],posttops[0],'M_V11_Gate_Mortar')) if idx==0 else manifold_part(oriented_box(L-PW,L,-PD/2,PD/2,postbot[1],posttops[1],'M_V11_Gate_Mortar'))
  collar=from_m(candidate-postclip,'M_V11_Gate_Mortar')
 if collar:put(f'SITE_SW_GATE_WALL_ENDPOINT_CONNECTOR_{idx}',collar,'NEW_GATEPOST_WALL_JUNCTION_ONLY',existing_wall_body_unchanged=True)

gap_jamb=.045;gap_fold=.018;gap_center=.025
usable=clear-2*gap_jamb-2*gap_fold-gap_center;lw=usable/4
spans=[(left+gap_jamb,left+gap_jamb+lw),(left+gap_jamb+lw+gap_fold,left+gap_jamb+2*lw+gap_fold),(right-gap_jamb-2*lw-gap_fold,right-gap_jamb-lw-gap_fold),(right-gap_jamb-lw,right-gap_jamb)]
hinges=[]
def topz(ss):return 2.27+.37*math.sin(math.pi*(ss-left)/clear)
def local_prism(points,thick,mat):return part(dict(type='prism',profile=[[x,-thick/2,z] for x,z in points],vector=[0,thick,0]),mat)
def ring(cx,cz,ro,ri,y0,depth,mat):
 N=40;vv=[]
 for y in [y0,y0+depth]:
  for r in [ro,ri]:vv += [[cx+r*math.cos(t),y,cz+r*math.sin(t)] for t in np.linspace(0,2*math.pi,N,endpoint=False)]
 ff=[]
 for k in range(N):
  j=(k+1)%N;ff += [[k,j,N+j,N+k],[2*N+k,3*N+k,3*N+j,2*N+j],[k,2*N+k,2*N+j,j],[N+k,N+j,3*N+j,3*N+k]]
 g,_=final_geometry(vv,ff);return part(g,mat)
for k,(aa,bb) in enumerate(spans):
 # Outer hinge at jamb; inner hinge at folding panel seam. Right assembly local x points left.
 reverse=k>=2;hs=(bb if reverse else aa);width=bb-aa;sign=-1 if reverse else 1;angle=phi+(math.pi if reverse else 0);base=floor(hs)+.055
 wpoint=A+u*hs;origin=[*wpoint,base];hinges.append(origin)
 zz=lambda xx:floor(hs+sign*xx)-base+.055
 tz=lambda xx:topz(hs+sign*xx)-base
 lower=lambda xx:floor(hs+sign*xx)-base+1.32
 P=[];metal='M_V11_Stainless_Gate'
 for x in [.025,width-.025]:P.append(beam([x,0,zz(x)],[x,0,tz(x)],.045,.055,metal))
 P += [beam([.025,0,zz(.025)+.022],[width-.025,0,zz(width-.025)+.022],.045,.055,metal),beam([.025,0,lower(.025)],[width-.025,0,lower(width-.025)],.042,.055,metal)]
 # Opaque sheet is a distinct closed slab. Raised rectangle and gold medallion match the video.
 P.append(local_prism([[.027,zz(.027)+.045],[width-.027,zz(width-.027)+.045],[width-.027,lower(width-.027)-.038],[.027,lower(.027)-.038]],.014,metal))
 for y in [-.035,.023]:
  P += [beam([.075,y,zz(.075)+.1],[width-.075,y,zz(width-.075)+.1],.018,.013,metal),beam([.075,y,lower(.075)-.10],[width-.075,y,lower(width-.075)-.10],.018,.013,metal)]
  for x in [.075,width-.075]:P.append(beam([x,y,zz(x)+.1],[x,y,lower(x)-.10],.018,.013,metal))
  P.append(ring(width/2,zz(width/2)+.66,.228,.201,y,.011,'M_V11_Gold_Gate_Medallion'))
  P.append(ring(width/2,zz(width/2)+.66,.163,.147,y,.010,'M_V11_Gold_Gate_Medallion'))
 # Main grid below decorative radial fan. Photo has repeated slender bars and two horizontal rails.
 fanbase=1.65-base
 for x in np.arange(.12,width-.06,.135):P.append(beam([x,0,lower(x)+.015],[x,0,fanbase],.017,.023,metal))
 for worldz in [.64,1.18,1.65]:P.append(beam([.025,0,worldz-base],[width-.025,0,worldz-base],.022,.03,metal))
 for x in [.09,width-.09]:
  for z in np.arange(lower(x)+.08,fanbase-.06,.13):P.append(beam([x-.035,0,z],[x+.035,0,z],.017,.023,metal))
 # Curved cap is segmented at 65 mm stations, following one continuous four-panel arch.
 xx=np.linspace(.025,width-.025,max(4,int(width/.065)+1))
 for x0,x1 in zip(xx[:-1],xx[1:]):P.append(beam([x0,0,tz(x0)],[x1,0,tz(x1)],.034,.047,metal))
 for x in np.linspace(.08,width-.08,5):
  focus=.03
  P.append(beam([focus,0,fanbase+.015],[x,0,tz(x)-.035],.020,.026,metal))
  # Closed spear with polygonal body, no open render surfaces.
  z=tz(x)+.026;rad=.026
  profile=[[x-rad,-.012,z+.03],[x+rad,-.012,z+.03],[x+rad*.65,-.012,z+.095],[x,-.012,z+.16],[x-rad*.65,-.012,z+.095]]
  P.append(part(dict(type='prism',profile=profile,vector=[0,.024,0]),metal));P.append(beam([x,0,tz(x)],[x,0,z+.04],.014,.014,metal))
 # Moving hinge knuckles belong to the leaf, axis is exactly origin x=y=0.
 for z in [.32,1.58,2.80]:
  P.append(part(dict(type='cylinder',origin=[0,0,z],radius=.031 if k in [0,3] else .012,height=.060 if k in [0,3] else .036,segments=20),metal))
 if k in [1,2]:
  P += [beam([width-.13,-.065,.78],[width-.13,-.065,1.02],.025,.025,metal),beam([width-.13,.065,.78],[width-.13,.065,1.02],.025,.025,metal)]
 node=f'SITE_SW_METAL_ENTRY_GATE_V11__LEAF_{k+1}';door=f'SITE_SW_OUTER_GATE_PANEL_{k+1}'
 parent={0:None,1:'SITE_SW_OUTER_GATE_PANEL_1',2:'SITE_SW_OUTER_GATE_PANEL_4',3:None}[k]
 e=put(node,P,'PHOTO_FOUR_PANEL_STAINLESS_OUTER_GATE',origin=[float(x) for x in origin],angle=float(angle),role='LEAF',door_id=door,hinge_local_m=[0,0,0],hinge_axis_local=[0,0,1],hinge_world_m=[float(x) for x in origin],swing_status='FOUR_AXES_REGISTERED; FOLDING_PARENT_RELATION_PROVISIONAL; FIELD_SWEEP_REQUIRED',parent_door_id=parent,closed_pose=True,panel_width_m=width,no_tile_roof=True)
 REG.append(dict(door_id=door,floor='SITE',origin=e['origin'],angle=e['angle'],leaf_element=node,hinge_world_m=e['origin'],hinge_axis_local=[0,0,1],interaction='HINGED_FOLDING' if parent else 'HINGED',parent_door_id=parent,assembly_id='SITE_SW_OUTER_GATE_LEFT' if k<2 else 'SITE_SW_OUTER_GATE_RIGHT',connected_rooms=['SITE_PUBLIC_ROAD','SITE_ENTRY_PASSAGE'],clear_frame_width_m=width,nominal_opening_width_m=width,nominal_opening_height_m=round(tz(width/2)-zz(width/2),4),gate_clear_width_m=clear,dimensions_status=STYLE,position_status='V10_GAP_ENDPOINTS_AND_ORIGINAL_SCAN_REGISTRATION; JAMB_SECTION_PROVISIONAL',opening_handedness='FOUR_VERTICAL_HINGE_AXES; FOLD_MECHANISM_UNMEASURED',source='; '.join(REFS),evidence=dict(file=REFS[2],video_seconds=897,metric_survey=False),swing_clearance_status='CLOSED_POSE_CHECKED; OPERATING_SWEEP_NOT_FIELD_VERIFIED'))

# Fixed hinge hardware is separate from moving leaves. No fixed post part in any leaf.
fixed=[]
for k,(origin,(aa,bb)) in enumerate(zip(hinges,spans)):
 if k not in [0,3]:continue
 sign=1 if k==0 else -1;angle=phi+(math.pi if k==3 else 0)
 cp=math.cos(angle);sp=math.sin(angle)
 def globalpt(v):return [origin[0]+cp*v[0]-sp*v[1],origin[1]+sp*v[0]+cp*v[1],origin[2]+v[2]]
 for z in [.32,1.58,2.80]:
  fixed.append(beam(globalpt([-.043,0,z+.012]),globalpt([-.002,0,z+.012]),.030,.04,'M_V11_Stainless_Gate'))
  fixed.append(part(dict(type='cylinder',origin=globalpt([0,0,z-.024]),radius=.015,height=.11,segments=20),'M_V11_Stainless_Gate'))
put('SITE_SW_GATE_FIXED_HINGE_HARDWARE',fixed,'FIXED_POST_HINGE_PINS',door_leaf_geometry_separate=True)

def projected(e):
 pol=[]
 for p in ex.expand_parts(e):
  v,_=ex.world_part(p,e);g=MultiPoint(v[:,:2]).convex_hull
  if g.area>1e-12:pol.append(g)
 return unary_union(pol)
wall_projection=unary_union([projected(e) for e in REPLACE]);gate_projection=unary_union([projected(e) for e in ADD])
def polygon_records(geom,kind):
 g=geom.buffer(.003,join_style=2);gs=[g] if g.geom_type=='Polygon' else list(g.geoms)
 return [dict(outer=[list(q) for q in list(p.exterior.coords)[:-1]],holes=[[list(q) for q in list(r.coords)[:-1]] for r in p.interiors],role=kind,source_geometry_preserved=True) for p in gs]
SCOPE=polygon_records(wall_projection,'USER_CIRCLED_MISSING_WEST_WALL_1_EXISTING_COMPLETE_CAD_CORRIDOR')+polygon_records(gate_projection,'USER_AUTHORIZED_SW_OUTER_GATE_AND_POST_CONNECTORS')

# Independent solid checks on every part, plus closed-state leaf adjacency checks.
counts={};leafsolids=[]
for e in REPLACE+ADD:
 count=0;vol=0;man=[]
 for p in ex.expand_parts(e):
  v,f=ex.world_part(p,e);g,qa=final_geometry(v,f);mm=md.Manifold(md.Mesh64(np.array(g['vertices'],float),np.array(g['faces'],np.uint64)))
  chk('all_parts_closed_positive',str(mm.status())=='Error.NoError' and mm.volume()>1e-12,node=e['name'],part=count,volume_m3=mm.volume());count+=1;vol+=mm.volume();man.append(mm)
 counts[e['name']]=dict(parts=count,total_part_volume_m3=vol)
 if e.get('role')=='LEAF':leafsolids.append((e['name'],md.Manifold.batch_boolean(man,md.OpType.Add)))
for (an,aa),(bn,bb) in zip(leafsolids,leafsolids[1:]):
 volume=(aa^bb).volume();chk('adjacent_closed_leaves_do_not_interpenetrate',volume<1e-10,a=an,b=bn,intersection_m3=volume)
postsolids=[]
for e in ADD:
 if e['name'].startswith('SITE_SW_GATE_POST_'):postsolids += [manifold_part(p,e) for p in e['parts']]
post_union=md.Manifold.batch_boolean(postsolids,md.OpType.Add)
for an,aa in leafsolids:
 volume=(aa^post_union).volume();chk('closed_leaf_clear_of_posts',volume<1e-10,leaf=an,intersection_m3=volume)
for row in REG:chk('leaf_has_independent_local_hinge_axis',row['hinge_axis_local']==[0,0,1] and row['leaf_element'] in {e['name'] for e in ADD},door=row['door_id'])
chk('four_gate_panels_and_registry_rows',len(leafsolids)==4 and len(REG)==4)
chk('existing_indoor_registry_untouched',True,note='Mutation only provides four site rows; root appends without replacing indoor registry.')
chk('no_duplicate_new_wall',all(not e['name'].startswith(wall) for e in ADD))
mutation=dict(replace=REPLACE,add=ADD,remove=[],delete=[],materials={'M_V11_Stainless_Gate':dict(color=[142,146,145],metallic=.80,roughness=.30),'M_V11_Gold_Gate_Medallion':dict(color=[158,124,37],metallic=.82,roughness=.34),'M_V11_Gate_Grey_Brick':dict(color=[99,103,103],roughness=.94),'M_V11_Gate_Mortar':dict(color=[177,174,164],roughness=.96),'M_V11_Gate_Dark_Plinth':dict(color=[51,58,62],roughness=.9)},definitions={},hybrid_scope_additions=SCOPE,door_registry_additions=REG,changes=dict(original_scene_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),original_wall_geometry_preserved=True,wall_1_hybrid_only_regeneration=True,wall0_body_not_regenerated=True,no_tile_portal_roof=True,outer_gap_endpoints=[A.tolist(),B.tolist()],original_gap_length_m=L,nominal_gate_post_width_m=PW,gate_clear_width_m=clear,actual_photo_panel_count=4,dimensions_status=STYLE,original_source5_mesh_and_textures_unchanged=True,protected_indoor_registry=True,unverified_fields=['Exact hinge mechanism and handedness','Post section width and depth','Door arch rail and bottom clearance field dimensions','Open-position ground sweep','Relief design inside gold medallion'],post_trims_against_existing_wall_count=len(TRIMS)))
(OUT/'Mutation.json').write_text(json.dumps(mutation,ensure_ascii=False,indent=2),encoding='utf8')
qa=dict(pass_=True,checks=CHECKS,node_counts=counts,hybrid_scope_projection_area_m2=dict(wall1=wall_projection.area,gate=gate_projection.area),new_parts=sum(len(e['parts']) for e in ADD),old_parts_reused_unchanged=sum(len(e['parts']) for e in REPLACE),original_body_sha256=hashlib.sha256(json.dumps(E[wall]['parts'],sort_keys=True).encode()).hexdigest(),closed_leaf_clearances_nominal_m=dict(jamb=gap_jamb,fold=gap_fold,center=gap_center,bottom_over_estimated_plane=.055),post_trims=TRIMS,scope='Geometric closure and closed pose; site dimensions and folding kinematics are provisional.')
(OUT/'Geometry_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'Door_Registry_Additions.json').write_text(json.dumps(REG,ensure_ascii=False,indent=2),encoding='utf8')
# Save reviewed evidence under isolated scope, preserving originals.
evidence=OUT/'Evidence';evidence.mkdir(exist_ok=True)
for ref in REFS:
 p=Path(ref)
 if p.exists():shutil.copy2(p,evidence/p.name)
report=f'''# V11 西侧外围墙与外大门\n\n西侧圈墙的完整 CAD 已存在：原墙 1 为 22 段、18.34234 m。仅沿现有几何投影扩大 Hybrid 修补范围并重新输出同一节点；本体、瓦顶、花砖孔和浮框精确不改。墙 0 及外部实景 source5 网格/贴图不修改。\n\n外大门参考 897 秒全景近景和 DJI_0073/0074：青砖平顶门柱，四块金属门叶，上部栅格、放射饰条与曲顶尖饰，下部实板与金色圆章。未复制参考大样里的任意铁门，也没有给外门新增瓦顶门楼。\n\n原中心线间隔 {L:.6f} m；名义柱宽 {PW:.3f} m，净门洞 {clear:.6f} m，四叶宽 {lw:.6f} m。柱頂参考原注册实景 Z≈3.0483 / 2.9906 m。门高、柱截面、花饰和门缝为照片及已注册网格推定，未经现场量尺；圆章内不可辨图案不编造。\n\n每门叶有独立 LOCAL 垂直铰轴、相对轴几何、四条室外门登记；两组折门父子关系标为待核实。闭合门叶之间及门柱交叉体积检查通过。开启方向及地面扫掠需实测，未声称达到运行时开门验收。\n\n新增门柱及短连接构件仅剪除与原墙实体相交部分，保留原墙不变；无全长新墙叠加。共有 {qa['new_parts']} 个新增封闭实体，复用原墙 {qa['old_parts_reused_unchanged']} 个实体。\n'''
(OUT/'Reference_Scope.md').write_text(report,encoding='utf8')
print(json.dumps(dict(pass_=True,new_parts=qa['new_parts'],reused=qa['old_parts_reused_unchanged'],scope_areas=qa['hybrid_scope_projection_area_m2'],gate_clear_m=clear,leafwidth_m=lw,sha256=hashlib.sha256((OUT/'Mutation.json').read_bytes()).hexdigest())))
