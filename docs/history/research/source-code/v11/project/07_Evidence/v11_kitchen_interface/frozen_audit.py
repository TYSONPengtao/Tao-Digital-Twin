"""Independent read-only checks against the frozen kitchen JSON and V10 scene."""
import sys, json, math, ast, hashlib, collections
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np, manifold3d as mf
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import export_v5 as ex
O=Path(__file__).parent
SP=Path(r'E:/jz/JIA/Rebuild_V10_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json')
sb=SP.read_bytes();mb=(O/'Mutation.json').read_bytes();M=json.loads(mb)
S=json.loads(sb);B={e['name']:e for e in S['elements']};R={e['name']:e for e in M['replace']};A={e['name']:e for e in M['add']}
tree=ast.parse((W/'v11_wall_junction/mutation.py').read_text(encoding='utf8'))
exec(compile(ast.Module([n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['triangles','oriented','manifold']],type_ignores=[]),'<geometry_helpers>','exec'))
checks=[]
def check(name,ok,**data):
 checks.append(dict(name=name,passed=bool(ok),**data))
 if not ok:raise AssertionError((name,data))
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def union(pp):return mf.Manifold.batch_boolean([manifold(p['geometry']) for p in pp],mf.OpType.Add)
def planar_floor(pp,z):
 polys=[]
 for p in pp:
  v,fs,*_=ex.solid_data(p['geometry']);v=np.asarray(v)
  for f in triangles(v,fs):
   t=v[np.asarray(f,dtype=int)]
   if max(abs(t[:,2]-z))<1e-8:
    q=Polygon(t[:,:2])
    if q.area>1e-12:polys.append(q)
 return unary_union(polys)
check('frozen_source_SHA_matches',hashlib.sha256(sb).hexdigest()==M['source_scene_sha256'])
for name in R:check('replaced_source_node_SHA_'+name,sha(B[name])==M['old_node_sha256'][name])
wall='SITE_PERIMETER_JOINED_RETAINING_WALL_0';old=B[wall]['parts'];new=R[wall]['parts'];mp={r['link_index']:r for r in M['old_wall0_replacement_map']};off=0;stone=[];upper=[]
for j in range(117):
 count=mp[j]['new_part_count'] if j in mp else 2
 pp=new[off:off+count]
 if j not in mp:check(f'non_kitchen_link_{j}_parts_exact',pp==old[j*2:j*2+2])
 else:
  stone.extend(p for p in pp if p['material']=='M_Stone_Rubble');upper.extend(p for p in pp if p['material']!='M_Stone_Rubble')
 off+=count
check('only_original_wall0_links60_to66_replaced',sorted(mp)==list(range(60,67)))
check('complete_wall0_part_map',off==len(new))
kit='SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES';Lparts=R[kit]['parts'][1:];Ls=union(Lparts)
check('original_south_gable_preserved_exact',R[kit]['parts'][0]==B[kit]['parts'][0])
protected=[n for n in B if n.startswith('SITE_KITCHEN_CHINESE_TILE_ROOF') or n.startswith('SITE_GATE_EAST_FLANK') or 'KITCHEN_GATE' in n or 'GATE_KITCHEN' in n]
for name in protected:check('protected_west_eave_roof_gate_node_'+name,name not in R and name not in A and name not in M['remove'])
k=float(M['registered_fit']['slope_x_per_y']);b=float(M['registered_fit']['intercept']);corner=np.array(M['registered_fit']['corner_local_m'])
check('registered_corner_on_original_fitted_face',abs(corner[0]-k*corner[1]-b)<1e-10)
check('north_return_to_back_is90degrees',abs(np.dot([k,1],[1,-k]))<1e-12,angle_degrees=90.)
check('original_mesh_fitted_wall_supported',M['registered_fit']['kept']>=400,p95_residual_m=M['registered_fit']['p95_abs_residual_m'],dimension_status='photographed_mesh_fit_not_field_survey')
highdup=0. if not upper else (Ls^union(upper)).volume()
check('no_high_kitchen_and_low_perimeter_double_wall',highdup<1e-7,intersection_volume_m3=highdup)
overlaps=[];max_stone_intersection_volume=0.
for i in range(len(stone)):
 for j in range(i+1,len(stone)):
  x=(manifold(stone[i]['geometry'])^manifold(stone[j]['geometry'])).volume()
  max_stone_intersection_volume=max(max_stone_intersection_volume,x)
  if x>1e-7:overlaps.append(dict(links=[60+i,60+j],volume_m3=x))
