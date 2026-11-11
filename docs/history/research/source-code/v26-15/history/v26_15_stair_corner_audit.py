from v26_2_common import *
from collections import defaultdict
D=W/'v26_15';I=D/'Input';J=json.loads((I/'Source_Index.json').read_text('utf8'));r=next(r for r in J['objects']if r['name']=='V26_3_House_Connected_Walls_And_Stairs');a=np.load(I/r['file']);h=solid(a['v'],a['f']);t=a['v'][a['f']];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ar=np.linalg.norm(n,axis=1)/2;n/=np.maximum(2*ar[:,None],1e-30);c=t.mean(1);rows=[]
for label,lo,hi in [('WF',[4.0199,7.4199,-.46],[4.5,7.85,10.25]),('WB',[4.0199,9.25,-.46],[4.5,9.6801,10.25]),('EF',[8.5,7.4199,-.46],[8.9801,7.85,10.25]),('EB',[8.5,9.25,-.46],[8.9801,9.6801,10.25])]:
 d=defaultdict(list);mask=np.all(c>lo,1)&np.all(c<hi,1)
 for k in np.flatnonzero(mask):
  ax=int(np.argmax(abs(n[k])))
  if abs(n[k,ax])<.9999:continue
  d[(ax,round(float(c[k,ax]),6),int(np.sign(n[k,ax])),r['materials'][a['mi'][k]])].append(k)
 for key,ids in d.items():
  tt=t[ids];row={'corner':label,'plane':key,'area':float(ar[ids].sum()),'bounds':[tt.min((0,1)).tolist(),tt.max((0,1)).tolist()]};rows.append(row)
  if row['area']>.0002:print(row,flush=True)
(D/'Stair_Corner_Audit.json').write_text(json.dumps(rows,indent=2),'utf8')
print('CORNER_AUDIT_DONE',flush=True)
