"""V7: user-marked wall corrections and photo-grounded visible detail.
Source scene and all survey/photo sources remain immutable.
"""
import sys,json,math,copy,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W/'v4_audit_junction'),str(W)]
import numpy as np
from shapely.geometry import Polygon,box as rect
from shapely.ops import unary_union
import apply_junction_v4 as J
import export_v5 as ex
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid');A=O/'08_Editable_Source'
for p in ['02_Data','03_Textures/Patch','03_Textures/Base','04_Rhino','05_Export','06_Report','07_Evidence/Selected','08_Editable_Source/05_Intermediate','08_Editable_Source/06_Rhino']:(O/p).mkdir(parents=True,exist_ok=True)
S=copy.deepcopy(ex.SCENE);original=copy.deepcopy(S);E={e['name']:e for e in S['elements']};changes=[]
def record(id,els,description,refs,**kw):changes.append(dict(id=id,elements=els,description=description,evidence=refs,metric_status='DRAWING/REGISTERED_MODEL_SCALE; AS_BUILT_TAPE_OFFSETS_REQUIRED',**kw))
def add(name,layer,parts,refs,**kw):
 e=dict(name=name,layer=layer,family='ARCH_MODEL',parts=parts,confidence='MEDIUM',source='; '.join(refs),status='V7_SOURCE_SUPPORTED_DETAIL; METRIC_PROFILES_PROVISIONAL',**kw);S['elements'].append(e);E[name]=e;return e
def part(g,m):return J._part(g,m)
def box(x,y,z,w,d,h,m):return part(J._box(x,y,z,w,d,h),m)
refs=['User annotation 2026-10-08 212249','Panorama 165/200/205s','DJI 0002/DJI_0623.JPG','DJI 0003/DJI_0100.JPG']
# The rear west nook is continuous with the covered terrace. Remove only the
# false infill, retaining columns and reinforced concrete beams.
ops={2:[(rect(4.112,7.2,7.8,7.4),3.9,7.37,'add')],3:[(rect(.212,7.2,3.688,7.4),7.5,10.67,'remove'),(rect(3.8,1.2,4.0,9.588),7.5,10.67,'add'),(rect(3.8,7.55,4.0,8.45),7.5,9.6,'remove')]}
columns=[]
for e in S['elements']:
 if e['name'].startswith(('BEAM_','KZ_')):
  for p in ex.expand_parts(e):
   if p['geometry']['type']=='box':columns.append(J._world_box(e,p))
for f,operations in ops.items():
 e=E['PARTITIONS_JOINED_F'+str(f)];old=e['parts'];breaks={q for p in old for q in [p['geometry']['z'],p['geometry']['z']+p['geometry']['height']]}
 for _,a,b,_ in operations:breaks.update([a,b])
 for _,a,b in columns:
  if min(breaks)<a<max(breaks):breaks.add(a)
  if min(breaks)<b<max(breaks):breaks.add(b)
 new=[]
 for lo,hi in zip(sorted(breaks)[:-1],sorted(breaks)[1:]):
  mid=(lo+hi)/2
  q=unary_union([Polygon(g['outer'],g['holes']) for p in old if (g:=p['geometry'])['z']-1e-8<mid<g['z']+g['height']+1e-8])
  for p,a,b,op in operations:
   if a-1e-8<mid<b-1e-8:q=q.union(p) if op=='add' else q.difference(p)
  q=q.difference(unary_union([p for p,a,b in columns if a-1e-8<mid<b-1e-8]))
  new+=J._prisms(q,lo,hi-lo,'M_Wall_Interior')
 e.update(parts=new,source='V7 user markings and panorama 165/200/205s',status='V7_PER_FLOOR_WALL_TOPOLOGY_CORRECTED',v7_operations=[dict(xy=list(p.bounds),z=[a,b],operation=op) for p,a,b,op in operations])
