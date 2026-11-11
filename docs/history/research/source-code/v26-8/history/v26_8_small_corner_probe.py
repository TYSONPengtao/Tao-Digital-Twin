from v26_2_common import *
D=W/'v26_8/Final';J={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};a=np.load(D/J['V26_3_House_Connected_Walls_And_Stairs']['file']);m=solid(a['v'],a['f']);eye=np.array([6.4,8.55,9.4])
for x,y in[(905,720),(915,720),(930,740),(910,735),(890,715)]:
 d=np.array([(2*x/1100-1)*36/44,(1-2*y/950)*36/44*950/1100,-1.]);h=m.ray_cast(eye,eye+d*20)[0];print(x,y,list(h.position),list(h.normal))
