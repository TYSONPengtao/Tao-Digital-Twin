from pathlib import Path
import sys,json
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
D=Path(__file__).parent;F=W/'v26_6/Final'
I={r['name']:r for r in json.loads((F/'Geometry_Index.json').read_text('utf8'))}
r=I['V26_2_Continuous_Ground_And_Perimeter_Shell'];a=np.load(F/r['file'])
route=json.loads((W/'v24_20/Prepared_Geometry.json').read_text('utf8'))['wall_uv_route']
code=(W/'v26_2_site.py').read_text('utf8');cl=code[code.index('class ArcMap:'):code.index('mapper=ArcMap(route)')]
exec(cl,globals());mapper=ArcMap(route)
for ix in np.flatnonzero(a['mi']==r['materials'].index('M_V26_2_Continuous_Exterior_Strata')):
 t=a['v'][a['f'][ix]];normal=np.cross(t[1]-t[0],t[2]-t[0]);normal/=max(np.linalg.norm(normal),1e-30)
 if abs(normal[2])>.85:continue
 nh=normal[:2]/max(np.linalg.norm(normal[:2]),1e-15);q=t[:,:2].mean(0);key=(*np.round(nh,4),round(float(q@nh),3))
 if key in mapper.planes:continue
 E=t[1:,:2]-t[0,:2];delta=a['uv'][ix,1:,0]-a['uv'][ix,0,0]
 # Vertical faces have rank one in XY; least squares gives their tangent.
 tangent=np.linalg.lstsq(E,delta,rcond=None)[0]
 if not .98<np.linalg.norm(tangent)<1.02:continue
 mapper.planes[key]=(tangent,float(a['uv'][ix,0,0]-t[0,:2]@tangent))
result={}
for k,mat in enumerate(r['materials']):
 if not mat.startswith('M_V26_3_Secondary_Original_Photo_'):continue
 ids=np.flatnonzero(a['mi']==k);tt=a['v'][a['f'][ids]]
 rows=[]
 for t in tt:
  uv=mapper.triangle(t);E=t[1:]-t[0];delta=uv[1:,0]-uv[0,0]
  grad=E.T@np.linalg.solve(E@E.T,delta);offset=uv[0,0]-t[0]@grad
  rows.append((grad,offset))
 # Each V26.3 affine material corresponds to one native triangle.
 assert len(rows)==1,(mat,len(rows))
 grad,offset=rows[0]
 result[mat]={'gradient_world':grad.tolist(),'offset_m':float(offset),'source_uv_x':a['uv'][ids[0],:,0].tolist(),'new_arc_uv_x':mapper.triangle(tt[0])[:,0].tolist(),'bounds_m':[tt.min((0,1)).tolist(),tt.max((0,1)).tolist()]}
(D/'Lower_Strata_Continuous_Arc_Mapping.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print('LOWER_MAPPING',len(result),'u_range',min(min(r['new_arc_uv_x'])for r in result.values()),max(max(r['new_arc_uv_x'])for r in result.values()),'old_u',min(min(r['source_uv_x'])for r in result.values()),max(max(r['source_uv_x'])for r in result.values()))
