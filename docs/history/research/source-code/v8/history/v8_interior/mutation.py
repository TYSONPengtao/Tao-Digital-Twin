"""V8 interior mutation: owned changes only; caller exports whole model.

Coordinates are inherited drawing metres, geometry topology follows the user's
2026-10-09 correction and reviewed panorama. Door offsets remain provisional.
"""
import copy, math, sys, json, hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs','v4_audit_junction']]
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from shapely import affinity
import apply_junction_v4 as J

BASE=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json')
OUT=Path(__file__).parent

def xy_at(e,z):
    return unary_union([Polygon(g['outer'],g['holes']) for p in e['parts']
                        if (g:=p['geometry'])['type']=='prism_holes' and
                        g['z']-1e-8<z<g['z']+g['height']+1e-8])

def mirror_g_y(g,total=17.1):
    g=copy.deepcopy(g);t=g['type']
    if t=='box':g['origin'][1]=total-g['origin'][1]-g['size'][1]
    elif t=='prism':
        for p in g['profile']:p[1]=total-p[1]
        g['vector'][1]*=-1
    elif t=='prism_holes':
        for r in [g['outer']]+g['holes']:
            for p in r:p[1]=total-p[1]
    elif t=='polyhedron':
        for p in g['vertices']:p[1]=total-p[1]
        g['faces']=[list(reversed(f)) for f in g['faces']]
    else:raise ValueError(t)
    return g

