import sys,json,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,manifold3d as mf
D=W/'v24_11';R=Path('E:/jz/JIA/Rebuild_V24_11/Reports');idx=json.loads((D/'Solid_Export_Index.json').read_text());results=[]
def solid(d):
 trials=[]
 for dec in[9,8,7,6,5]:
  v,iv=np.unique(np.round(d['v'],dec),axis=0,return_inverse=True);f=iv[d['f']];ok=(f[:,0]!=f[:,1])&(f[:,0]!=f[:,2])&(f[:,1]!=f[:,2]);f=f[ok];t=v[f];ok=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-13;f=f[ok];m=mf.Manifold(mf.Mesh64(np.ascontiguousarray(v),np.array(f,dtype=np.uint64,order='C')));trials.append({'precision_m':10.**(-dec),'status':str(m.status()),'discarded_zero_area_triangles':len(d['f'])-len(f),'volume_m3':m.volume()})
  if m.status()==mf.Error.NoError and m.volume()>0:break
 return m,trials,dec
for r in idx['objects']:
 m,trial,dec=solid(np.load(D/r['file']));passed=m.status()==mf.Error.NoError and m.volume()>0;results.append({'name':r['name'],'pass':passed,'status':str(m.status()),'coordinate_precision_m':10.**(-dec),'volume_m3':m.volume(),'trials':trial});print('SOLID',r['name'],passed,flush=True)
out={'status':'PASS_INDEPENDENT_SAVED_SOLIDS'if all(r['pass']for r in results)else'FAIL_INDEPENDENT_SAVED_SOLIDS','model_sha256':idx['model_sha256'],'method':'Independent oriented-solid reconstruction from freshly saved Blender world vertices; coincident UV split coordinates normalized at 1nm..10um, zero-area triangles removed','solids':results};(R/'V24_11_Independent_Solid_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
obs=[];states=[]
for r in json.loads((D/'QA_Obstacle_Index.json').read_text()):
 m,t,dec=solid(np.load(D/r['file']));obs.append((r['name'],m));states.append({'name':r['name'],'pass':m.status()==mf.Error.NoError and m.volume()>0,'status':str(m.status())})
boxes=[('Entry',[12.5,-15.63,-.37],[1.30,.65,2.02]),('Gallery main route',[13.8,-15.58,-.37],[4.25,.60,2.02]),('Bypass north of the end column',[18.02,-15.35,-.37],[.45,.33,2.02]),('Storage room door',[15.64,-15.00,-.37],[.60,.45,1.95]),('East end portal',[18.47,-15.61,-.37],[.45,.59,2.02])];hits=[]
for label,lo,sz in boxes:
 box=mf.Manifold.cube(sz).translate(lo);rr=[]
 for n,m in obs:
  if m.status()!=mf.Error.NoError:continue
  v=(m^box).volume()
  if v>1e-7:rr.append({'object':n,'obstruction_m3':v})
 hits.append({'label':label,'origin':lo,'size':sz,'obstructions':rr})
good=all(r['pass']for r in states)and all(not r['obstructions']for r in hits);out={'status':'PASS_INDEPENDENT_CLEARANCE'if good else'FAIL_INDEPENDENT_CLEARANCE','model_sha256':idx['model_sha256'],'obstacle_solids':states,'clearance_samples':hits,'note':'Sampling of the corrected model, not surveyed passage dimensions or a code assessment'};(R/'V24_11_Independent_Clearance_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out['status'],json.dumps(hits),flush=True)
