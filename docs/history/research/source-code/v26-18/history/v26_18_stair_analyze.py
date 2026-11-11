from v26_2_common import *
from collections import defaultdict
FD=W/'v26_17/Final';jr=next(r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))if r['name']=='V26_3_House_Connected_Walls_And_Stairs');a=np.load(FD/jr['file']);v,f=a['v'],a['f'];t=v[f];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(no,axis=1)/2;no/=np.maximum(2*area[:,None],1e-30);m=solid(v,f);mats=jr['materials']
mask=(t[:,:,0].max(1)>4.0)&(t[:,:,0].min(1)<9.01)&(t[:,:,1].max(1)>7.3)&(t[:,:,1].min(1)<9.82)&(t[:,:,2].max(1)>-.4)&(t[:,:,2].min(1)<3.46)&(no[:,2]<-.1)
g=defaultdict(lambda:{'area':0.,'ids':[]})
for i in np.flatnonzero(mask):
 k=(tuple(np.round(no[i],4)),round(float(no[i]@t[i,0]),4),mats[a['mi'][i]]);g[k]['area']+=float(area[i]);g[k]['ids'].append(int(i))
out=[]
for k,r in sorted(g.items(),key=lambda kv:-kv[1]['area']):
 tt=t[r['ids']];out.append({'normal':k[0],'plane':k[1],'material':k[2],'area':r['area'],'bounds':[tt.min((0,1)).tolist(),tt.max((0,1)).tolist()],'faces':r['ids']})
for r in out[:35]:print('UNDER_PLANE',{k:v for k,v in r.items()if k!='faces'},flush=True)
profiles=[]
for y in[7.5,7.9,8.3,8.55,8.8,9.1,9.5,9.7]:
 rr=[]
 for x in np.linspace(4.2,8.9,20):
  hits=m.ray_cast([x,y,-.2],[x,y,3.6]);rr.append([round(float(x),3),[round(float(h.position[2]),6)for h in hits]])
 profiles.append({'y':y,'samples':rr});print('PROFILE',y,rr,flush=True)
idx=json.loads((W/'v26/Geometry_Index.json').read_text('utf8'));original=[{'name':r['name'],'bounds':r['bounds']}for r in idx if r['name'].startswith(('STAIR_','SLAB_JOINED'))];print('ORIGINAL_STAIR_BOUNDS',original,flush=True)
D=W/'v26_18';D.mkdir(exist_ok=True);(D/'Stair_Analysis.json').write_text(json.dumps({'planes':out,'profiles':profiles,'original_bounds':original},ensure_ascii=False,indent=2),'utf8')