record('V7_F2_STAIR_FRONT_CLOSE',['PARTITIONS_JOINED_F2'],'二层楼梯前 Y7.3 墙封闭；右侧平台通道保留',['User request 2026-10-08'],closed_xy=[4.112,7.2,7.8,7.4])
record('V7_F3_REMOVE_FALSE_CROSSWALL',['PARTITIONS_JOINED_F3'],'拆除三层西侧打叉的横向误墙，后部窗前区域与雨棚下连通',refs,removed_xy=[.212,7.2,3.688,7.4])
record('V7_F3_TERRACE_SEPARATOR',['PARTITIONS_JOINED_F3'],'补齐西侧阳台与中心房间之间的 X3.9 侧墙分隔，出口设于后部平台侧',refs)
# Rebase both members to keep the true leaf hinge and opening coincident.
id='DOOR_LAUNDRY_F3';fo=[3.9,7.55,7.5];angle=math.pi/2
frame=E[id+'__FRAME'];leaf=E[id+'__LEAF'];previous=frame['origin'][:]
frame.update(origin=fo,angle=angle,source='V7 user specified perpendicular wall; panorama 165/200/205s',status='USER_AND_VIDEO_CORRECTED_TO_TERRACE_EXIT')
off=S['definitions'][leaf['definition']]['parameters']['Hinge_Surface_Offset'];ho=[fo[0]-off,fo[1]+.047,fo[2]]
leaf.update(origin=ho,angle=angle,pivot_world_m=ho,source=frame['source'],status=frame['status'],room_use='TERRACE_EXIT_NOT_LAUNDRY')
for r in S['door_registry']:
 if r['door_id']==id:r.update(origin=fo,angle=angle,hinge_world_m=ho,connected_rooms=['F3-R03','F3-R04'],position_status=frame['status'],source=frame['source'])
for r in S['openings']:
 if r['name']==id:r.update(origin=fo,angle=angle)
S['room_connectivity'][id]=['F3-R03','F3-R04']
for r in S['rooms']:
 if r['room_id']=='F3-R04':r.update(label='西侧雨棚阳台及后部窗前凹区',review_polygon_xy_m=[[.212,1.2],[3.8,1.2],[3.8,9.588],[.212,9.588]],door_ids=[id])
 if r['room_id']=='F3-R06':r.update(label='并入西侧阳台的后部窗前区域',use='TERRACE_REAR_NO_SEPARATING_WALL',door_ids=[],boundary_status='Retired separate laundry assumption; continuous with F3-R04')
 if r['room_id']=='F3-R03' and id not in r['door_ids']:r['door_ids'].append(id)
record('V7_F3_TERRACE_DOOR_ROTATE',[frame['name'],leaf['name'],'PARTITIONS_JOINED_F3'],'旧门退出 Y7.3 横墙，移至垂直的 X3.9 侧墙，门框与门扇同步旋转 90°',refs,old_origin=previous,new_origin=fo,hinge=ho)
# Front gable touches the existing arch beam at Z7.37 and terminates on the
# unchanged roof underside; the real roof overhang remains outside its plane.
gb=[]
for i in [0,1]:gb+=J._support_parts(E['CANOPY_CENTER_'+str(i)]['parts'][0]['geometry'],rect(3.00,-.218,10.00,-.018),7.37,'M_Wall_Exterior')
add('CANOPY_FRONT_CLOSED_GABLE','51_CANOPY',gb,['User red outline 211428','DJI 0002/DJI_0429.JPG','DJI 0003/DJI_0100.JPG'])
record('V7_CLOSED_GABLE',['CANOPY_FRONT_CLOSED_GABLE'],'小坡屋顶前山墙封闭，上接坡屋顶底面，下接拱梁顶面',['DJI 0002/DJI_0429.JPG','DJI 0003/DJI_0100.JPG'],base_z=7.37,front_y=-.218)
# Replace the solid infill with the photographed stone railing: lower relief
# panels, open upper bays, posts and a continuous top rail.
retired=['BALCONY_STONE_JOINED','BALCONY_STONE_COPING_JOINED','BALCONY_PANEL_MOULDING_0','BALCONY_PANEL_MOULDING_1','BALCONY_PANEL_MOULDING_2']
S['v7_retired_elements']=[copy.deepcopy(E[n]) for n in retired if n in E]
S['elements']=[e for e in S['elements'] if e['name'] not in retired]
paths=[([4.122,0],[8.878,0]),([3.9,.222],[3.9,1.9]),([9.1,.222],[9.1,1.9])]
stone=[];panelcount=0
for pi,(aa,bb) in enumerate(paths):
 aa=np.array(aa);bb=np.array(bb);L=np.linalg.norm(bb-aa);u=(bb-aa)/L;n=np.array([-u[1],u[0]]);count=3 if pi==0 else 1;step=L/count
 def railprism(s0,s1,z,h,depth=.13):
  p0=aa+u*s0;p1=aa+u*s1;q=[[*p0-n*depth/2,z],[*p1-n*depth/2,z],[*p1+n*depth/2,z],[*p0+n*depth/2,z]]
  return part({'type':'prism','profile':q,'vector':[0,0,h]},'M_Stone')
 stone += [railprism(0,L,3.98,.08,.17),railprism(0,L,4.06,.50,.09),railprism(0,L,4.56,.06,.14),railprism(0,L,4.94,.11,.15)]
 for j in range(count+1):
  s=j*step;stone+=[railprism(max(0,s-.075),min(L,s+.075),4.06,1.01,.18),railprism(max(0,s-.095),min(L,s+.095),5.07,.10,.20)]
 for j in range(count):
  panelcount+=1
  # Gourd-shaped upper supports are separate capped profiles, leaving actual
  # negative spaces rather than an opaque painted railing strip.
  for sx in [.19,step-.19]:
   st=j*step+sx;zz=[4.62,4.67,4.73,4.78,4.84,4.89,4.94];ww=[.10,.07,.045,.07,.045,.07,.10]
   prof=[[*aa+u*(st-w/2)-n*.05,z] for z,w in zip(zz,ww)]+[[*aa+u*(st+w/2)-n*.05,z] for z,w in reversed(list(zip(zz,ww)))]
   stone.append(part({'type':'prism','profile':prof,'vector':[*n*.1,0]},'M_Stone'))
