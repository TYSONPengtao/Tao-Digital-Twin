from pathlib import Path
p=Path('work/v10_wall_audit/audit_mutations.py');t=p.read_text(encoding='utf-8')
t=t.replace("g=E[n]['parts'][i]['geometry'];v,fs,_,_=ex.solid_data(g)","expanded=ex.expand_parts(E[n]);g=expanded[i]['geometry'];v,fs=ex.world_part(expanded[i],E[n])")
needle="# All coping profiles report absolute rise relative to old profile; estimates cannot become field values."
block='''# All actual holes and genuine junctions are tested, rather than moving the original corner probe alone.
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
'''
assert needle in t;t=t.replace(needle,block+needle)
t=t.replace("'floral_negative_space_probe_results':probe_rows,'method'","'floral_negative_space_probe_results':probe_rows,'all_actual_hole_probe_results':broad_rows,'crosschain_flower_crown_positive_intersections':overlap,'method'")
p.write_text(t,encoding='utf-8')
