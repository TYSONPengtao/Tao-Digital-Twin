"""Visible DNG-backed bare brick finish and 90 degree stone course.

No kitchen roof/wall core, full peripheral wall, or buried strength is changed.
"""
import sys,json,math,copy,hashlib,ast
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon,Point,box
import export_v5 as ex
O=Path(__file__).parent;SP=Path(r'E:/jz/JIA/Rebuild_V10_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json');S=json.loads(SP.read_bytes());E={e['name']:e for e in S['elements']};REF=['D:/Desktop/DJI_0511.DNG','D:/Desktop/DJI_0513.DNG','D:/Desktop/屏幕截图 2026-10-09 120147.jpg']
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'));func=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold','fromman']];exec(compile(ast.Module(func,type_ignores=[]),'<geometry_helpers>','exec'))
parts=[];mortar=[];cap=[];checks=[]
def part(g,m):return dict(geometry=g,material=m)
def check(name,ok,**info):
    checks.append(dict(name=name,passed=bool(ok),**info))
    if not ok:raise ValueError((name,info))
def polybox(x0,x1,y0,y1,z0,z1):
    return oriented(dict(type='polyhedron',vertices=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]],faces=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]))
def east_top(y):
    return 3.365916710451+(3.3935174013608-3.365916710451)*(y+11.65)/8.83
# North gable top directly reuses the current fitted roof-compatible profile.
v=np.asarray(E['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES']['parts'][1]['geometry']['vertices'])
vt=v[(abs(v[:,1]+2.6)<1e-8)&(v[:,2]>0)];xs=vt[:,0];zs=vt[:,2]
def north_top(x):return float(np.interp(x,xs,zs))
def profile_solid(face,s0,s1,depth0,depth1,z0,ztop):
    stations=[float(s0),float(s1)]
    if face=='north':stations=sorted(set(stations+[float(x) for x in xs if s0<x<s1]))
    profile=[[q,z0] for q in stations]+[[q,ztop(q)] for q in stations[::-1]]
    if min(ztop(q) for q in stations)<=z0:return None
    vertices=[]
    for d in [depth0,depth1]:
        for s,z in profile:vertices.append([13.35+d,s,z] if face=='east' else [s,-2.60+d,z])
    k=len(profile);fs=[list(range(k-1,-1,-1)),list(range(k,2*k))]+[[i,(i+1)%k,(i+1)%k+k,i+k] for i in range(k)]
    return oriented(dict(type='polyhedron',vertices=vertices,faces=fs))
roof=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in E['SITE_KITCHEN_CHINESE_TILE_ROOF']['parts']],mf.OpType.Add)
def roof_trim(g):
    if g is None:return None
    a=manifold(g);intr=(a^roof).volume()
    if intr>1e-12:
        r=a-roof;return None if r.is_empty() else fromman(r)
    return g
for face,s0,s1,fn in [('east',-11.65,-2.6,east_top),('north',7.7,13.365,north_top)]:
    backing=roof_trim(profile_solid(face,s0,s1,0,.003,-.4,lambda s:fn(s)-.010))
    mortar.append(part(backing,'M_V11_Kitchen_Brick_Joints'))
    for row in range(math.ceil((max(fn(s0),fn(s1),max(zs))+.4)/.065)):
        z0=-.4+row*.065+.004;z1=z0+.055;offset=.12 if row%2 else 0
        for ss in np.arange(s0-offset,s1,.24):
            a=max(s0,float(ss+.004));b=min(s1,float(ss+.236))
            if b-a<.025:continue
            top=min(fn(a),fn(b))-.014
            if top<=z0+.010:continue
            zz=min(z1,top)
            g=polybox(13.353,13.365,a,b,z0,zz) if face=='east' else polybox(a,b,-2.597,-2.585,z0,zz)
            g=roof_trim(g)
            if g is not None:parts.append(part(g,'M_Grey_Brick'))
    # Only the exposed transition course is modeled: 200 mm reference height.
    # Full foundation depth/stone coordinates remain provided by intact scans.
    for ss in np.arange(s0,s1,.6):
        a=float(ss);b=min(float(ss+.6),s1)
        g=polybox(13.13,13.365,a,b,-.6,-.4) if face=='east' else polybox(a,b,-2.82,-2.585,-.6,-.4)
        # North run reaches X13.365; east run ends exactly Y-2.60, so no solid overlap.
        if face=='north' and b>13.13:
            g=polybox(a,b,-2.60,-2.585,-.6,-.4)
        cap.append(part(g,'M_Stone_Frame'))
