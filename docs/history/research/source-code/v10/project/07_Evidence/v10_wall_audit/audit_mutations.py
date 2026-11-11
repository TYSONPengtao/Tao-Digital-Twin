"""Read-only audit staged V10 wall mutations; does not write Scene/model."""
import sys,json,math,hashlib,copy
from pathlib import Path
from collections import Counter
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
import manifold3d as md
from shapely.geometry import Polygon,box,Point,LineString
from shapely.ops import unary_union
import export_v5 as ex
O=Path(__file__).parent
BASE=Path(r'E:/jz/JIA/Rebuild_V9_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json')
base_bytes=BASE.read_bytes();B=json.loads(base_bytes);old={e['name']:e for e in B['elements']}
paths=[Path(x) for x in sys.argv[1:]]
if not paths:raise SystemExit('Usage: audit_mutations.py <Mutation1.json> <Mutation2.json>')
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
patches=[json.loads(p.read_bytes()) for p in paths]
E=copy.deepcopy(old);staged={};checks=[];cache={};invalid=[]
def check(name,ok,**extra):checks.append({'name':name,'passed':bool(ok),**extra})
for pp in patches:
 for n in pp.get('remove',[]):E.pop(n,None)
 for e in pp.get('replace',[])+pp.get('add',[]):
  check('mutation_name_disjoint_'+e['name'],e['name'] not in staged)
  staged[e['name']]=e;E[e['name']]=e
ex.SCENE={**B,'elements':list(E.values())}
body_names=['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1','SITE_COURTYARD_WEST_TILE_WALL','SITE_GATE_EAST_FLANK']
for n in body_names:check('wall_core_vertices_parts_and_materials_unchanged_'+n,E[n]['parts']==old[n]['parts'])
protected=json.loads((O/'Reference_Scope.json').read_text(encoding='utf-8'))['protected_existing_elements']
check('all_65_gate_kitchen_screenwall_annex_elements_protected',all(n in E and E[n]['parts']==old[n]['parts'] for n in protected),changed=[n for n in protected if n not in E or E[n]['parts']!=old[n]['parts']])
check('deleted_sw_gate_not_restored','SITE_SW_METAL_ENTRY_GATE' not in E)
check('cleared_timber_farmyard_fence_not_restored','SITE_FARMYARD_TIMBER_FENCE' not in E)
def body(n,i):
 key=(n,i)
 if key in cache:return cache[key]
 expanded=ex.expand_parts(E[n]);g=expanded[i]['geometry'];v,fs=ex.world_part(expanded[i],E[n])
 if v is None:raise ValueError((n,i,g['type']))
 tri=[]
 for f in fs:
  ts=ex.triangulate(v[f]) if len(f)>3 else [[0,1,2]]
  tri.extend([[f[j] for j in t] for t in ts])
 vs=np.asarray(v,np.float64);sol=md.Manifold(md.Mesh64(vs,np.asarray(tri,np.uint64)))
 row={'name':n,'part':i,'status':str(sol.status()),'volume_m3':sol.volume(),'vertices':len(v),'triangles':len(tri)}
 if sol.status()!=md.Error.NoError or sol.volume()<=1e-14 or not np.isfinite(vs).all():invalid.append(row)
 cache[key]=(sol,vs.min(0),vs.max(0));return cache[key]
for n in staged:
 for i in range(len(E[n]['parts'])):body(n,i)
check('all_new_detail_parts_closed_positive_finite',not invalid,parts_checked=len(cache),failures=invalid[:100])
# No changed wall solids enter retained actual inner doorway. A solid screenwall is protected above.
opening=md.Manifold.cube([2.6,.50,2.49]).translate([5.3,-11.95,-.45]);op_lo=np.array([5.3,-11.95,-.45]);op_hi=op_lo+np.array([2.6,.5,2.49]);positive=[]
for n in staged:
 for i in range(len(E[n]['parts'])):
  sol,lo,hi=body(n,i)
  if np.any(np.minimum(hi,op_hi)-np.maximum(lo,op_lo)<=1e-10):continue
  vol=(sol^opening).volume()
  if vol>1e-9:positive.append({'name':n,'part':i,'volume_m3':vol})
