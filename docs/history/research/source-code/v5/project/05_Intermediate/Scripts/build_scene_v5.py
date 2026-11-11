"""Video-supported local interior revision; no source survey claim."""
import sys,json,math,copy,hashlib,csv,shutil,re
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W/'v4_audit_junction')]
from shapely.geometry import Polygon,box as rect
from shapely.ops import unary_union
import apply_junction_v4 as J
BASE=Path(r'E:\jz\JIA\Rebuild_V4');OUT=Path(r'E:\jz\JIA\Rebuild_V5')
for d in ['01_Source','02_PDF_Reference','03_Insta360_Frames','04_ContextCapture','05_Intermediate','06_Rhino','07_SketchUp','08_Export','09_Report','10_DJI_Reference','11_Construction_Reference','12_Video_Layout_Evidence']:(OUT/d).mkdir(parents=True,exist_ok=True)
for d in ['01_Source','02_PDF_Reference','04_ContextCapture','10_DJI_Reference','11_Construction_Reference']:
 shutil.copytree(BASE/d,OUT/d,dirs_exist_ok=True)
source=BASE/'05_Intermediate/Architecture_Scene.json';S=json.loads(source.read_text(encoding='utf-8'));B=copy.deepcopy(S);E={e['name']:e for e in S['elements']};changes=[];patches={1:[],2:[],3:[]}
def evidence(times):return {'file':r'E:\jz\VID_20260507_152114_00_001.insv','seconds':times,'acquisition_date':'2026-05-07','projection':'Uncalibrated dual-fisheye qualitative perspective','metric_survey':False}
def record(id,names,details,times,**kw):changes.append(dict(id=id,elements=names,change=details,evidence=evidence(times),position_basis='Video topology and front/back placement; drawing grid used only for provisional dimensions',**kw))
def patch(f,p,zlo,zhi,op):patches[f].append((p,zlo,zhi,op))
def move(name,new,times,f):
 e=E[name];old=e['origin'][:];w=S['definitions'][e['definition']]['parameters']['Width'];z=old[2]
 if abs(e['angle']-math.pi/2)<1e-5:
  close=rect(old[0]-.1,old[1],old[0]+.1,old[1]+w);hole=rect(new[0]-.1,new[1],new[0]+.1,new[1]+w)
 else:
  close=rect(old[0],old[1]-.1,old[0]+w,old[1]+.1);hole=rect(new[0]-.09,new[1],new[0]+.09,new[1]+w)
 patch(f,close,z,z+2.1,'add');patch(f,hole,z,z+2.1,'remove')
 e.update(origin=new,angle=math.pi/2,source='Panorama '+','.join(map(str,times))+'s; retained drawing size is provisional',confidence='MEDIUM',dimension_confidence='PROVISIONAL_NOT_MEASURED',status='VIDEO_TOPOLOGY_CORRECTED; METRIC_POSITION_PROVISIONAL',video_evidence=evidence(times),previous_origin=old,position_candidate_y_range=([2.30,3.50] if f<3 and 'BED' in name else [7.50,8.50]))
 record('V5_MOVE_'+name,[name,'PARTITIONS_JOINED_F'+str(f)],'Closed old door hole and reopened on the video-supported room access side',times,old_origin=old,new_origin=new,nominal_width_m=w,nominal_height_m=2.1)
for f,z,t in [(1,0,[510,515,525,590]),(2,3.9,[315,325,375,485,490])]:
 for x in [3.9,9.1]:move(f'DOOR_BED_F{f}_X{x}',[x,2.4,z],t,f)
move('DOOR_BED_F3_X9.1',[9.1,7.55,7.5],[160,232,237,265,268],3)
patch(3,rect(9.0,7.1,9.2,9.588),7.5,10.67,'add')
# Re-apply the new hole after adding the rear platform boundary.
patch(3,rect(9.0,7.55,9.2,8.45),7.5,9.6,'remove')
record('V5_F3_PLATFORM_WALL',['PARTITIONS_JOINED_F3','DOOR_BED_F3_X9.1'],'Extended right-side platform enclosure behind grid Y7.3, with separate red wood door into the right sleeping room',[160,232,237,265],boundary_xy=[9.0,7.1,9.2,9.588],dimension_status='Drawing grid retained, not a measured as-built wall length')
# The ground-floor right wet room now uses the same side-wall route seen in the video, independently identified for F1.
move('DOOR_BACKROOM_F1_R',[10.8,7.65,0],[570,575,580,588],1)
e=E['DOOR_BACKROOM_F1_R'];e['previous_name']=e['name'];e['name']='DOOR_BATH_F1_R';E[e['name']]=e;E.pop('DOOR_BACKROOM_F1_R')
for f,z,t in [(1,0,[530,550,570,580]),(2,3.9,[338,350,355,410,440,455]),(3,7.5,[235,237,255,265])]:
 patch(f,rect(9.3,7.2,10.71,7.4),z,[3.77,7.37,10.67][f-1],'remove')
 record(f'V5_PASSAGE_F{f}',['PARTITIONS_JOINED_F'+str(f)],'Removed the false cross-wall over the right sleeping-room rear recess; retained the bathroom front wall and its side boundary',t,removed_xy=[9.3,7.2,10.71,7.4],clearance_basis='Model grid only; passage presence supported by uninterrupted video movement')
