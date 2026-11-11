import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,manifold3d as mf
D=W/'v24_17';R=Path('E:/jz/JIA/Rebuild_V24_17/Reports');gi=json.loads((D/'Gate_Export_Index.json').read_text());si=json.loads((D/'Solid_Export_Index.json').read_text());idx={r['name']:r for r in si['objects']}
def m(file):
 d=np.load(D/file);v=d['v'];f=d['f'];a=mf.Manifold(mf.Mesh64(np.array(v,dtype=np.float64,order='C'),np.array(f,dtype=np.uint64,order='C')))
 if a.status()==mf.Error.NoError:return a
 for dec in [9,8,7,6]:
  vv,ix=np.unique(np.round(v,dec),axis=0,return_inverse=True);ff=ix[f];t=vv[ff];ff=ff[np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-13];a=mf.Manifold(mf.Mesh64(np.array(vv,dtype=np.float64,order='C'),np.array(ff,dtype=np.uint64,order='C')))
  if a.status()==mf.Error.NoError:return a
 raise RuntimeError((file,a.status()))
gate=mf.Manifold.batch_boolean([m(r['file'])for r in gi['objects']],mf.OpType.Add);checks=[]
for n in ['V24_Kitchen_Gable_Upper_Brick_Infill','V24_Kitchen_Curved_Gable_Coping','SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry']:
 v=(m(idx[n]['file'])^gate).volume();checks.append({'check':'Kitchen front clears accepted gate roof / '+n,'pass':abs(v)<1e-6,'overlap_m3':v})
assert gi['model_sha256']==si['model_sha256'];out={'status':'PASS_GATE_JUNCTION'if all(r['pass']for r in checks)else'FAIL_GATE_JUNCTION','model_sha256':gi['model_sha256'],'checks':checks};(R/'V24_17_Gate_Junction_QA.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