check('new_wall_details_do_not_occupy_inner_wood_doorway',not positive,positive=positive)
# Audit actual flower negative space through the full wall-normal depth, including every new layer.
probe_rows=[]
for patch in patches:
 probes=patch.get('hole_probes') or patch.get('changes',{}).get('negative_space_probes',[])
 for q in probes:
  center=np.array(q.get('point_local_m',q.get('center_local_m')),float)
  normal=np.array(q.get('normal_local',q.get('normal_local_m')),float);normal/=np.linalg.norm(normal)
  node=q.get('node',q.get('element')); depth=float(q.get('through_depth_m',q.get('normal_depth_m',.08)))
  maximum=0.;occ=[]
  for distance in np.linspace(-depth*.8,depth*.8,9):
   pc=center+normal*distance;cube=md.Manifold.cube([.004]*3,center=True).translate(pc.tolist());lo=pc-.002;hi=pc+.002
   for n in staged:
    for i in range(len(E[n]['parts'])):
     s,slo,shi=body(n,i)
     if np.any(np.minimum(hi,shi)-np.maximum(lo,slo)<=1e-10):continue
     vol=(s^cube).volume();maximum=max(maximum,vol)
     if vol>1e-12:occ.append(dict(distance_m=float(distance),name=n,part=i,volume_m3=vol))
  neighbor=np.array(q.get('solid_probe_neighbor_local_m',center+[0,0,.05]),float)
  cube=md.Manifold.cube([.004]*3,center=True).translate(neighbor.tolist());material_volume=0.
  for i in range(len(E[node]['parts'])):
   s,slo,shi=body(node,i)
   if np.any(np.minimum(neighbor+.002,shi)-np.maximum(neighbor-.002,slo)<=1e-10):continue
   material_volume+=(s^cube).volume()
  check('floral_aperture_is_true_through_hole_'+node,maximum<=1e-12,probe=center.tolist(),through_depth_m=depth,maximum_blockage_volume_m3=maximum,positive_layers=occ)
  check('floral_neighbor_is_solid_'+node,material_volume>1e-11,neighbor_probe=neighbor.tolist(),solid_volume_m3=material_volume)
  probe_rows.append(dict(node=node,center=center.tolist(),maximum_blockage_volume_m3=maximum,neighbor_material_volume_m3=material_volume))
check('both_perimeter_and_courtyard_genuine_negative_space_probes_present',len(probe_rows)>=3,probe_count=len(probe_rows))
# All actual holes and genuine junctions are tested, rather than moving the original corner probe alone.
broad_rows=[];broad_fail=[];sidecars=[]
for d in [W/'v10_perimeter_detail',W/'v10_courtyard_wall']:
 fp=d/'All_Actual_Hole_Probes.json'
 if fp.exists():
  data=json.loads(fp.read_text(encoding='utf-8'));sidecars.append((fp,data))
  check('hole_registration_matches_frozen_mutation_'+d.name,data.get('mutation_sha256')==hashes[str(d/'Mutation.json')] if str(d/'Mutation.json') in hashes else data.get('mutation_sha256')==hashlib.sha256((d/'Mutation.json').read_bytes()).hexdigest())
source_host_names=['KZ_1_1_F1','SITE_INNER_STONE_GATEHOUSE','SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES','SITE_KITCHEN_CHINESE_TILE_ROOF','SITE_INNER_GATEHOUSE_UNDER_ROOF_BASE']+body_names
query_names=list(staged)+[n for n in source_host_names if n in E]
query=[]
for n in query_names:
 for i in range(len(ex.expand_parts(E[n]))):
  sol,lo,hi=body(n,i);query.append((n,i,sol,lo,hi))
qlo=np.array([r[3] for r in query]);qhi=np.array([r[4] for r in query])
for fp,data in sidecars:
 for q in data.get('all_holes',data.get('holes',[])):
  pc=np.array(q.get('point_local_m',q.get('center_local_m')),float);nn=np.array(q.get('normal_local',q.get('normal_local_m')),float);nn/=np.linalg.norm(nn)
  depth=float(q.get('drill_depth_m',q.get('through_depth_m',q.get('normal_depth_m',.08))))
  blockers=[];maxvol=0.
  for distance in np.linspace(-depth/2,depth/2,9):
   point=pc+nn*distance;lo=point-.003;hi=point+.003
   ids=np.flatnonzero(np.all(np.minimum(qhi,hi)-np.maximum(qlo,lo)>1e-10,axis=1))
   cube=md.Manifold.cube([.006]*3,center=True).translate(point.tolist())
   for j in ids:
    n,i,sol,_,_=query[j];vol=(sol^cube).volume();maxvol=max(maxvol,vol)
    if vol>1e-12:blockers.append(dict(name=n,part=i,distance_m=float(distance),volume_m3=vol))
  row={'node':q.get('node',q.get('element')),'center_local_m':pc.tolist(),'segment':q.get('segment'),'station_local_m':q.get('station_local_m',q.get('route_s')),'maximum_blockage_volume_m3':maxvol,'blockers':blockers}
  broad_rows.append(row)
  if blockers:broad_fail.append(row)