oldwindow=copy.deepcopy(E['WINDOW_STUDY_C3620_F3']);S['retired_design_elements']=[oldwindow]
S['elements'].remove(E['WINDOW_STUDY_C3620_F3']);E.pop('WINDOW_STUDY_C3620_F3')
patch(3,rect(4.1,7.2,7.7,7.4),8.4,10.35,'add')
record('V5_CLOSE_DESIGN_STUDY_WINDOW',['PARTITIONS_JOINED_F3','WINDOW_STUDY_C3620_F3'],'Retired drawing-only 3.6m indoor window and filled its hole: video platform wall is opaque and has a light wood bedroom door',[158,160,162,210,228,265],closed_xy=[4.1,7.2,7.7,7.4],closed_z=[8.4,10.35])
E['DOOR_STUDY_F3'].update(source='Panorama 210/212/215/218/223/228s: light wood door to central sleeping room',video_evidence=evidence([210,212,215,218,223,228]),status='VIDEO_CONFIRMED_ROOM_CONNECTION; POSITION_AND_SIZE_PROVISIONAL',dimension_confidence='PROVISIONAL_NOT_MEASURED',room_use='SLEEPING_ROOM_NOT_DESIGN_STUDY')
E['DOOR_KITCHEN_F1'].update(source='Panorama 100/110/505s: stair-adjacent washroom, red frosted door; retained drawing position provisional',video_evidence=evidence([100,110,505]),status='VIDEO_CONFIRMED_STAIR_WASHROOM_USE; POSITION_PROVISIONAL',dimension_confidence='PROVISIONAL_NOT_MEASURED',room_use='WASHROOM_NOT_DESIGN_KITCHEN')
record('V5_F1_STAIR_WASHROOM',['DOOR_KITCHEN_F1'],'Corrected drawing kitchen use to a stair-adjacent washroom; retained stable legacy door ID and provisional location',[100,110,505])
# Rebuild only affected partitions, preserve all original elevation breakpoints,
# and always subtract the unchanged reinforced-concrete beam cores.
beams=[J._world_box(e,p) for e in S['elements'] if e['name'].startswith('BEAM_') for p in e['parts']]
for f,ops in patches.items():
 e=E['PARTITIONS_JOINED_F'+str(f)];old=e['parts'];cuts=set()
 for p in old:g=p['geometry'];cuts.update([g['z'],g['z']+g['height']])
 for _,a,b,_ in ops:cuts.update([a,b])
 for _,a,b in beams:
  if min(cuts)<a<max(cuts):cuts.add(a)
  if min(cuts)<b<max(cuts):cuts.add(b)
 rebuilt=[]
 for a,b in zip(sorted(cuts)[:-1],sorted(cuts)[1:]):
  if b-a<1e-7:continue
  mid=(a+b)/2;polys=[Polygon(g['outer'],g['holes']) for p in old if (g:=p['geometry'])['z']-1e-8<mid<g['z']+g['height']+1e-8]
  p=unary_union(polys)
  for q,lo,hi,op in ops:
   if lo-1e-8<mid<hi-1e-8:p=p.union(q) if op=='add' else p.difference(q)
  cutters=[q for q,lo,hi in beams if lo-1e-8<mid<hi-1e-8]
  if cutters:p=p.difference(unary_union(cutters))
  rebuilt+=J._prisms(p,a,b-a,'M_Wall_Interior')
 e.update(parts=rebuilt,source='V5 per-floor video topology; V4 beam interfaces retained',status='VIDEO_LAYOUT_REVISION; DRAWING_GRID_DIMENSIONS_PROVISIONAL',video_patch_operations=[dict(xy=list(q.bounds),z=[a,b],operation=op) for q,a,b,op in ops])