add('BALCONY_F2_PHOTO_OPEN_STONE_RAIL','41_RAILING',stone,['DJI 0002/DJI_0478.JPG','DJI 0003/DJI_0106.JPG'],open_upper_bays=True,lower_relief_panels=panelcount)
record('V7_F2_BALCONY_OPEN_RAIL',['BALCONY_F2_PHOTO_OPEN_STONE_RAIL']+retired,'二层栏板按照片改为下部石雕面板、上部镂空、分格立柱及扶手；撤销整片实心栏板',['DJI 0002/DJI_0478.JPG'])
# F2 exit assembly has two separate sliding leaves, fixed side panes and a
# transom. Preserve the rough opening; the travel direction is visible in 0478.
old=E['DOOR_FRONT_CENTER_F2'];S['elements'].remove(old);S['v7_retired_elements'].append(copy.deepcopy(old))
fw=4.8;fh=2.1;r=.045;pw=(fw-2*r)/4
fixed=[box(0,-.05,0,r,.10,fh,'MAT_DOOR_FRAME_RED'),box(fw-r,-.05,0,r,.10,fh,'MAT_DOOR_FRAME_RED'),box(r,-.05,fh-r,fw-2*r,.10,r,'MAT_DOOR_FRAME_RED'),box(r,-.05,0,fw-2*r,.10,.025,'MAT_DOOR_FRAME_RED')]
for j in [0,3]:
 x=r+j*pw;fixed += [box(x,-.04,.025,pw,.08,.04,'MAT_DOOR_FRAME_RED'),box(x,-.004,.065,pw,.008,fh-.11,'M_Glass_Clear'),box(x+pw-r,-.04,.025,r,.08,fh-.07,'MAT_DOOR_FRAME_RED')]
add('DOOR_FRONT_CENTER_F2__FIXED','30_DOOR',fixed,['DJI 0002/DJI_0478.JPG'],origin=old['origin'],angle=0,role='FIXED_FRAME_AND_SIDELIGHTS',door_id='DOOR_FRONT_CENTER_F2')
for j,direction in [(1,-1),(2,1)]:
 parts=[box(0,-.025,0,r,.05,fh-.065,'MAT_DOOR_FRAME_RED'),box(pw-r,-.025,0,r,.05,fh-.065,'MAT_DOOR_FRAME_RED'),box(r,-.025,0,pw-2*r,.05,r,'MAT_DOOR_FRAME_RED'),box(r,-.025,fh-.065-r,pw-2*r,.05,r,'MAT_DOOR_FRAME_RED'),box(r,-.004,r,pw-2*r,.008,fh-.065-2*r,'M_Glass_Clear')]
 # A visible handle sits clear of the glass on the inner jamb.
 xx=pw-.09 if direction<0 else .06;parts.append(box(xx,-.045,.82,.02,.02,.30,'M_Timber_Honey'))
 key='V7_BALCONY_SLIDING_LEAF_'+str(j);S['definitions'][key]=dict(parts=parts,parameters=dict(Role='SLIDING_LEAF',Width=pw,Height=fh-.065,Travel_Axis_Local=[direction,0,0],Travel_m=pw-.05),source='DJI 0002 0478; dimensions provisional',confidence='MEDIUM')
 e=add('DOOR_FRONT_CENTER_F2__SLIDE_'+str(j),'30_DOOR',[],['DJI 0002/DJI_0478.JPG'],definition=key,origin=[4.1+r+j*pw,2.1+(-.02 if j==1 else .02),3.925],angle=0,door_id='DOOR_FRONT_CENTER_F2',role='SLIDING_LEAF',interaction='SLIDING',slide_axis_local=[direction,0,0],travel_m_provisional=pw-.05)