check('all_actual_registered_holes_clear_other_new_layers_and_retained_pier_gate_kitchen_cores',not broad_fail,actual_holes_tested=len(broad_rows),failed_hole_count=len(broad_fail),failures=broad_fail)
check('both_actual_hole_registrations_available',len(sidecars)==2,files=[str(x[0]) for x in sidecars])
# Actual interpenetration of the two flower crown groups at the NW cross-chain corner.
a='SITE_PERIMETER_JOINED_RETAINING_WALL_0_PROVISIONAL_FLOWER_CROWN';b='SITE_PERIMETER_JOINED_RETAINING_WALL_1_PROVISIONAL_FLOWER_CROWN';overlap=[];bcalls=0
for i in range(len(E[a]['parts'])):
 aa,alo,ahi=body(a,i)
 for j in range(len(E[b]['parts'])):
  bb,blo,bhi=body(b,j)
  if np.any(np.minimum(ahi,bhi)-np.maximum(alo,blo)<=1e-10):continue
  vol=(aa^bb).volume();bcalls+=1
  if vol>1e-9:overlap.append(dict(wall0_part=i,wall1_part=j,volume_m3=vol))
check('two_perimeter_flower_crown_groups_do_not_interpenetrate_at_shared_NW_corner',not overlap,boolean_calls=bcalls,positive_pairs=overlap)
# All coping profiles report absolute rise relative to old profile; estimates cannot become field values.
profiles=[]
for n in staged:
 vs=[body(n,i)[2] for i in range(len(E[n]['parts']))]
 if not vs:continue
 hi=np.max(vs,axis=0)
 base_z=None
 if n in old and n.endswith('_TILE_COPING'):
  zz=[]
  for p in old[n]['parts']:
   ov=ex.solid_data(p['geometry'])[0];zz.extend(ov[:,2])
  base_z=max(zz)
 profiles.append({'name':n,'max_z_local_m':float(hi[2]),'old_max_z_local_m':base_z,'delta_max_z_m':float(hi[2]-base_z) if base_z is not None else None})
# Source-supported kitchen south gable / roof risk: report actual positive intersections for flank details.
hosts=['SITE_KITCHEN_GREY_BRICK_BACK_AND_GABLES','SITE_KITCHEN_CHINESE_TILE_ROOF']
intersections=[]
for n in staged:
 if not any(k in n for k in ['FLANK','EAST']):continue
 for hn in hosts:
  total=0.;pairs=[]
  for i in range(len(E[n]['parts'])):
   a,alo,ahi=body(n,i)
   for j in range(len(E[hn]['parts'])):
    b,blo,bhi=body(hn,j)
    if np.any(np.minimum(ahi,bhi)-np.maximum(alo,blo)<=1e-10):continue
    vol=(a^b).volume()
    if vol>1e-9:total+=vol;pairs.append({'detail_part':i,'host_part':j,'volume_m3':vol})
  if pairs:intersections.append({'detail':n,'host':hn,'total_volume_m3':total,'pairs':pairs})
# Compare only actual top-shell penetration as failure; wall-seated ornament is reported for context.
roof_intrusions=[r for r in intersections if r['host']=='SITE_KITCHEN_CHINESE_TILE_ROOF']
check('east_flank_details_do_not_enter_kitchen_roof_shell',not roof_intrusions,positive=roof_intrusions)
for p in paths:check('frozen_patch_unchanged_'+p.parent.name,hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p)])
check('source_scene_read_only',BASE.read_bytes()==base_bytes)
result={'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','checks':checks,'mutation_sha256':hashes,'base_scene_sha256':hashlib.sha256(base_bytes).hexdigest(),'tested_new_parts':sum(len(E[n]['parts']) for n in staged),'closed_part_failures':invalid,'coping_profile_absolute_and_delta':profiles,'east_flank_kitchen_intersections':intersections,'floral_negative_space_probe_results':probe_rows,'all_actual_hole_probe_results':broad_rows,'crosschain_flower_crown_positive_intersections':overlap,'method':'V9 baseline and frozen Mutation files merged only in memory; Mesh64 closed-manifold/volume/doorway and actual kitchen roof Boolean checks; original files untouched. Floral negative-space probes audited separately when provided.'}
(O/'Final_Wall_Geometry_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':result['status'],'checks':len(checks),'new_parts':result['tested_new_parts'],'failed':[c for c in checks if not c['passed']],'kitchen_intersections':intersections},ensure_ascii=False,indent=2))