# Separate actual geometry origins for hinges: frame stays at opening start;
# leaf block origin is the hinge, with local vertices measured from that hinge.
S['materials']['M_Honey_Door_Wood']={'color':[155,101,53],'roughness':.43}
S['materials']['M_Door_Panel_Wood']={'color':[124,60,32],'roughness':.44}
def pbox(x,y,z,w,d,h,m):return J._part(J._box(x,y,z,w,d,h),m)
for width in [.8,.9]:
 k=f'DOOR_W{round(width*1000)}_H2100_WOOD';d=S['definitions'][k];d['parts']=d['parts'][1:];d['parameters'].update(Role='FRAME',Nominal_Opening_Width=width,Clear_Frame_Width=width-.09,Clear_Frame_Height=2.055);d['source']='Retained drawing frame geometry; separated from hinged leaf for V5'
for name,w,m,glass in [('WOOD900_RED',.9,'M_Wood',False),('WOOD900_HONEY',.9,'M_Honey_Door_Wood',False),('WOOD800_RED',.8,'M_Wood',False),('FROSTED800_RED',.8,'MAT_DOOR_FRAME_RED',True)]:
 width=w-.094;h=2.035;pieces=[]
 if glass:
  r=.038;pieces=[pbox(0,-.025,.01,r,.05,h,m),pbox(width-r,-.025,.01,r,.05,h,m),pbox(r,-.025,.01,width-2*r,.05,r,m),pbox(r,-.025,h+.01-r,width-2*r,.05,r,m)]
  bands=[.01+r,.70,1.35,h+.01-r]
  for zz in bands[1:-1]:pieces.append(pbox(r,-.025,zz-.015,width-2*r,.05,.03,m))
  for a,b in zip(bands[:-1],bands[1:]):
   lo=a+(.015 if a!=bands[0] else 0);hi=b-(.015 if b!=bands[-1] else 0)
   pieces.append(pbox(r,-.003,lo,width-2*r,.006,hi-lo,'M_Glass_Frosted'))
 else:
  pieces=[pbox(0,-.024,.01,width,.048,h,m)]
  # Two visible raised fields, touching rather than embedded in the base slab.
  for z,hh in [(.18,.56),(.90,.93)]:
   pieces.append(pbox(.10,-.029,z,width-.20,.005,hh,m))
   pieces.append(pbox(.10,.024,z,width-.20,.005,hh,m))
 k='V5_LEAF_'+name;S['definitions'][k]={'parts':pieces,'parameters':dict(Role='LEAF',Width=width,Height=h,Hinge_Local=[0,0,0],Gap=0.002,Geometry_Origin='Actual hinge axis at local X=0',Dimensions_Status='Provisional drawing width and visually estimated profiles'),'source':'Video material/type, profile dimensions estimated','confidence':'MEDIUM'}
