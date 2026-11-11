"""Cut the V8 kitchen roof to the photographed gate underlap, preserving heights."""
import sys, json, copy, math, hashlib
from pathlib import Path
from collections import Counter
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
import manifold3d as md
from shapely.geometry import Polygon, box
import export_v5 as ex
from roof_parameters import *

OUT=Path(__file__).parent
BASELINE=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid\08_Editable_Source\05_Intermediate\Architecture_Scene.json')
S=json.loads(BASELINE.read_text(encoding='utf-8')); E={e['name']:e for e in S['elements']}
FOOT=Polygon(KITCHEN_FOOTPRINT)
OLD=box(6.98,-12.05,13.60,-2.15)
CUT=OLD.difference(FOOT)
MASK=md.CrossSection([np.asarray(KITCHEN_FOOTPRINT,dtype=np.float64)]).extrude(8).translate([0,0,-2])
replace=[];add=[];remove=[];metrics=[]

def triangles(faces):
    return np.asarray([[f[0],f[k],f[k+1]] for f in faces for k in range(1,len(f)-1)],dtype=np.uint64)

def as_manifold(g):
    v, fs, _, _=ex.solid_data(g)
    result=md.Manifold(md.Mesh64(np.asarray(v,dtype=np.float64),triangles(fs)))
    if result.status()!=md.Error.NoError: raise ValueError(('Input manifold',result.status()))
    return result

def from_manifold(result):
    if result.status()!=md.Error.NoError:raise ValueError(('Result manifold',result.status()))
    m=result.to_mesh64()
    return dict(type='polyhedron',vertices=m.vert_properties[:,:3].tolist(),faces=m.tri_verts.tolist())

def trim_node(name):
    e=copy.deepcopy(E[name]);parts=[];trimmed=removed=unchanged=0;before_vol=after_vol=0.
    for p in e['parts']:
        g=p['geometry'];v=np.asarray(g['vertices'])
        outside=np.array([not FOOT.covers(__import__('shapely').geometry.Point(*q[:2])) for q in v])
        if not outside.any():
            parts.append(p);unchanged+=1;continue
        source=as_manifold(g);result=source^MASK
        before_vol+=source.volume();after_vol+=result.volume()
        if result.is_empty():removed+=1;continue
        if abs(source.volume()-result.volume())<1e-10:
            parts.append(p);unchanged+=1;continue
        p['geometry']=from_manifold(result);parts.append(p);trimmed+=1
    e['parts']=parts
    e.update(status='V9_PHOTO_AND_REGISTERED_SCAN_UNDERLAP_TERMINATION',source='DJI_0046.JPG; DJI_0047.JPG; DJI_0048.JPG; V9 user relationship diagram; original registered JIA OBJ',roof_plan_footprint=KITCHEN_FOOTPRINT,underlap_termination_line=JOINT_TERMINATION_LINE,ordinary_height_formula_unchanged=True)
    replace.append(e)
    metrics.append(dict(name=name,parts_before=len(E[name]['parts']),parts_after=len(parts),whole_parts_unchanged=unchanged,cut_closed_parts=trimmed,removed_parts=removed,affected_input_volume_m3=before_vol,affected_result_volume_m3=after_vol))

trim_node('SITE_KITCHEN_CHINESE_TILE_ROOF')
trim_node('SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_0')

# Concealed thin cap closes cut tile ends without introducing a gutter or
# invented tall wall between the two roofs. It sits within the lower roof.
xs=np.unique(np.r_[np.linspace(6.98,9.05,43),8.45]); vertices=[]
for zoff in [0,-.055]:
    for x in xs:
        y=kitchen_ymin(x)
        for yy in [y+.003,y+.080]:vertices.append([float(x),float(yy),float(zkitchen(x,yy)-.003+zoff)])
n=len(vertices)//2;faces=[]
for i in range(len(xs)-1):
    a=2*i;b=a+2;c=b+1;d=a+1
    faces.extend([[a,b,c],[a,c,d],[a+n,d+n,c+n],[a+n,c+n,b+n]])
