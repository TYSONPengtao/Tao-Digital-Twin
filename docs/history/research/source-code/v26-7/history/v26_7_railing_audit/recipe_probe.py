from pathlib import Path
import json,numpy as np
W=Path('work');p=json.loads((W/'v26_1/Prepared_Railing.json').read_text('utf8'))['proof']
for q in p['posts']:print('POST',q['tag'],q['xy'],q['seat_z_m'],q['collar_z_m'],q['ball_center_z_m'])
for fl in p['flights']:print('FLIGHT',fl['floor'],fl['flight'],'START',fl['path'][0],'END',fl['path'][-1])
for fl in [1,2]:
 z=[-.45,3.450024414][fl-1];b=[q['top_z_m']-q['seat_z_m']for q in p['balusters']if q['tag'].startswith(f'F{fl} flight')];print('GRIP_ABOVE_SPINDLE_FOOT',fl,min(b),max(b))
post=next(q for q in p['posts']if q['tag']=='Floor 3');center=np.r_[post['xy'],post['ball_center_z_m']];p0=np.array(p['flights'][-1]['path'][-1]);p1=np.array([7.88,8.65,7.05+1.175]);d0=np.array([.08,.12,.10]);d1=np.array([0,.15,0]);tt=np.linspace(0,1,101);path=np.array([(2*t**3-3*t*t+1)*p0+(t**3-2*t*t+t)*d0+(-2*t**3+3*t*t)*p1+(t**3-t*t)*d1 for t in tt]);i=int(np.argmin(np.linalg.norm(path-center,axis=1)));print('GUARD_NEAR_BALL',center.tolist(),path[i].tolist(),'CENTER_DISTANCE',np.linalg.norm(path[i]-center),'BALL_RADIUS',post['ball_radius_m'],'GRIP_ENVELOPE_CLEARANCE',np.linalg.norm(path[i]-center)-post['ball_radius_m']-.041)
