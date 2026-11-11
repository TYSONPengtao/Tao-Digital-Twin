import sys,json,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,manifold3d as mf
D=W/'v24_10';O=Path('E:/jz/JIA/Rebuild_V24_10');idx=json.loads((D/'Solid_Export_Index.json').read_text());rows=[]
for r in idx['objects']:
 d=np.load(D/r['file']);trials=[];passed=False
 for dec in[9,8,7,6,5]:
  v,iv=np.unique(np.round(d['v'],dec),axis=0,return_inverse=True);f=iv[d['f']];valid=(f[:,0]!=f[:,1])&(f[:,0]!=f[:,2])&(f[:,1]!=f[:,2]);f=f[valid];t=v[f];valid2=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-13;f=f[valid2];m=mf.Manifold(mf.Mesh64(np.ascontiguousarray(v),np.array(f,dtype=np.uint64,order='C')));trials.append({'precision_m':10.**(-dec),'status':str(m.status()),'discarded_zero_area_triangles':len(d['f'])-len(f),'volume_m3':m.volume()})
  if m.status()==mf.Error.NoError and m.volume()>0:
   passed=True;break
 rows.append({'name':r['name'],'pass':passed,'status':str(m.status()),'coordinate_precision_m':10.**(-dec),'volume_m3':m.volume(),'trials':trials})
 if not passed:print('SOLID_FAIL',r['name'],trials[-1],flush=True)
out={'status':'PASS_INDEPENDENT_SAVED_SOLIDS'if all(r['pass']for r in rows)else'FAIL_INDEPENDENT_SAVED_SOLIDS','model_sha256':idx['model_sha256'],'method':'Independent closed-oriented-solid reconstruction from the saved file; coincident UV-split coordinates normalized at 1nm..10um and zero-area triangles discarded; all nondegenerate boundaries must close','solids':rows};(O/'Reports/V24_10_Independent_Solid_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out['status'],len(rows),sum(not r['pass']for r in rows),flush=True)
