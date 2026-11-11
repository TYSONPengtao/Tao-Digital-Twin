from v26_2_common import *
from shapely.geometry import Polygon,shape,box as box2
from shapely.ops import unary_union
import hashlib
D=W/'v26_16';O=Path('E:/jz/JIA/Rebuild_V26_16');P=O/'Blender/Architecture_Complete_V26_16.blend';sj=json.loads((D/'Input/Source_Index.json').read_text('utf8'));S={r['name']:r for r in sj['objects']};final={r['name']:r for r in json.loads((D/'Final/Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';EN='HOUSE_V22_CONTINUOUS_BALCONY_EDGE_Geometry';fr=final[HN];a=np.load(D/'Input'/S[HN]['file']);b=np.load(D/'Final'/fr['file']);old=solid(a['v'],a['f']);new=solid(b['v'],b['f']);proof=json.loads((D/'Prepared.json').read_text('utf8'))['proof'];scopes=[cube(*q['scope_bounds_m'])for q in proof['nodes']+proof['balcony_corner_ownership']+[proof['bay_ceiling_closure']]];mask=union(scopes);checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('GEOMETRY_QA',n,bool(p),kw if not p else'',flush=True)
outside=[((new-old)-mask).volume(),((old-new)-mask).volume()];ck('Changes stay inside five jambs, two corner seats and the F3R bay soffit within native float tolerance',max(map(abs,outside))<5e-6,outside_added_removed_m3=outside,native_float32_volume_tolerance_m3=5e-6)
ck('Saved house stays one positive connected closed solid',len(new.decompose())==1 and new.volume()>0,components=len(new.decompose()),volume_m3=new.volume())
def sliced(m,z):
 pos=[];neg=[]
 for p in m.slice(z).to_polygons():
  p=np.asarray(p);sgn=np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1]);(pos if sgn>0 else neg).append(Polygon(p))
 return unary_union(pos).difference(unary_union(neg))
sections=[];frames=[];heads=[]
for nd in proof['nodes']:
 lo,hi=nd['scope_bounds_m'];roi=box2(lo[0]+.0001,lo[1]+.0001,hi[0]-.0001,hi[1]-.0001);ideal=shape(nd['jamb_plan']).intersection(roi)
 for z in np.linspace(nd['frame_bottom_z_m']+.06,nd['beam_soffit_z_m']-.04,5):
  p=sliced(new,float(z)).intersection(roi);# Existing frame seat removes a narrow terminal portion of the ideal jamb.
  difference=p.difference(ideal.buffer(.00001)).area;sections.append({'floor':nd['floor'],'side':nd['side'],'z_m':float(z),'extra_white_projection_m2':difference})
 # The fixed black frame owns its full depth; no white fingers cross it.
 wr=S[nd['frame']];wa=np.load(D/'Input'/wr['file']);wm=solid(wa['v'],wa['f']);frames.append({'frame':nd['frame'],'before_overlap_m3':(old^wm).volume(),'after_overlap_m3':(new^wm).volume()})
 cx=(lo[0]+hi[0])/2;head=sliced(new,nd['frame_top_z_m']+.025);heads.append({'floor':nd['floor'],'side':nd['side'],'continuous_header_seat':head.covers(shape(nd['jamb_plan']).intersection(box2(cx-.1,2.2,cx+.1,2.38)).buffer(-.002))})
ck('No transverse white tabs remain at25 different glazing-height slices',all(q['extra_white_projection_m2']<2e-6 for q in sections),samples=sections)
ck('All five retained fixed oblique frames have no white-solid intersection',all(abs(q['after_overlap_m3'])<1e-7 for q in frames),frames=frames)
ck('Each head is bonded continuously to its narrow wall return',all(q['continuous_header_seat']for q in heads),nodes=heads)
ea=np.load(D/'Input'/S[EN]['file']);eb=np.load(D/'Final'/final[EN]['file']);edge0=solid(ea['v'],ea['f']);edge1=solid(eb['v'],eb['f']);seats=union([cube(*q['scope_bounds_m'])for q in proof['balcony_corner_ownership']]);edge_outside=[((edge1-edge0)-seats).volume(),((edge0-edge1)-seats).volume()]
ck('External balcony edge is unchanged outside the two transferred seats',max(map(abs,edge_outside))<2e-6,outside_added_removed_m3=edge_outside)
ownership=[]
for nd in proof['balcony_corner_ownership']:
 roi=cube(*nd['scope_bounds_m']);ep=edge0^roi;actual=(new^ep)+(edge1^ep);air=shape(nd['indoor_air_plan']);z0,z1=nd['old_underside_z_m'],nd['new_underside_z_m'];z=(z0+z1)/2
 removed=(ep-actual).volume();wanted=nd['exposed_intrusion_removed_m3'];ownership.append({'floor':nd['floor'],'side':nd['side'],'removed_from_old_balcony_m3':removed,'expected_room_side_trim_m3':wanted,'transferred_volume_retained_above_ceiling_m3':(actual^cube([nd['scope_bounds_m'][0][0],nd['scope_bounds_m'][0][1],z1+.00001],nd['scope_bounds_m'][1])).volume(),'single_owner_overlap_m3':(new^edge1^roi).volume(),'residual_old_room_air_area_m2':sliced(actual,z).intersection(air).area})
ck('Balcony corner ownership preserves its stock except the 2mm indoor intrusion',all(abs(q['removed_from_old_balcony_m3']-q['expected_room_side_trim_m3'])<2e-6 and abs(q['single_owner_overlap_m3'])<2e-7 and q['residual_old_room_air_area_m2']<2e-6 for q in ownership),nodes=ownership)
closure=proof['bay_ceiling_closure'];body_nodes=union([cube(*q['scope_bounds_m'])for q in proof['nodes']]);low_added=((new-old)-body_nodes)^cube([9.,1.,9.9],[13.1,2.5,closure['finished_ceiling_z_m']-.00001]);ck('Bay closure adds no stock below the existing ceiling outside the five separately repaired jambs',abs(low_added.volume())<2e-6,added_below_ceiling_m3=low_added.volume())
ck('Prior V26.15 source stays byte-identical',hashlib.sha256(Path(sj['model']).read_bytes()).hexdigest()==sj['sha256'])
fail=[q for q in checks if not q['pass']];report={'status':'PASS'if not fail else'FAIL','model_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'checks':checks,'failures':fail};(O/'Reports/V26_16_Geometry_QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print('GEOMETRY_QA_DONE',len(checks),len(fail),flush=True)
if fail:raise AssertionError(fail)