rim=[2*i for i in range(len(xs))]+[2*i+1 for i in range(len(xs)-1,-1,-1)]
for a,b in zip(rim,rim[1:]+rim[:1]):faces.append([b,a,a+n,b+n])
cap=dict(type='polyhedron',vertices=vertices,faces=faces)
# Reverse only if the closed builder's signed volume is negative.
vv=np.array(vertices);volume=sum(np.dot(vv[f[0]],np.cross(vv[f[k]],vv[f[k+1]]))/6 for f in faces for k in range(1,len(f)-1))
if volume<0:cap['faces']=[f[::-1] for f in faces]
add.append(dict(name='SITE_KITCHEN_GATE_UNDERLAP_TILE_EDGE_CLOSURE',layer='60_SITE',family='SITE_MODEL',parts=[dict(geometry=cap,material='M_Roof')],classification='CONCEALED_TILE_TERMINATION_CAPPING',confidence='MEDIUM',source='V9 relationship diagram; photo-supported lower roof end below gate; module thickness estimated',status='RELATION_PHOTO_CONFIRMED; HIDDEN_CAP_DIMENSIONS_ESTIMATED',underlap_termination_line=JOINT_TERMINATION_LINE))

changes=[dict(id='V9_KITCHEN_GATE_ROOF_UNDERLAP',description='木房西南角在门楼承托墙前斜向收头，保留伸入前檐投影的低屋面；移除贯穿墙芯的旧瓦，封闭瓦端。保留原普通瓦坡面高程和门楼主体。',evidence=['DJI_0046.JPG','DJI_0047.JPG','DJI_0048.JPG','User roof relationship diagram','Original registered JIA OBJ'],dimension_status='ROOF_SCAN_HEIGHT_PRESERVED; JOINT_PLAN_TERMINATION_PHOTO_INFERRED')]
mutation=dict(replace=replace,add=add,remove=remove,materials={},definitions={},changes=changes)

def apply(scene):
    names={e['name'] for e in replace}|set(remove)
    scene['elements']=[e for e in scene['elements'] if e['name'] not in names]+copy.deepcopy(replace)+copy.deepcopy(add)
    scene.setdefault('v9_changes',[]).extend(copy.deepcopy(changes));return scene

