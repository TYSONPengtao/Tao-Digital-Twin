import sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
O=Path(r'E:/jz/JIA/Rebuild_V10_Hybrid')
S=json.loads((O/'08_Editable_Source/05_Intermediate/Architecture_Scene.json').read_text(encoding='utf-8'));E={e['name']:e for e in S['elements']};I={r['name']:r for r in json.loads((O/'02_Data/Patch_Index.json').read_text(encoding='utf-8'))}
rows=[]
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0','SITE_PERIMETER_JOINED_RETAINING_WALL_1']:
 e=E[n];centers=[];bodyps=[]
 for p in e['parts'][::2]:
  v=np.array(p['geometry']['vertices']);aa=(v[0,:2]+v[3,:2])/2;bb=(v[1,:2]+v[2,:2])/2
  if not centers:centers.append(aa.tolist())
  centers.append(bb.tolist());bodyps.append(Polygon(v[:4,:2]))
 P=unary_union(bodyps);r=I.get(n);PN=None
 if r:
  a=np.load(O/'02_Data'/r['file']);v=a['vertices'];ps=[]
  for f in a['faces']:
   q=Polygon(v[f,:2])
   if q.area>1e-12:ps.append(q)
  PN=unary_union(ps)
 line=LineString(centers);missing=P.difference(PN) if PN is not None else P
 stations=[]
 for s in np.linspace(0,line.length,1001):
  pp=line.interpolate(s)
  if missing.covers(pp):stations.append(float(s))
 row=dict(name=n,centerline=centers,length_m=line.length,full_body_projection_m2=P.area,hybrid_patch_projection_m2=PN.area if PN is not None else 0,fullbody_outside_existing_patch_m2=missing.area,current_body_patch_file=r['file'] if r else None,missing_centerline_station_ranges_approx_m=[min(stations),max(stations)] if stations else [],body_part_count=len(e['parts']),detail_nodes=[(ee['name'],len(ee['parts'])) for ee in S['elements'] if ee['name'].startswith(n)])
 rows.append(row)
 print(json.dumps(row,ensure_ascii=False))
(Path(__file__).parent/'Wall_Current_Clip_Audit.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')