# Glass frames have the same retained nominal rough location, red colour observed in video.
S['definitions']['V5_FRAME_FROSTED800_RED']=copy.deepcopy(S['definitions']['DOOR_W800_H2100_WOOD'])
for p in S['definitions']['V5_FRAME_FROSTED800_RED']['parts']:p['material']='MAT_DOOR_FRAME_RED'
registry=[];doors=[e for e in S['elements'] if e['layer']=='30_DOOR'];new=[]
for e in doors:
 id=e['name'];f=int(re.search(r'_F([123])',id)[1]);defn=e['definition'];w=S['definitions'][defn]['parameters']['Width'];reg=dict(door_id=id,previous_id=e.get('previous_name',id),floor=f,origin=e['origin'][:],angle=e.get('angle',0),nominal_opening_width_m=w,nominal_opening_height_m=2.1,clear_frame_width_m=(w-.09 if w<2 else w-.12),dimensions_status='PROVISIONAL_DRAWING_SCALE_NOT_FIELD_MEASURED',evidence=e.get('video_evidence'),position_status=e.get('status','DRAWING_POSITION_UNCONFIRMED'),source=e['source'])
 if w<2:
  glass=id in ['DOOR_BATH_F1_L','DOOR_BATH_F1_R','DOOR_BATH_F2_L','DOOR_BATH_F2_R','DOOR_KITCHEN_F1'];honey=id=='DOOR_STUDY_F3';leafdef='V5_LEAF_'+('FROSTED800_RED' if glass else 'WOOD900_HONEY' if honey else 'WOOD900_RED' if w>.85 else 'WOOD800_RED')
  frame=copy.deepcopy(e);frame.update(name=id+'__FRAME',parent_id=id,door_id=id,role='FRAME')
  if glass:frame['definition']='V5_FRAME_FROSTED800_RED'
  if honey:
   hk='V5_FRAME_WOOD900_HONEY';S['definitions'][hk]=copy.deepcopy(S['definitions']['DOOR_W900_H2100_WOOD'])
   for p in S['definitions'][hk]['parts']:p['material']='M_Honey_Door_Wood'
   frame['definition']=hk
  leaf=copy.deepcopy(e);a=e.get('angle',0);swing=(-90 if 'X9.1' in id or 'BATH_F' in id and id.endswith('_L') else 90)
  # Put the axis on the opening-side leaf surface, clear of the fixed jamb.
  # Rebase vertices and the instance together; closed world geometry is invariant.
  off=(.025 if glass else .029)*(1 if swing>0 else -1);variant=leafdef+('_POS' if swing>0 else '_NEG')
  if variant not in S['definitions']:
   S['definitions'][variant]=copy.deepcopy(S['definitions'][leafdef])
   for p in S['definitions'][variant]['parts']:p['geometry']['origin'][1]-=off
   S['definitions'][variant]['parameters'].update(Hinge_Surface_Offset=off,Opening_Sign=1 if swing>0 else -1)
  hinge=[e['origin'][0]+.047*math.cos(a)-off*math.sin(a),e['origin'][1]+.047*math.sin(a)+off*math.cos(a),e['origin'][2]]
  leaf.update(name=id+'__LEAF',parent_id=id,door_id=id,role='LEAF',definition=variant,origin=hinge,pivot_world_m=hinge,pivot_local_m=[0,0,0],open_angle_degrees_provisional=swing,interaction='HINGED_LEAF',swing_status='Model interaction direction proposed; hinge handedness requires confirmation')
  new.extend([frame,leaf]);reg.update(frame_element=frame['name'],leaf_element=leaf['name'],hinge_world_m=hinge,interaction='HINGED',type_status=('VIDEO_SUPPORTED_FROSTED_GLASS' if glass else 'VIDEO_SUPPORTED_LIGHT_WOOD' if honey else 'WOOD_TYPE_RETAINED; REVIEW_EVIDENCE'),opening_handedness='PROVISIONAL')
  if glass:record('V5_GLASS_'+id,[frame['name'],leaf['name']],'Replaced opaque wood wet-room leaf with red-frame frosted glazing, separate from its fixed jambs',([100,110,505] if id=='DOOR_KITCHEN_F1' else [550] if id=='DOOR_BATH_F1_L' else [570,580] if f==1 else [350] if id.endswith('_L') else [440,450,455]),type_confidence='Video supported, side assignments and metric positions provisional')
 else:
  new.append(e);reg.update(frame_element=id,leaf_element=None,interaction='FRONT_GLAZING_ASSEMBLY_REQUIRES_PANEL_TYPE_CONFIRMATION')
 registry.append(reg)
S['elements']=[e for e in S['elements'] if e not in doors]+new
S['door_registry']=registry
S['openings']=[o for o in S['openings'] if o['type']!='door' and o['name']!='WINDOW_STUDY_C3620_F3']+[dict(name=r['door_id'],type='door',W=r['nominal_opening_width_m'],H=r['nominal_opening_height_m'],origin=r['origin'],angle=r['angle'],frame_element=r['frame_element'],leaf_element=r['leaf_element'],clear_frame_width_m=r['clear_frame_width_m'],dimension_status=r['dimensions_status']) for r in registry]
# Room query records follow the actual observed connections, each floor owns
# its records. Their polygons are review zones rather than surveyed boundaries.
rooms=[]
def room(f,id,label,xy,use,t):rooms.append(dict(room_id=f'F{f}-R{id:02}',floor=f,label=label,use=use,review_polygon_xy_m=[list(p) for p in list(xy.exterior.coords)[:-1]],floor_z_m=[0,3.9,7.5][f-1],boundary_status='Provisional drawing-grid review zone, not measured room area',evidence=evidence(t),door_ids=[]))
for f in [1,2]:
 room(f,1,'一层起居厅／入口' if f==1 else '二层起居厅',rect(4,2.2,9,7.2),'LIVING',[510,515] if f==1 else [315,325,485])
 room(f,2,'左翼睡眠房及后凹段',rect(.2,2.2,3.8,9.6).difference(rect(.2,7.2,2.3,9.6)),'SLEEPING',[525,550] if f==1 else [338,350,355])
 room(f,3,'右翼睡眠房及后凹段',rect(9.2,2.2,12.8,9.6).difference(rect(10.7,7.2,12.8,9.6)),'SLEEPING',[570,580,588] if f==1 else [410,440,455])
 room(f,4,'左侧湿区',rect(.2,7.4,2.1,9.6),'WET_ROOM',[100,110,550] if f==1 else [350])
 room(f,5,'右侧湿区',rect(10.9,7.4,12.8,9.6),'WET_ROOM',[580] if f==1 else [450,455])
 room(f,6,'楼梯平台与后部通道',rect(4.0,7.4,9.0,9.6),'STAIR_CIRCULATION',[115,130] if f==1 else [275,300,495])
