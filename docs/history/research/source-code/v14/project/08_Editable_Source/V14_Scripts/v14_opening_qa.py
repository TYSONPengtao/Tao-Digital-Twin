import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1')]
import numpy as np
O=Path(r'E:/jz/JIA/Rebuild_V14');I=json.loads((O/'02_Data/Native_Readback_Index_V14.json').read_text(encoding='utf8'))
tests=[]
for y in [6.28,6.60,6.93]:
 for z in [7.70,8.40,9.30]:tests.append(('terrace_exit',[3.0,y,z],[1,0,0],1.5))
for x in [8.15,8.45,8.75]:
 for z in [7.70,8.40,9.30]:tests.append(('study_entry',[x,5.5,z],[0,1,0],1.5))
tests.append(('continuous_hall',[8.55,6.60,8.40],[-1,0,0],5.25))
records=[{'opening':label,'start_local_m':a,'direction':di,'length_m':L,'closed_door_hits':[],'obstructions':[]} for label,a,di,L in tests]
column=None
for row in I:
 n=row['name'];d=np.load(O/'02_Data'/row['file']);v=d['vertices'];b=np.array([v.min(0),v.max(0)])
 if n=='KZ_2_2_F3':column=b.tolist()
 for j,(label,a,di,L) in enumerate(tests):
  a=np.array(a);di=np.array(di);seg=np.array([a,a+di*L])
  if not(np.all(b[1]>=seg.min(0)) and np.all(b[0]<=seg.max(0))):continue
  t=v[d['faces']];u=t[:,1]-t[:,0];vv=t[:,2]-t[:,0];hh=np.cross(np.tile(di,(len(t),1)),vv);det=np.einsum('ij,ij->i',u,hh);keep=abs(det)>1e-10;inv=np.zeros(len(t));inv[keep]=1/det[keep];s=a-t[:,0];p=np.einsum('ij,ij->i',s,hh)*inv;q=np.cross(s,u);r=q@di*inv;dist=np.einsum('ij,ij->i',vv,q)*inv;hit=keep&(p>=0)&(r>=0)&(p+r<=1)&(dist>.001)&(dist<L)
  if hit.any():
   rec={'node':n,'distance_m':np.unique(np.round(dist[hit],6)).tolist()}
   key='closed_door_hits' if n in ['DOOR_LAUNDRY_F3__LEAF','DOOR_STUDY_F3__LEAF'] else 'obstructions';records[j][key].append(rec)
bad=[r for r in records if r['obstructions']]
Q={'status':'PASS_CLEAR_OPENINGS' if not bad else 'FAIL','method':'Actual V14 native readback mesh segment intersections; closed door leaves classified separately. No finish, wall or column allowed across sampled clear opening. This is geometry inspection, not regulatory clearance certification.','rays':records,'failures':bad,'exit_y_range_local_m':[6.15,7.05],'retained_column_name':'KZ_2_2_F3','retained_column_bounds_local_m':column,'hall_clear_width_m':1.15,'exit_to_column_clearance_y_m':None if column is None else column[0][1]-7.05}
(W/'v14/Opening_QA.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'status':Q['status'],'rays':len(records),'failures':bad,'column_clearance':Q['exit_to_column_clearance_y_m']},ensure_ascii=False),flush=True)
assert not bad
