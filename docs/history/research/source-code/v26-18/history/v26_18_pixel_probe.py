from v26_2_common import *
from v26_18_views import VIEWS
tag,pos,aim,lens=VIEWS[0];pos=np.asarray(pos,float);fw=np.asarray(aim)-pos;fw/=np.linalg.norm(fw);right=np.cross(fw,[0.,0.,1.]);right/=np.linalg.norm(right);up=np.cross(right,fw);fp=1100*lens/36
for u,v in[(150,635),(137,626),(914,612),(911,625),(919,602),(900,609),(924,615),(876,626),(968,602)]:
 d=fw+right*((u+.5-550)/fp)+up*((500-v-.5)/fp);d/=np.linalg.norm(d);rows=[]
 for label,fd in[('before','Input'),('after','Prepared')]:
  a=np.load(W/'v26_18'/fd/'V26_3_House_Connected_Walls_And_Stairs.npz');m=solid(a['v'],a['f']);hs=m.ray_cast(pos,pos+d*30);rows.append({'model':label,'hits':[list(h.position)for h in hs[:2]]})
 print('PIXEL',u,v,rows,flush=True)