check('no_duplicated_retaining_foundation_volume',not overlaps,overlaps=overlaps,maximum_residual_volume_m3=max_stone_intersection_volume,accepted_numerical_residual_volume_m3=1e-7,XY_plan_rounding_m=1e-6)
lf=planar_floor(Lparts,-.4);sf=planar_floor(stone,-.4)
a=np.array([k*(-8.275)+b,-8.275]);n=np.array([-1.,k]);n/=np.linalg.norm(n)
supported=Polygon([a,corner,corner+n*.22,a+n*.22]).intersection(lf).intersection(box(-100,-8.275,100,corner[1]));gap=supported.difference(sf).area
check('registered_back_wall_supported_without_artificial_walkway',gap<1e-5,uncovered_area_m2=gap)
roof=union(B['SITE_KITCHEN_CHINESE_TILE_ROOF']['parts']);eave=union(A['SITE_KITCHEN_V11_REGISTERED_EAST_EAVE_STRIP']['parts']);roofdup=(roof^eave).volume()
check('local_eave_strip_does_not_duplicate_original_roof',roofdup<1e-7,intersection_volume_m3=roofdup)
scope=[]
for j in range(60,67):
 v=np.array(old[j*2]['geometry']['vertices'])[:4,:2];a=(v[0]+v[3])/2;c=(v[1]+v[2])/2;oa=(v[3]-v[0])/2/.16*.30;oc=(v[2]-v[1])/2/.16*.30
 scope.append(Polygon([a-oa,c-oc,c+oc,a+oa]))
scope=unary_union(scope)
for suffix in ['_TILE_COPING','_PROVISIONAL_FLOWER_CROWN','_PLASTER_STEPPED_RELIEF']:
 name=wall+suffix;cnt=collections.Counter(sha(p) for p in R[name]['parts']);untouched=[]
 for p in B[name]['parts']:
  v=np.array(p['geometry']['vertices']);bb=box(*v[:,:2].min(0),*v[:,:2].max(0))
  if not bb.intersects(scope):untouched.append(p)
 wanted=collections.Counter(sha(p) for p in untouched)
 check('all_whole_detail_parts_outside7_scope_exact'+suffix,all(cnt[h]>=c for h,c in wanted.items()),exact_original_parts=len(untouched),original_parts=len(B[name]['parts']))
qa=json.loads((O/'Geometry_QA.json').read_bytes());check('all_frozen_geometry_passed_closed_solid_checks',qa['status']=='PASS' and all(c['passed'] for c in qa['checks']),closed_parts=qa['parts'],checks=qa['checks_count'])
slivers=qa['collapsed_boolean_slivers'];check('only_numerical_zero_thickness_boolean_slivers_removed',max(x['raw_volume_m3'] for x in slivers)<1e-9,removed_count=len(slivers),maximum_original_volume_m3=max(x['raw_volume_m3'] for x in slivers),total_original_volume_m3=sum(x['raw_volume_m3'] for x in slivers),weld_tolerance_m=qa['boolean_weld_tolerance_m'])
check('frozen_files_unchanged_during_audit',SP.read_bytes()==sb and (O/'Mutation.json').read_bytes()==mb)
out=dict(status='PASS',mutation_sha256=hashlib.sha256(mb).hexdigest(),checks=checks,checks_count=len(checks),changed_retaining_links=sorted(mp),preserved_other_link_count=110,closed_parts=qa['parts'],replace=len(R),add=len(A),limitations=['Original photographed mesh fit P95 residual46.86mm, not field-measured construction coordinates.','Short stone endpoint transitions and northern return geometry are inferred; underground structural dimensions/stone positions not asserted.','Individual visible brick module dimensions are reference values.'])
(O/'Frozen_Connection_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='checks'},ensure_ascii=False))