def apply(s,stair_bath_origin=None):
    """Apply explicit edits to mutable dict, return records for root's report.

    stair_bath_origin selects the stair-opposite washroom doorway candidate;
    default [9.1,8.6,0] places the washroom door on the wall beyond the
    unframed ascending approach. Axis assignment and exact offsets are
    provisional; panorama establishes the two openings are separate.
    This parameter must be resolved once before production export.
    """
    e={a['name']:a for a in s['elements']};changes=[];old=copy.deepcopy(s)
    # The flight closest to the rear solid wall is the first ascending run.
    # Landing and its front-edge safety rail stay in place. Inboard handrails
    # and return mirror with the flights; shared end post lies on the axis.
    stair_names=[a['name'] for a in s['elements'] if a['name'].startswith('STAIR_F') or
                 a['name'].startswith('STAIR_V4_RAIL_') or a['name'].startswith('STAIR_V4_RETURN_')]
    for n in stair_names:
        for p in e[n]['parts']:p['geometry']=mirror_g_y(p['geometry'])
        e[n].update(source='User 2026-10-09; panorama 115s/125s: ascending run has solid wall on right and handrail on left',
                    status='V8_STAIR_HANDEDNESS_CORRECTED; DRAWING_METRIC_DIMENSIONS_RETAINED')
    changes.append(dict(id='V8_STAIR_ASCENT_RIGHT_WALL',elements=stair_names,
        change='Mirrored both storeys about Y8.55; ascending first run now Y8.56..9.66, right side at rear solid wall, inner guard on left',
        evidence=[str(W/'ue5_panorama_audit/Center_L0_0115s.jpg'),str(W/'ue5_panorama_audit/Center_L0_0125s.jpg'),
                  r'D:\Desktop\新建文件夹\屏幕截图 2026-10-09 001423.jpg'],metric_status='Inherited drawing stair dimensions, not a field survey'))

    # Formal ground floor right washroom remained as drawn. Restore its front
    # doorway and close the provisional V5 side-wall doorway only.
    ops={1:[],2:[]}
    ops[1]+=[(box(10.71,7.2,12.788,7.4),0,3.77,'add'),
             (box(10.71,7.4,10.89,9.588),0,3.77,'add'),
             (box(11.9,7.19,12.7,7.41),0,2.1,'remove')]

    def move_door(id,origin,angle,source):
        reg=next(r for r in s['door_registry'] if r['door_id']==id)
        fr=e[reg['frame_element']];lf=e[reg['leaf_element']]
        fr.update(previous_origin=fr['origin'][:],origin=origin[:],angle=angle,source=source,
                  dimension_confidence='PROVISIONAL_NOT_FIELD_MEASURED',status='V8_USER_CORRECTED_DOOR_TOPOLOGY')
        off=s['definitions'][lf['definition']]['parameters']['Hinge_Surface_Offset']
        hp=[origin[0]+.047*math.cos(angle)-off*math.sin(angle),
            origin[1]+.047*math.sin(angle)+off*math.cos(angle),origin[2]]
        lf.update(previous_origin=lf['origin'][:],origin=hp,angle=angle,pivot_world_m=hp,pivot_local_m=[0,0,0],source=source,
                  dimension_confidence='PROVISIONAL_NOT_FIELD_MEASURED',status='V8_USER_CORRECTED_DOOR_TOPOLOGY')
        reg.update(origin=origin[:],angle=angle,hinge_world_m=hp,source=source,
                   position_status='V8_USER_CONFIRMED_TOPOLOGY; DRAWING_OFFSETS_PROVISIONAL')
        for o in s['openings']:
            if o['name']==id:o.update(origin=origin[:],angle=angle,dimension_status='DRAWING_DIMENSIONS_NOT_FIELD_MEASURED')
        return reg
    move_door('DOOR_BATH_F1_R',[11.9,7.3,0],0,'User 2026-10-09: ground floor right washroom unchanged from D03 floor plan')
    changes.append(dict(id='V8_F1_RIGHT_BATH_RESTORE_PLAN',elements=['PARTITIONS_JOINED_F1','DOOR_BATH_F1_R__FRAME','DOOR_BATH_F1_R__LEAF'],
        change='Restored front-wall washroom opening [11.9,7.3,0], closed X10.8 side opening; preserve video-corrected bedroom access',
        evidence=[r'E:\jz\JIA\Rebuild_V5\02_PDF_Reference\D03.png'],metric_status='User confirmed design layout; dimension inherited from design drawing'))

    # Right second-floor wing is the mirror of the independently modeled left
    # wing. This removes the former narrow front-door residuals while preserving
    # central sealed stair-front wall and main frame/beam volumes.
    f2=e['PARTITIONS_JOINED_F2'];leftmask=box(.212,1.1,4.112,9.588);rightmask=affinity.scale(leftmask,-1,1,origin=(6.5,0))
    cuts=set()
    for p in f2['parts']:
        g=p['geometry'];cuts.update([g['z'],g['z']+g['height']])
    rebuilt=[]
    for a,b in zip(sorted(cuts)[:-1],sorted(cuts)[1:]):
        p=xy_at(f2,(a+b)/2);replacement=affinity.scale(p.intersection(leftmask),-1,1,origin=(6.5,0))
        out=p.difference(rightmask).union(replacement)
        rebuilt+=J._prisms(out,a,b-a,'M_Wall_Interior')
    f2.update(parts=rebuilt,status='V8_RIGHT_WING_MIRRORS_LEFT; V7_CENTRAL_STAIR_FRONT_SEAL_RETAINED',source='User 2026-10-09: F2 right-side layout mirrors left room')
    for lid,rid in [('DOOR_BATH_F2_L','DOOR_BATH_F2_R'),('DOOR_BED_F2_X3.9','DOOR_BED_F2_X9.1')]:
        lr=next(r for r in s['door_registry'] if r['door_id']==lid)
        rr=next(r for r in s['door_registry'] if r['door_id']==rid)
        lf=e[lr['leaf_element']];rf=e[rr['leaf_element']]
        rf['definition']=lf['definition'].replace('_NEG','_TEMP').replace('_POS','_NEG').replace('_TEMP','_POS')
        rf['open_angle_degrees_provisional']=-lf['open_angle_degrees_provisional']
        move_door(rid,[13-lr['origin'][0],lr['origin'][1],lr['origin'][2]],math.pi/2,'User 2026-10-09: F2 right room mirror of left; opposite hinge/swing retained')
    changes.append(dict(id='V8_F2_RIGHT_WING_MIRROR',elements=['PARTITIONS_JOINED_F2','DOOR_BATH_F2_R__FRAME','DOOR_BATH_F2_R__LEAF','DOOR_BED_F2_X9.1__FRAME','DOOR_BED_F2_X9.1__LEAF'],
        change='Rebuilt right wing partitions as X=6.5 mirror of left wing, including rear recess and side bathroom access; mirrored hinge/swing, preserved F2 central sealed wall',
        evidence=[str(W/'v5_video_plan/Wide_L0_0350s_Y-40.jpg'),str(W/'v5_video_plan/Wide_L0_0450s_Y-40.jpg')],metric_status='User-defined mirror topology, drawing dimensions provisional'))

    # Move the former "kitchen" frame/leaf away from the actual stair approach.
    # Panorama L1 115/120s shows a free stair mouth, a short passage and then
    # the more distant frosted washroom door. Place its wall at inherited X9.1,
    # separately from the X7.8 stair mouth. This is a topology-supported
    # candidate, not calibrated camera metric localization.
    bo=stair_bath_origin or [9.1,8.6,0]
    ops[1]+=[(box(7.70,7.5,7.90,9.588),0,3.77,'remove'),
             (box(9.01,8.41,9.19,9.588),0,3.77,'add'),
             (box(9.0,bo[1],9.2,bo[1]+.8),0,2.1,'remove'),
             (box(9.19,8.41,10.71,8.59),0,3.77,'add')]
    move_door('DOOR_KITCHEN_F1',bo,math.pi/2,'User 2026-10-09: no door at ascending stair entry; retained frosted door is opposite-side washroom; exact offset provisional')
    changes.append(dict(id='V8_STAIR_ENTRY_OPEN_OPPOSITE_WASHROOM',elements=['PARTITIONS_JOINED_F1','DOOR_KITCHEN_F1__FRAME','DOOR_KITCHEN_F1__LEAF'],
        change='Removed old stair-entry frame and blocking X7.8 wall at Y8.56..9.588; relocated stable washroom door to more distant opposite wall X9.1/Y8.6 candidate, kept X7.8..9.1 passage open and corrected room zone off stair footprint',
        evidence=[str(W/'ue5_panorama_audit/Center_L0_0115s.jpg'),str(W/'ue5_panorama_audit/Center_L1_0115s.jpg'),str(W/'ue5_panorama_audit/Center_L1_0120s.jpg'),str(W/'ue5_panorama_audit/Center_L0_0505s.jpg')],
        position_basis='User confirmed stair/bath topology and reviewed 115/120s rearward views; X9.1 inherited-grid candidate, exact door offset and compact washroom extent provisional'))
    beams=[J._world_box(a,p) for a in s['elements'] if a['name'].startswith('BEAM_') for p in a['parts']]
    for floor,operations in ops.items():
        if not operations:continue
        host=e['PARTITIONS_JOINED_F'+str(floor)];parts=host['parts'];cuts=set()
        for p in parts:g=p['geometry'];cuts.update([g['z'],g['z']+g['height']])
        for _,a,b,_ in operations:cuts.update([a,b])
        for _,a,b in beams:
            if min(cuts)<a<max(cuts):cuts.add(a)
            if min(cuts)<b<max(cuts):cuts.add(b)
        rebuilt=[]
        for a,b in zip(sorted(cuts)[:-1],sorted(cuts)[1:]):
            if b-a<1e-7:continue
            mid=(a+b)/2;p=xy_at(host,mid)
            for q,lo,hi,op in operations:
                if lo-1e-8<mid<hi-1e-8:p=p.union(q) if op=='add' else p.difference(q)
            cut=[q for q,lo,hi in beams if lo-1e-8<mid<hi-1e-8]
            if cut:p=p.difference(unary_union(cut))
            rebuilt+=J._prisms(p,a,b-a,'M_Wall_Interior')
        host['parts']=rebuilt;host['v8_patch_operations']=[dict(xy=list(q.bounds),z=[a,b],operation=op) for q,a,b,op in operations]
    for r in s['rooms']:
        if r['room_id']=='F1-R07':
            r.update(label='楼梯对面洗手间（保留旧门ID）',use='STAIR_OPPOSITE_WASHROOM',review_polygon_xy_m=[[9.2,8.6],[10.7,8.6],[10.7,9.6],[9.2,9.6]],boundary_status='Opposite-door candidate review zone at inherited drawing-grid X9.1; actual offsets, extent and room boundary require tape measurement')
        if r['room_id']=='F1-R03':
            pp=Polygon(r['review_polygon_xy_m']).difference(box(9.19,8.41,10.71,9.7))
            r['review_polygon_xy_m']=[list(p) for p in list(pp.exterior.coords)[:-1]]
            r['boundary_status']='Bedroom review zone excludes separate provisional stair-opposite washroom; original right washroom remains as drawn'
        if r['room_id']=='F2-R03':
            source=next(x for x in s['rooms'] if x['room_id']=='F2-R02')
            r.update(review_polygon_xy_m=[[13-x,y] for x,y in source['review_polygon_xy_m']],boundary_status='User-corrected mirror of F2 left room, drawing-grid zone provisional')
        if r['room_id']=='F2-R05':
            source=next(x for x in s['rooms'] if x['room_id']=='F2-R04')
            r.update(review_polygon_xy_m=[[13-x,y] for x,y in source['review_polygon_xy_m']],boundary_status='User-corrected mirror of F2 left wet room, drawing-grid zone provisional')
    # Queries must not claim overlapping room polygons; split circulation from
    # the compact opposite washroom review zone.
    bath=Polygon(next(r['review_polygon_xy_m'] for r in s['rooms'] if r['room_id']=='F1-R07'))
    for r in s['rooms']:
        if r['room_id']=='F1-R06':
            pp=Polygon(r['review_polygon_xy_m']).difference(bath)
            r['review_polygon_xy_m']=[list(p) for p in list(pp.exterior.coords)[:-1]]
            r['boundary_status']='Circulation review zone excludes washroom candidate; not surveyed room area'
    s['v8_interior_changes']=changes
    return changes

