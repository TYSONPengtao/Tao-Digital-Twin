from pathlib import Path
import sys,json
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from v24_16_common import solid,cube,union,section
D=W/'v26_4'/'Final'; I={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))}
for n in ['BAY_WINDOW_F1_L_0_Geometry','BAY_WINDOW_F1_L_1_Geometry']:
 r=I[n];a=np.load(D/r['file']);t=a['v'][a['f']];print(n,a.files)
 for j,mat in enumerate(r['materials']):
  ps=t[a['mi']==j].reshape(-1,3);print(mat,'vertices',np.unique(ps,axis=0).tolist())
base=I['BAY_WINDOW_F1_L_0_Geometry'];a=np.load(D/base['file']);G=solid(a['v'],a['f'],'glass assembly')
report=[]
for n,r in I.items():
 if not n.startswith('SITE_COURTYARD_WEST_TILE_WALL_'):continue
 a=np.load(D/r['file']);m=solid(a['v'],a['f'],n);intersection=m^G
 local=m^cube([-.5,.8,1.8],[.7,2.3,2.9]);tr=np.asarray(local.to_mesh64().vert_properties)[:,:3]
 result={'name':n,'intersection_volume_m3':intersection.volume(),'intersection_triangles':intersection.num_tri(),'local_bounds':[] if not len(tr) else [tr.min(0).tolist(),tr.max(0).tolist()]}
 if intersection.num_tri():
  v=np.asarray(intersection.to_mesh64().vert_properties)[:,:3];result['intersection_bounds']=[v.min(0).tolist(),v.max(0).tolist()]
 report.append(result);print(result,flush=True)
(Path(__file__).parent/'intersection_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
