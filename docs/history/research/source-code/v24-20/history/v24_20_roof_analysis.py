from v24_20_common import *
from shapely.ops import unary_union
from collections import defaultdict
out={}
for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','SITE_KITCHEN_V11_REGISTERED_EAST_EAVE_STRIP_Geometry','SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry','SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry','SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry']:
 d=source(n);v=d['v'];gs={}
 for t in v[d['f']]:
  nn=np.cross(t[1]-t[0],t[2]-t[0]);l=np.linalg.norm(nn)
  if l<1e-9 or nn[2]/l<.3:continue
  co=np.array([-nn[0]/nn[2],-nn[1]/nn[2],nn@t[0]/nn[2]]);key=tuple(np.round(co,3));g=gs.setdefault(key,{'co':co.tolist(),'tris':[],'area':0});g['tris'].append(t[:,:2].tolist());g['area']+=l/2
 groups=[]
 for g in gs.values():
  if g['area']<.02:continue
  ps=unary_union([Polygon(t)for t in g['tris']]).buffer(0);polys=[ps]if ps.geom_type=='Polygon'else list(ps.geoms);groups.append({'co':g['co'],'area':g['area'],'poly':[list(p.exterior.coords)for p in polys]})
 out[n]={'bounds':[v.min(0).tolist(),v.max(0).tolist()],'groups':groups}
 print(n,out[n]['bounds'],flush=True)
 for g in sorted(groups,key=lambda g:-g['area'])[:12]:print('PLANE',np.round(g['co'],6).tolist(),'AREA',round(g['area'],4),'POLY',g['poly']if 'TILE_COURSES'not in n and 'TIMBER'not in n else len(g['poly']),flush=True)
(D/'Roof_Analysis.json').write_text(json.dumps(out,indent=2))