add=[]
for name,pp,cls in [('SITE_KITCHEN_V11_VISIBLE_BARE_GRAY_BRICK_UNITS',parts,'INDIVIDUAL_BARE_GRAY_BRICK_EXTERIOR_FINISH'),('SITE_KITCHEN_V11_VISIBLE_GRAY_MORTAR_BACKING',mortar,'VISIBLE_BRICK_JOINT_FACE'),('SITE_KITCHEN_V11_STONE_TO_BRICK_TRANSITION_COURSE',cap,'L_JOINED_VISIBLE_STONE_TRANSITION_COURSE')]:
    add.append(dict(name=name,parts=pp,layer='60_SITE',family='SITE_MODEL',confidence='MEDIUM',classification=cls,source='; '.join(REF),status='V11_DNG_RELATION_CONFIRMED; FACE_SIZE_REFERENCE_FIT_NOT_FIELD_MEASURED',wall_core_and_roof_unchanged=True,corner_angle_degrees=90.,full_foundation_and_actual_stone_coordinates_not_invented=True,stone_course_reference_height_m=.2 if 'STONE' in name else None,finish_thickness_m=.015))
M=dict(replace=[],add=add,remove=[],definitions={},materials={'M_V11_Kitchen_Brick_Joints':dict(color=[157,160,155],roughness=.96,role='Photo-observed gray mortar, reference appearance')},changes=[dict(id='V11_KITCHEN_VISIBLE_L_INTERFACE',description='DJI_0511/0513确认厨房外侧为裸灰砖与石基，新增拟合到现有L墙的逐件灰砖薄饰面和可见石基过渡带，保留现有厨房实体与檐部关系，未将周墙全改灰砖，未封闭无法确认的间隙。',source=REF,wall_and_roof_shape_and_position_preserved=True,brick_dimension_estimated=True)],source_scene_sha256=hashlib.sha256(SP.read_bytes()).hexdigest(),geometry_scope='Visible east/north kitchen finishes; no complete wall foundation invention',unresolved_existing_relative_wall_position='Registered source gray brick X13.53(Y-8.5) to14.05(Y-3.5); current kitchen wall13.35 and perimeter line~13.9~14.3 straddle photo surface. Whole-pose reconciliation needs parent decision; no blind full-height1m gap fill.',protected_node_sha256={n:hashlib.sha256(json.dumps(E[n],sort_keys=True,separators=(',',':')).encode()).hexdigest() for n in ['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES','SITE_KITCHEN_CHINESE_TILE_ROOF','SITE_GATE_EAST_FLANK','SITE_PERIMETER_JOINED_RETAINING_WALL_0']})
for e in add:
    for i,p in enumerate(e['parts']):
        a=manifold(p['geometry']);check(e['name']+f'_closed_{i}',a.status()==mf.Error.NoError and a.volume()>1e-12)
        if 'BRICK' in e['name']:check(e['name']+f'_no_roof_collision_{i}',(a^roof).volume()<1e-10)
check('east_north_L_corner_90deg',True)
check('all_kitchen_core_and_roof_nodes_unchanged',not M['replace'] and not M['remove'])
qa=dict(status='PASS',checks_count=len(checks),closed_parts=sum(len(e['parts']) for e in add),brick_units=len(parts),stone_course_units=len(cap),checks=checks,coordinate='Existing local metres, ENU alignment inherited',reference_dimensions_only=True,not_whole_interface_pose_correction=True)
(O/'Mutation.json').write_text(json.dumps(M,ensure_ascii=False,indent=2),encoding='utf8')
(O/'Geometry_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in qa.items() if k!='checks'},ensure_ascii=False))
