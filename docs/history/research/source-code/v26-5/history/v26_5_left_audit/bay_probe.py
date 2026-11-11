exec((__import__('pathlib').Path(__file__).parent/'probe.py').read_text('utf8').split('for n in [')[0])
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
hn='V26_3_House_Connected_Walls_And_Stairs';a=np.load(D/I[hn]['file']);house=solid(a['v'],a['f'],hn)
for z in [1.,2.5,4.7,6.1,8.3,9.2]:
 cs=house.slice(z);print('SLICE',z)
 pp=[Polygon(p) for p in cs.to_polygons()];p=unary_union(pp).intersection(box(8.7,.8,13.4,2.5));print(p.wkt)