def validate(s,base):
    e={a['name']:a for a in s['elements']};checks=[]
    def ck(id,ok,**info):
        checks.append(dict(id=id,pass_=bool(ok),**info))
        assert ok,(id,info)
    for f in [1,2]:
        g=e[f'STAIR_F{f}_FLIGHT1']['parts'][0]['geometry'];yy=[p[1] for p in g['profile']]
        low=min(min(yy),min(yy)+g['vector'][1]);hi=max(max(yy),max(yy)+g['vector'][1])
        ck('First_run_right_rear_wall_F'+str(f),abs(low-8.56)<1e-7 and abs(hi-9.66)<1e-7,bounds_y=[low,hi])
        g2=e[f'STAIR_F{f}_FLIGHT2']['parts'][0]['geometry'];ck('Second_run_front_side_F'+str(f),abs(min(p[1] for p in g2['profile'])+min(0,g2['vector'][1])-7.44)<1e-7)
    for r in s['door_registry']:
        if r.get('leaf_element'):
            fr=e[r['frame_element']];lf=e[r['leaf_element']];hp=lf['origin']
            ck('Registry_hinge_'+r['door_id'],math.dist(hp,r['hinge_world_m'])<1e-9 and math.dist(hp,lf['pivot_world_m'])<1e-9)
    ck('F1_right_bath_front_door',next(r['origin'] for r in s['door_registry'] if r['door_id']=='DOOR_BATH_F1_R')==[11.9,7.3,0])
    q1=xy_at(e['PARTITIONS_JOINED_F1'],1.0)
    ck('F1_right_side_bath_hole_closed',q1.covers(Point(10.8,8.0)))
    ck('F1_right_front_bath_hole_open',not q1.intersects(box(11.95,7.22,12.65,7.38)))
    ck('Unframed_first_stair_entry_open',not q1.intersects(box(7.71,8.6,7.89,9.5)))
    ck('Stair_approach_passage_open',not q1.intersects(box(7.9,8.65,9.0,9.35)))
    ck('Opposite_washroom_new_door_open',not q1.intersects(box(9.02,8.65,9.18,9.35)))
    ck('Opposite_door_is_beyond_entry',next(r['origin'] for r in s['door_registry'] if r['door_id']=='DOOR_KITCHEN_F1')==[9.1,8.6,0])
    q2=xy_at(e['PARTITIONS_JOINED_F2'],4.9);mask=box(.212,1.1,4.112,9.588);rm=affinity.scale(mask,-1,1,origin=(6.5,0))
    err=affinity.scale(q2.intersection(mask),-1,1,origin=(6.5,0)).symmetric_difference(q2.intersection(rm)).area
    ck('F2_right_partitions_mirror_left',err<1e-8,area_error_m2=err)
    ck('F2_sealed_stair_front_unchanged',q2.covers(box(4.12,7.21,7.79,7.39)))
    f3=next(x for x in base['elements'] if x['name']=='PARTITIONS_JOINED_F3')
    ck('F3_user_corrected_walls_unchanged',e['PARTITIONS_JOINED_F3']==f3)
    bath=Polygon(next(r['review_polygon_xy_m'] for r in s['rooms'] if r['room_id']=='F1-R07'))
    ck('Bath_room_registry_off_stairs',bath.intersection(box(3.9,7.4,7.8,9.7)).area==0)
    ck('Bath_circulation_registry_disjoint',bath.intersection(Polygon(next(r['review_polygon_xy_m'] for r in s['rooms'] if r['room_id']=='F1-R06'))).area<1e-9)
    ck('Bath_original_right_registry_disjoint',bath.intersection(Polygon(next(r['review_polygon_xy_m'] for r in s['rooms'] if r['room_id']=='F1-R05'))).area<1e-9)
    ck('Bath_bedroom_registry_disjoint',bath.intersection(Polygon(next(r['review_polygon_xy_m'] for r in s['rooms'] if r['room_id']=='F1-R03'))).area<1e-9)
    for floor,zz in [(1,0),(2,3.9)]:
        for hh in [.4,1.1,1.9]:
            pp=xy_at(e['PARTITIONS_JOINED_F'+str(floor)],zz+hh)
            ck(f'First_run_approach_clear_F{floor}_height{hh}',not pp.intersects(box(7.8,8.65,8.99,9.35)))
        arrival=e['PARTITIONS_JOINED_F'+str(floor+1)]
        ck(f'Second_run_arrival_clear_F{floor+1}',not xy_at(arrival,[3.9,7.5][floor-1]+1).intersects(box(7.8,7.55,8.99,8.35)))
    # Bathroom metadata may not overlap any independently identified wet room.
    for r in s['rooms']:
        if r['floor']==1 and r['room_id']!='F1-R07' and r['use']=='WET_ROOM':
            ck('Separate_stair_washroom_from_'+r['room_id'],bath.intersection(Polygon(r['review_polygon_xy_m'])).area<1e-9)
    return dict(status='PASS',checks=checks,limits=['Door offset and compact opposite washroom boundary remain candidate dimensions.','Rhino native kernel QA and full hybrid export handled by root.'])

if __name__=='__main__':
    s=json.loads(BASE.read_text(encoding='utf8'));b=copy.deepcopy(s);apply(s);qa=validate(s,b)
    previous={a['name']:a for a in b['elements']};changed=[a for a in s['elements'] if previous.get(a['name'])!=a]
    patch=dict(elements=changed,definitions={k:v for k,v in s['definitions'].items() if b['definitions'].get(k)!=v},
               door_registry=s['door_registry'],openings=s['openings'],rooms=s['rooms'],room_connectivity=s['room_connectivity'],v8_interior_changes=s['v8_interior_changes'])
    OUT.mkdir(exist_ok=True)
    (OUT/'Interior_Patch_V8.json').write_text(json.dumps(patch,ensure_ascii=False,indent=2),encoding='utf8')
    (OUT/'Interior_QA_V8.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
    (OUT/'Interior_Review_Scene.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(dict(changed=[a['name'] for a in changed],qa=qa['status'],checks=len(qa['checks'])),ensure_ascii=False))
