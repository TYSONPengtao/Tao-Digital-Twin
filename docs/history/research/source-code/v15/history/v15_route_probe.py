import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,export_v5 as ex
B=Path(r'E:/jz/JIA/Rebuild_V14');S=json.loads((B/'08_Editable_Source/Architecture_Scene_V14.json').read_text(encoding='utf8'));ex.SCENE=S;Q=json.loads((W/'v15/Mutation.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']};E.update({e['name']:e for e in Q['replace']+Q['add']})
def tris(e):
 out=[]
 for pp in e['parts']:
  v,fs=ex.world_part(pp,e)
  for f in fs:
   for t in ex.triangulate(v[f]) if len(f)>3 else [[0,1,2]]:out.append(v[[f[i] for i in t]])
 t=np.array(out);nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);return t[nn[:,2]>1e-8]
def heights(t,xy):
 a=t[:,0,:2];d=t[:,1,:2]-a;b=t[:,2,:2]-a;q=np.array(xy)-a;det=d[:,0]*b[:,1]-d[:,1]*b[:,0];safe=abs(det)>1e-10;u=np.divide(q[:,0]*b[:,1]-q[:,1]*b[:,0],det,out=np.zeros(len(t)),where=safe);v=np.divide(d[:,0]*q[:,1]-d[:,1]*q[:,0],det,out=np.zeros(len(t)),where=safe);keep=safe&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8);return (t[:,0,2]+u*(t[:,1,2]-t[:,0,2])+v*(t[:,2,2]-t[:,0,2]))[keep]
road=tris(E['SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT']);soil=np.concatenate([tris(e) for e in E.values() if e['name'].startswith(('SITE_V12_REBUILT_EARTH','SITE_V12_REBUILT_ROAD'))]);rows=[]
for xy in [[-13.5,-10.6],[-12.8,-10.3],[-10.2,-11.13],[-8,-11.66],[-5,-12.28],[-3,-12.7],[0,-12.7],[3,-12.7],[6.6,-12.7],[6.6,-11.75],[6.6,-10.9]]:
 hr=heights(road,xy);hs=heights(soil,xy);rows.append({'xy':xy,'road':hr.tolist(),'soil':hs.tolist(),'soil_above_road':bool(len(hr) and len(hs) and hs.max()>hr.max()+.003)})
print(json.dumps(rows,indent=2),flush=True);(W/'v15/Route_Probe.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
