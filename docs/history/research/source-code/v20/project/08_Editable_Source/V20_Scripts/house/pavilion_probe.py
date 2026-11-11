from pathlib import Path
exec((Path(__file__).parent/'inventory.py').read_text().split('rows=[]')[0])
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
ii={r['name']:r for r in I}
def fp(n):
 d=np.load(B/'02_Data'/ii[n]['file']);v=d['vertices'];t=v[d['faces']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);p=unary_union([Polygon(q[:,:2]) for q in t[no[:,2]>1e-9]]).buffer(0);return p,v,t,no
domain=box(-.30,-8.40,5.3,-3.0);rows=[]
for n in ii:
 if not n.startswith('SITE_V12_REBUILT_COURT') and n not in ['SITE_GAZEBO_V11_STONE_PLATFORM','SITE_V16_GRADED_INTERIOR_SOIL']:continue
 p,v,t,no=fp(n)
 area=domain.intersection(p).area
 if area<1e-8:continue
 print(n,'bbox',np.round([v.min(0),v.max(0)],4).tolist(),'localarea',area,'coveredtest',[[q,p.covers(Point(q))] for q in [[2,-5],[.1,-5],[4.75,-5],[5.1,-5],[2,-3.2]]])
 rows.append({'name':n,'bbox':[v.min(0).tolist(),v.max(0).tolist()],'intersection_area':area,'footprint_geometry':p.__geo_interface__})
 print('LOCAL missingpolygon',domain.difference(p).simplify(.001).__geo_interface__)
(Path(__file__).parent/'Pavilion_Ground_Probe.json').write_text(json.dumps(rows),encoding='utf8')
