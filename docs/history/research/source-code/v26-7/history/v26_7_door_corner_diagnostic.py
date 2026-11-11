from v26_2_common import *
from v26_7_views import VIEWS
FD=W/'v26_7/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';a=np.load(FD/J[HN]['file']);m=solid(a['v'],a['f']);_,pos,aim,lens=VIEWS[2];eye=np.array(pos);F=np.array(aim)-eye;F/=np.linalg.norm(F);R=np.cross(F,[0,0,1]);R/=np.linalg.norm(R);U=np.cross(R,F)
for x,y in[(555,500),(570,500),(600,500),(615,500),(580,700),(500,500),(650,500)]:
 d=F+(2*x/1100-1)*(36/(2*lens))*R+(1-2*y/950)*(36/(2*lens))*(950/1100)*U;d/=np.linalg.norm(d);hs=m.ray_cast(eye,eye+d*30);print('PIXEL',x,y,[(list(h.position),list(h.normal))for h in hs[:2]],flush=True)
