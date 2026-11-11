import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,rhino3dm as rh
O=Path(r'E:\jz\JIA\Rebuild_V13');C=json.loads((O/'02_Data/Coordinate.json').read_text(encoding='utf8'));a=math.radians(C['rotation_deg']);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);origin=np.array(C['origin'])
F=rh.File3dm.Read(str(O/'04_Rhino/Architecture_Complete_V13_ALIGNED_ENU.3dm'));I=json.loads((O/'02_Data/Native_Readback_Index_V13.json').read_text(encoding='utf8'));by={r['name']:r for r in I};checks=[]
for ob in F.Objects:
 at=ob.Attributes;n=at.Name.rsplit('__',1)[0]
 if not n.startswith(('SITE_V12_REBUILT_EARTH','SITE_V12_REBUILT_ROAD')):continue
 g=ob.Geometry;v=(np.array([[q.X,q.Y,q.Z] for q in g.Vertices.ToPoint3dArray()])-origin)@R;nn=np.array([[q.X,q.Y,q.Z] for q in g.Normals])@R;path=O/'02_Data'/by[n]['file'];d=np.load(path);arrays={k:d[k] for k in d.files};err=float(np.max(abs(v-arrays['vertices'])));assert err<1e-9 and len(nn)==len(v),(n,err);nn/=np.maximum(np.linalg.norm(nn,axis=1)[:,None],1e-30);arrays['normals']=nn;np.savez_compressed(path,**arrays);checks.append({'name':n,'vertex_order_max_error_m':err,'normals':len(nn),'source':'Delivered native mesh vertex normals, transformed ENU to LOCAL'})
(O/'06_Report/Native_Preview_Ground_Normal_QA.json').write_text(json.dumps({'status':'PASS','geometry_changed':False,'native_3dm_rewritten':False,'checks':checks,'note':'Preserve the previously harmonized actual Rhino normal field in the diagnostic preview; do not smooth each separate terrain panel independently.'},ensure_ascii=False,indent=2),encoding='utf8');print('copied actual native normal fields',len(checks),flush=True)
