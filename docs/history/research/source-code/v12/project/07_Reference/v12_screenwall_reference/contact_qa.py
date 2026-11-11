import sys,json
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,trimesh
O=Path(__file__).parent
S=json.loads((O/'Preview_Scene.json').read_text(encoding='utf-8'))
E={e['name']:e for e in S['elements']}
def mesh(p):
 g=p['geometry'];faces=[]
 for f in g['faces']:
  faces.extend([[f[0],f[k],f[k+1]] for k in range(1,len(f)-1)])
 t=trimesh.Trimesh(np.array(g['vertices']),np.array(faces),process=True)
 if t.volume<0:t.invert()
 return t
lotus=E['SITE_SOUTH_SCREENWALL_V12_LOTUS_DRIP_ENDS']['parts'];tiles=E['SITE_SOUTH_SCREENWALL_BARREL_TILE_ROWS']['parts']
records=[]
for i in range(0,len(lotus),9):
 cap=lotus[i];x=cap['tile_row_x'];side=cap['eave_side']
 candidates=[p for p in tiles if abs(np.array(p['geometry']['vertices'])[:,0].mean()-x)<1e-6]
 tile=candidates[0 if side<0 else -1]
 intersection=trimesh.boolean.intersection([mesh(cap),mesh(tile)],engine='manifold',check_volume=False)
 volume=abs(float(intersection.volume)) if intersection is not None else 0
 records.append(dict(x=x,eave_side=side,cap_tube_intersection_m3=volume,positive_contact=volume>1e-10))
 assert volume>1e-10,(x,side,volume)
R=dict(status='PASS',measured_eave_axes=90,checked_cap_tube_contacts=len(records),all_positive_solid_intersections=True,min_intersection_volume_m3=min(r['cap_tube_intersection_m3'] for r in records),details=records)
(O/'Drip_Contact_QA.json').write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding='utf-8')
Q=json.loads((O/'Geometry_QA.json').read_text(encoding='utf-8'));Q['drip_contact_qa']={k:v for k,v in R.items() if k!='details'}
(O/'Geometry_QA.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in R.items() if k!='details'}))
