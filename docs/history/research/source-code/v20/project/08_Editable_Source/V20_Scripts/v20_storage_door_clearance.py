import sys,json,math,copy
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1')]
import numpy as np
D=W/'v20';Q=json.loads((D/'Mutation.json').read_text(encoding='utf8'));DM=json.loads((D/'Door_Manifest.json').read_text(encoding='utf8'))
def rot(v,p,d):
 a=math.radians(d);r=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);p=np.array(p);return (np.array(v)-p)@r.T+p
for e in Q['add']:
 if not e['name'].startswith('DOOR_STORAGE'):continue
 p=e['pivot_world_m'];deg=e['open_angle_degrees'];ps=copy.deepcopy(e['parts'])
 for q in ps:q['geometry']['vertices']=rot(q['geometry']['vertices'],p,-deg).tolist()
 vv=np.vstack([q['geometry']['vertices'] for q in ps]);newp=list(p);newp[1]=float(vv[:,1].max()+.013)
 for q in ps:q['geometry']['vertices']=rot(q['geometry']['vertices'],newp,deg).tolist()
 e['parts']=ps;e['pivot_world_m']=newp;e['v20_hinge_clearance']='Interior face plus 13 mm to clear existing timber reveal; closed leaf footprint retained'
 row=next(r for r in DM['doors'] if r['name']==e['name']);row['hinge_local_m']=newp
(D/'Mutation.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');(D/'Door_Manifest.json').write_text(json.dumps(DM,ensure_ascii=False,indent=2),encoding='utf8');print('STORAGE HINGES CORRECTED')
