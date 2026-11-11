import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,manifold3d as mf
D=W/'v24_10';idx=json.loads((D/'QA_Obstacle_Index.json').read_text());results=[];sol=[]
for r in idx:
 d=np.load(D/r['file']);v,iv=np.unique(np.round(d['v'],7),axis=0,return_inverse=True);f=iv[d['f']];m=mf.Manifold(mf.Mesh64(v,np.array(f,dtype=np.uint64,order='C')));results.append({'name':r['name'],'status':str(m.status()),'volume_m3':m.volume()});sol.append((r['name'],m))
boxes=[('Entry',[12.5,-15.63,-.37],[1.55,.65,2.02]),('Veranda',[13.8,-15.60,-.37],[4.45,.60,2.02]),('Storage room door',[15.64,-15.00,-.37],[.60,.45,1.95]),('East eave end',[18.47,-15.61,-.37],[.45,.59,2.02])]
hits=[]
for label,lo,sz in boxes:
 box=mf.Manifold.cube(sz).translate(lo);rows=[]
 for n,m in sol:
  if m.status()!=mf.Error.NoError:continue
  vol=(m^box).volume()
  if vol>1e-7:rows.append({'name':n,'obstruction_m3':vol})
 hits.append({'label':label,'origin':lo,'size':sz,'obstructions':rows})
good=all(r['status']=='Error.NoError'and r['volume_m3']>0 for r in results)and all(not r['obstructions']for r in hits)
model_sha=json.loads((D/'Solid_Export_Index.json').read_text())['model_sha256']
out={'status':'PASS_INDEPENDENT_CLEARANCE'if good else 'FAIL_INDEPENDENT_CLEARANCE','model_sha256':model_sha,'solids':results,'clearance_boxes':hits};(D/'Independent_Clearance_QA.json').write_text(json.dumps(out,indent=2),encoding='utf8');(Path('E:/jz/JIA/Rebuild_V24_10/Reports')/'V24_10_Independent_Clearance_QA.json').write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(out),flush=True)