room(1,7,'楼梯旁洗手间（原图厨房）',rect(4.1,7.4,7.7,9.6),'STair_ADJACENT_WASHROOM_BOUNDARY_UNCONFIRMED',[100,110,505])
rooms[-1]['boundary_status']='Review zone overlaps stair projection; under-stair relationship and actual washroom extent require verification, not a measured footprint'
room(3,1,'中心睡眠房（原图书房）',rect(4,2.2,9,7.2),'SLEEPING',[210,215,218,223])
room(3,2,'右翼多床房及后凹段',rect(9.2,2.2,12.8,9.6).difference(rect(10.7,7.2,12.8,9.6)),'SLEEPING',[232,235,237,255,265])
room(3,3,'三层楼梯平台',rect(4,7.4,9,9.6),'STAIR_CIRCULATION',[158,160,162,228,265])
room(3,4,'西侧有金属雨棚露台',rect(.2,1.2,3.8,7.1),'TERRACE',[165,180,200,205])
room(3,5,'设计右湿区／视频覆盖未确认',rect(10.9,7.4,12.8,9.6),'UNCONFIRMED_WET_ROOM',[])
room(3,6,'设计西后部洗衣间／待核对',rect(.2,7.4,3.7,9.6),'UNCONFIRMED_UTILITY',[])
connections={}
for f in [1,2]:
 for x,r in [(3.9,2),(9.1,3)]:connections[f'DOOR_BED_F{f}_X{x}']=[f'F{f}-R01',f'F{f}-R{r:02}']
 for side,a,b in [('L',2,4),('R',3,5)]:connections[f'DOOR_BATH_F{f}_{side}']=[f'F{f}-R{a:02}',f'F{f}-R{b:02}']
connections.update({'DOOR_BED_F3_X9.1':['F3-R03','F3-R02'],'DOOR_STUDY_F3':['F3-R03','F3-R01'],'DOOR_BATH_F3_R':['F3-R02','F3-R05'],'DOOR_LAUNDRY_F3':['F3-R04','F3-R06']})
connections['DOOR_KITCHEN_F1']=['F1-R06','F1-R07']
for r in registry:
 r['connected_rooms']=connections.get(r['door_id'],[])
 for rr in rooms:
  if rr['room_id'] in r['connected_rooms']:rr['door_ids'].append(r['door_id'])
S['rooms']=rooms;S['room_connectivity']=connections;S['v5_video_changes']=changes
S['status']='V5 video-supported interior topology revision, provisional drawing dimensions; V4 construction coordination proposals retained and separately identified. Not a surveyed construction/as-built certification.'
S['video_revision']={'source':evidence([100,610]),'floor_assignment':'F1/F2/F3 derived by continuous two stair ascents/descent and exterior window/balcony alignment','known_uncertainties':['Exact door offsets/clear sizes and wall thickness need tape measurement','Hinge handedness and opening travel provisional','F3 right wet room and west rear laundry not covered sufficiently','F1 stair-adjacent washroom exact extent/door offset retained provisionally','Front glass panel type/opening mechanism remains to verify'],'retained_construction_proposals':'V4 fields and CONSTRUCTION_* remain coordination proposals, not asserted existing finishes'}
base_hashes={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,BASE/'06_Rhino/Production_1QK_Rebuild.3dm',BASE/'07_SketchUp/Production_1QK_Rebuild.skp']}
(OUT/'09_Report/V4_Baseline_SHA256.json').write_text(json.dumps(base_hashes,indent=2),encoding='utf-8')
(OUT/'05_Intermediate/Architecture_Scene.json').write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'09_Report/Video_Changes_V5.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'09_Report/Door_Registry_V5.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'09_Report/Room_Registry_V5.json').write_text(json.dumps(rooms,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'09_Report/Door_Changes_V5.csv').open('w',encoding='utf-8-sig',newline='') as f:
 keys=['door_id','previous_id','floor','origin','nominal_opening_width_m','clear_frame_width_m','frame_element','leaf_element','hinge_world_m','connected_rooms','dimensions_status','position_status','interaction'];wr=csv.DictWriter(f,keys,extrasaction='ignore');wr.writeheader();wr.writerows(registry)
print('V5 source built:',len(S['elements']),'elements,',len(changes),'changes,',len(rooms),'review room records',flush=True)
