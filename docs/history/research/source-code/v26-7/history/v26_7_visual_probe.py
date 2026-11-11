from v26_2_common import *
FD=W/'v26_7/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};a=np.load(FD/J['V26_3_House_Connected_Walls_And_Stairs']['file']);m=solid(a['v'],a['f'])
eye=np.array([6.7,8.4,4.85]);F=np.array([4.,9.3,3.65])-eye;F/=np.linalg.norm(F);R=np.cross(F,[0,0,1]);R/=np.linalg.norm(R);U=np.cross(R,F)
for x,y in[(170,570),(180,590),(195,610),(175,630),(245,866),(190,610),(160,590)]:
 d=F+(2*x/1100-1)*(36/38)*R+(1-2*y/950)*(36/38)*(950/1100)*U;d/=np.linalg.norm(d);hs=m.ray_cast(eye,eye+d*30)
 print('PIXEL',x,y,[(list(h.position),list(h.normal))for h in hs[:3]],flush=True)
