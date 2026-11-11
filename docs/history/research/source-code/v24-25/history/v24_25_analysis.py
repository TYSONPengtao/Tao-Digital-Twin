from v24_25_common import *
from shapely.ops import unary_union
out={}
for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','SITE_KITCHEN_V11_REGISTERED_EAST_EAVE_STRIP_Geometry','V24_20_Two_Rooms_Continuous_Valley_Roof_Bed','V24_20_Kitchen_Unified_Pan_Barrel_Slope_0']:
 d=source(n);v=d['v'];gs={}
 for t in v[d['f']]:
  no=np.cross(t[1]-t[0],t[2]-t[0]);a=np.linalg.norm(no)/2
  if a<1e-8 or no[2]<.6*2*a:continue
  co=np.array([-no[0]/no[2],-no[1]/no[2],no@t[0]/no[2]]);key=tuple(np.round(co,3));g=gs.setdefault(key,{'co':co.tolist(),'tris':[],'area':0});g['tris'].append(t[:,:2].tolist());g['area']+=a
 groups=[]
 for g in gs.values():
  if g['area']<.02:continue
  p=unary_union([Polygon(t)for t in g['tris']]).buffer(0);ps=[p]if p.geom_type=='Polygon'else list(p.geoms);groups.append({'co':g['co'],'area':g['area'],'poly':[list(q.exterior.coords)for q in ps],'holes':[[list(h.coords)for h in q.interiors]for q in ps]})
 out[n]={'bounds':[v.min(0).tolist(),v.max(0).tolist()],'groups':groups}
 print(n,'GROUPS',len(groups),flush=True)
 for g in sorted(groups,key=lambda g:-g['area'])[:18]:print('PLANE',np.round(g['co'],6).tolist(),'AREA',round(g['area'],4),'POLYS',len(g['poly']),flush=True)
(D/'Roof_Analysis.json').write_text(json.dumps(out,indent=2))
