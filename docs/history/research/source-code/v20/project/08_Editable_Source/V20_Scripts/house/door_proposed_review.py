from pathlib import Path
exec((Path(__file__).parent/'door_review.py').read_text().split("report={'status'")[0])
# Latest assembled-source pose against the retained real collision bodies.
# This is a proposal review, distinct from the saved-native result.
Q=json.loads((W/'v20/Mutation.json').read_text(encoding='utf8'));QE={e['name']:e for e in Q['replace']+Q['add']}
DM=json.loads((W/'v20/Door_Manifest.json').read_text(encoding='utf8'))
patch=json.loads((D/'Outer_Gate_Bottom_Mutation.json').read_text(encoding='utf8'))
QE.update({e['name']:e for e in patch['replace']})
report={'scope':'Latest work/v20/Mutation source poses plus isolated outer-gate bottom fix; collision bodies from actual saved V20 cache','status':'PASS_PROPOSED_POSES','doors':[],'critical_collisions':[],'minor_contacts':[],'unresolved':[]}
leaf_names={r['name'] for r in DM['doors']};physical=[]
for r in I:
 n=r['name']
 if n in leaf_names or n.startswith(('SITE_V14_ORIGINAL_EXTERIOR','CONTEXT','VIS_','REF_','GRID_')) or r['element'].get('family')=='VIS_MODEL' or not r['triangles']:continue
 b=r.get('actual_3dm_mesh_bbox_local');b=native(n)[2] if b is None else np.array(b);physical.append((n,b))
def qleaf(n):
 e=QE[n];m=mf.Manifold.batch_boolean([manifold(p['geometry']) for p in e['parts']],mf.OpType.Add);vv=np.vstack([p['geometry']['vertices'] for p in e['parts']]);return m,np.array([vv.min(0),vv.max(0)])
for mr in DM['doors']:
 n=mr['name'];dm,b=qleaf(n);row={'name':n,'open_angle':QE[n].get('open_angle_degrees'),'bounds':b.tolist(),'hinge':QE[n]['pivot_world_m'],'collisions':[]}
 for cn,cb in physical:
  if not bbox_overlap(b,cb):continue
  try:
   cm=get(cn);intr=dm^cm;vol=intr.volume()
   if vol<=1e-7:continue
   rr={'door':n,'collider':cn,'volume_m3':vol,'fraction':vol/dm.volume(),'bounds':list(intr.bounding_box())};row['collisions'].append(rr)
   minor=(('HINGE_HARDWARE' in cn or cn.endswith('__FRAME')) and vol<.0004 and vol/dm.volume()<.03)
   (report['minor_contacts'] if minor else report['critical_collisions']).append(rr)
  except Exception as er:report['unresolved'].append({'door':n,'collider':cn,'error':str(er)})
 report['doors'].append(row);print(n,'hits',len(row['collisions']),flush=True)
if report['critical_collisions']:report['status']='FAIL_REMAINING_PROPOSED_POSE_COLLISIONS'
if report['unresolved']:report['status']='INCOMPLETE'
(D/'Door_Proposed_Review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('FINAL',report['status'],'critical',len(report['critical_collisions']),'minor',len(report['minor_contacts']),flush=True)