for r0 in S['door_registry']:
 if r0['door_id']=='DOOR_FRONT_CENTER_F2':r0.update(frame_element='DOOR_FRONT_CENTER_F2__FIXED',leaf_elements=['DOOR_FRONT_CENTER_F2__SLIDE_1','DOOR_FRONT_CENTER_F2__SLIDE_2'],interaction='TWO_SLIDING_LEAVES',type_status='PHOTO_VISIBLE_SLIDING_PANELS',position_status='ROUGH_OPENING_RETAINED; PANEL_DIVISION_PHOTO_CORRECTED')
for r0 in S['openings']:
 if r0['name']=='DOOR_FRONT_CENTER_F2':r0.update(frame_element='DOOR_FRONT_CENTER_F2__FIXED',leaf_elements=['DOOR_FRONT_CENTER_F2__SLIDE_1','DOOR_FRONT_CENTER_F2__SLIDE_2'])
record('V7_F2_BALCONY_EXIT_PANELS',['DOOR_FRONT_CENTER_F2__FIXED','DOOR_FRONT_CENTER_F2__SLIDE_1','DOOR_FRONT_CENTER_F2__SLIDE_2'],'阳台出口改为固定边玻璃与两片独立推拉门；保留门洞位置',['DJI 0002/DJI_0478.JPG'])
# Visible ceramic panel grid on the terrace side wall. Inset boundaries are
# defined by real separated tiles rather than lines painted across a door.
S['materials']['M_Ceramic_Warm']={'color':[205,203,193],'roughness':.72}
ceramic=[];tileswall=0
for zz in np.arange(7.50,10.40,.4):
 for yy in np.arange(2.312,9.588,.6):
  height=min(.397,10.4-zz);length=min(.597,9.588-yy)
  if height<=0 or length<=0:continue
  if yy<8.45 and yy+length>7.55 and zz<9.6:continue
  ceramic.append(box(3.796,yy+.0015,zz+.0015,.004,length,height,'M_Ceramic_Warm'));tileswall+=1
add('TERRACE_SIDE_CERAMIC_PANEL_GRID','10_WALL_EXT',ceramic,['Panorama 200s','DJI 0002/DJI_0623.JPG'],visible_tile_count=tileswall,joint_width_m=.003)
# Metal canopy purlins and transverse ribs, supported in both drone and video.
metal=[]
for x in [.15,1.05,1.95,2.85]:
 metal.append(part({'type':'prism','profile':[[x-.025,1.0,10.10],[x+.025,1.0,10.10],[x+.025,1.0,10.16],[x-.025,1.0,10.16]],'vector':[0,5.65,.18]},'M_Metal_Black'))