def verify():
    checks=[]
    def check(name,passed,**data):
        checks.append(dict(name=name,passed=bool(passed),**data))
        if not passed:raise ValueError((name,data))
    for e in replace+add:
        for i,p in enumerate(e['parts']):
            g=p['geometry'];v=np.asarray(g['vertices']);f=g['faces']
            ed=Counter(tuple(sorted((a,b))) for face in f for a,b in zip(face,face[1:]+face[:1]))
            dr=Counter((a,b) for face in f for a,b in zip(face,face[1:]+face[:1]))
            check(e['name']+f'_part_{i}_closed', all(n==2 for n in ed.values()) and all(n==dr.get((b,a),0) for (a,b),n in dr.items()))
            check(e['name']+f'_part_{i}_within_footprint',all(FOOT.buffer(1e-8).covers(__import__('shapely').geometry.Point(*q[:2])) for q in v))
            check(e['name']+f'_part_{i}_volume_positive',as_manifold(g).volume()>0)
    gateplan=box(*GATE_BOUNDS);overlap=FOOT.intersection(gateplan)
    expected_overlap=(8.45-6.98)*(-10.22+11.28)+.5*(9.05-8.45)*((-10.22+11.28)+(-10.22+12.05))
    check('nonzero_lower_roof_under_gate_plan_overlap',overlap.area>0 and abs(overlap.area-expected_overlap)<1e-10,area_m2=overlap.area,derived_expected_area_m2=expected_overlap)
    check('removed_corner_entirely_under_high_gate_roof',CUT.difference(gateplan).area<1e-10,uncovered_removed_corner_area_m2=CUT.difference(gateplan).area)
    check('front_back_lower_roof_end_in_front_of_gate_support',kitchen_ymin(7.7)>-11.45,front_wall_clearance_m=kitchen_ymin(7.7)+11.45,roof_underlap_to_front_eave_m=-10.22-kitchen_ymin(7.7))
    gatebaseplan=box(4.9,-11.95,8.3,-11.45)
    check('no_lower_roof_through_gate_support_wall_plan',FOOT.intersection(gatebaseplan).area<1e-9,plan_collision_area_m2=FOOT.intersection(gatebaseplan).area)
    q=np.load(W/'v8_chinese_eaves/Donor_Roof_Samples.npz')['centroids']
    q=q[(q[:,0]>=7)&(q[:,0]<=13.4)&(q[:,1]>=-10)&(q[:,1]<=-3)&(q[:,2]>=2.5)&(q[:,2]<=4.45)]
    r=np.array([p[2]-zkitchen(*p[:2])-.05 for p in q])
    check('ordinary_kitchen_scan_fit_unchanged',abs(float(np.sqrt(np.mean(r*r)))-.03595051262842575)<1e-12,samples=len(q),rmse_m=float(np.sqrt(np.mean(r*r))),p95_m=float(np.quantile(abs(r),.95)))
    # Ordinary upper/lower tile envelopes are separated; changed ends now
    # have solid caps and no inter-roof intrusion. Compare both before/after.
    qxy=np.array([[x,y] for x in np.linspace(6.98,9.05,101) for y in np.linspace(-12.05,-10.22,101) if in_kitchen(x,y)])
    gap=np.array([zgate(x,y)-.075-zkitchen(x,y)-.10 for x,y in qxy])
    check('no_lower_cover_tile_in_upper_tile_shell',gap.min()>0,min_tile_envelope_clearance_m=float(gap.min()),interpretation='Actual ordinary roof level difference is retained; termination/cornice relation does not mean coincident roof surfaces.')
    check('gate_roof_and_kitchen_east_roof_nodes_unmodified',not any(e['name'].startswith('SITE_INNER_GATEHOUSE_ROOF') or e['name']=='SITE_KITCHEN_CHINESE_TILE_ROOF_TILE_ROWS_1' for e in replace))
    scope=dict(coordinates='LOCAL metres Z up',source_scene_sha256=hashlib.sha256(BASELINE.read_bytes()).hexdigest(),changed_roof_corner_polygon=[list(p) for p in CUT.exterior.coords],changed_corner_area_m2=CUT.area,final_kitchen_footprint=KITCHEN_FOOTPRINT,concealed_edge_cap=JOINT_TERMINATION_LINE,gate_roof_formula_unchanged=True,kitchen_ordinary_roof_formula_unchanged=True,upper_and_lower_roof_axes_angle_degrees=90,roof_centreline_front_back_relation='Kitchen west eave runs north/south; gate ridge east/west. At SW join, kitchen termination is in front (larger LOCAL Y) of gate masonry wall, inside gate front-eave shadow. Gate front slope drains north toY=-10.22; kitchen west slope drains west toX=6.98; no valley gutter inferred.')
    (OUT/'Repair_Scope.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2),encoding='utf-8')
    result=dict(status='PASS',checks_count=len(checks),checks=checks,mutation_metrics=metrics,scope=scope,limitations=['Boundary offset and concealed cap thickness inferred from photographs, not field measurements.','Door position, whole kitchen ordinary slope and gate ordinary tile shell are unchanged.','Construction-layer and south-gable corrections are a separate coordinated patch.'])
    (OUT/'Geometry_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=result['status'],checks=len(checks),metrics=metrics,overlap_m2=overlap.area,minimum_roof_clearance_m=float(gap.min())),ensure_ascii=False,indent=2))

if __name__=='__main__':
    (OUT/'Mutation.json').write_text(json.dumps(mutation,ensure_ascii=False,indent=2),encoding='utf-8')
    verify()
