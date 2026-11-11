from pathlib import Path
p=Path('work/v10_wall_audit/audit_mutations.py');t=p.read_text(encoding='utf-8')
needle='# All coping profiles report absolute rise relative to old profile; estimates cannot become field values.'
block='''# Audit actual flower negative space through the full wall-normal depth, including every new layer.
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
'''
assert needle in t;t=t.replace(needle,block+needle)
t=t.replace("'east_flank_kitchen_intersections':intersections,'method'","'east_flank_kitchen_intersections':intersections,'floral_negative_space_probe_results':probe_rows,'method'")
p.write_text(t,encoding='utf-8')