for y in np.arange(1.15,6.65,.8):metal.append(box(-.15,y-.025,10.12+(y-1)*.18/5.65,3.55,.05,.05,'M_Metal_Black'))
add('TERRACE_CANOPY_VISIBLE_PURLINS','51_CANOPY',metal,['DJI 0002/DJI_0623.JPG','Panorama 200s'])
# Turn continuous artificial tile tubes into individually capped, curved tile
# modules. Row pitch is retained from the registered roof; cover-tile profiles
# and length are photo-estimated, expressly not a count of surveyed real tiles.
detailcount=0;rownames=[]
for e in list(S['elements']):
 if 'TILE_ROWS' not in e['name'] or not e['parts']:continue
 new=[]
 for p in e['parts']:
  g=p['geometry']
  if g['type']!='prism':new.append(p);continue
  v=np.array(g['vector'],float);L=np.linalg.norm(v)
  if L<.055:new.append(p);continue
  axis=v/L;center=np.mean(g['profile'],axis=0);transverse=np.cross(axis,[0,0,1]);transverse/=np.linalg.norm(transverse);up=np.cross(transverse,axis)
  if up[2]<0:up=-up
  # Semicircular hollow section, 12 segments and 8mm shell thickness.
  outer=[center+transverse*(.06*math.cos(a))+up*(.06*math.sin(a)) for a in np.linspace(0,math.pi,13)]
  inner=[center+transverse*(.052*math.cos(a))+up*(.052*math.sin(a)) for a in np.linspace(math.pi,0,13)]
  profile=np.array(outer+inner)
  steps=max(1,math.ceil(L/.32));length=L/steps
  for k in range(steps):
   new.append(part({'type':'prism','profile':(profile+axis*(k*length)).tolist(),'vector':(axis*(length-.003 if steps>1 else length)).tolist()},p['material']));detailcount+=1
 e.update(parts=new,family='ARCH_MODEL',source=e['source']+'; V7 curved individual modules DJI 0002 0038/0429/0478',tile_modules=len(new),tile_profile_status='PHOTO_ESTIMATED_120mm_COVER_WIDTH_8mm_SHELL; NOT_FIELD_MEASURED')
 rownames.append(e['name'])
# Small centre roof has no former tube rows: model individual cover tiles on
# its two slopes. Exact eave/ridge remain those of the existing aligned roof.
small=[]
for sign in [-1,1]:
 v=np.array([sign*3.525,0,-.9]);L=np.linalg.norm(v);axis=v/L;across=np.array([0,1,0]);up=np.cross(axis,across)
 if up[2]<0:up=-up
 for y in np.arange(-.72,2.06,.2):
  center=np.array([6.5,y,8.412]);profile=np.array([center+across*.06*math.cos(a)+up*.06*math.sin(a) for a in np.linspace(0,math.pi,13)]+[center+across*.052*math.cos(a)+up*.052*math.sin(a) for a in np.linspace(math.pi,0,13)])
  steps=math.ceil(L/.32);length=L/steps
  for k in range(steps):small.append(part({'type':'prism','profile':(profile+axis*k*length).tolist(),'vector':(axis*(length-.003)).tolist()},'M_Roof'));detailcount+=1
add('CANOPY_CENTER_INDIVIDUAL_COVER_TILES','50_ROOF',small,['DJI 0002/DJI_0429.JPG','DJI 0003/DJI_0100.JPG'],tile_modules=len(small))
record('V7_INDIVIDUAL_VISIBLE_TILES',rownames+['CANOPY_CENTER_INDIVIDUAL_COVER_TILES'],'已建瓦列细化为独立弧形空心盖瓦，保留现有坡面和瓦列位置',['DJI 0002/DJI_0038.JPG','DJI 0002/DJI_0429.JPG'],module_count=detailcount,profile_status='PHOTO_ESTIMATED; NO_HIDDEN_BRICKS_ASSERTED')
S['v7_changes']=changes;S['status']='V7 user- and photo-supported topology/detail correction. Registered source unchanged outside the missing-area mask. Metric offsets/profiles provisional pending tape survey; not construction certification.'
S['v7_detail_counts']={'curved_cover_tiles':detailcount,'ceramic_wall_tiles':tileswall}
for k in ['cameras']:
 S[k]+=[dict(name='V7_Terrace_Door',position=[-5,2.8,10.7],target=[3.9,7.7,8.8],fov=58),dict(name='V7_Closed_Gable',position=[6.5,-12,9.1],target=[6.5,0,7.7],fov=42)]
(A/'05_Intermediate/Architecture_Scene.json').write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'06_Report/Changes_V7.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
for key,name in [('door_registry','Door_Registry_V7'),('rooms','Room_Registry_V7')]: (O/'06_Report'/f'{name}.json').write_text(json.dumps(S[key],ensure_ascii=False,indent=2),encoding='utf-8')
changed=[e['name'] for e in S['elements'] if e['name'] not in {x['name'] for x in original['elements']} or e!=next(x for x in original['elements'] if x['name']==e['name'])]
removed=[e['name'] for e in original['elements'] if e['name'] not in {x['name'] for x in S['elements']}]
(O/'02_Data/V7_Changed_Nodes.json').write_text(json.dumps({'changed':changed,'removed':removed},indent=2),encoding='utf-8')
print('SCENE V7',len(S['elements']),'elements;',len(changed),'changed;',detailcount,'tile modules;',tileswall,'ceramic units',flush=True)
