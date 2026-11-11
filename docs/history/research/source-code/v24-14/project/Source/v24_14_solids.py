import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,manifold3d as mf
D=W/'v24_14';R=Path('E:/jz/JIA/Rebuild_V24_14/Reports');idx=json.loads((D/'Solid_Export_Index.json').read_text());results=[];solids={};rows={r['name']:r for r in idx['objects']}
def solid(d):
 trials=[];raw=mf.Manifold(mf.Mesh64(np.array(d['v'],dtype=np.float64,order='C'),np.array(d['f'],dtype=np.uint64,order='C')));trials.append({'method':'saved_vertex_indices','status':str(raw.status()),'volume_m3':raw.volume()})
 if raw.status()==mf.Error.NoError and raw.volume()>0:return raw,trials
 for dec in [9,8,7,6,5]:
  v,ix=np.unique(np.round(d['v'],dec),axis=0,return_inverse=True);f=ix[d['f']];t=v[f];ok=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-13;f=f[ok];m=mf.Manifold(mf.Mesh64(np.array(v,dtype=np.float64,order='C'),np.array(f,dtype=np.uint64,order='C')));trials.append({'coordinate_precision_m':10.**-dec,'status':str(m.status()),'volume_m3':m.volume(),'removed_zero_area_faces':int((~ok).sum())})
  if m.status()==mf.Error.NoError and m.volume()>0:return m,trials
 return m,trials
for row in idx['objects']:
 m,tr=solid(np.load(D/row['file']));passed=m.status()==mf.Error.NoError and m.volume()>0;solids[row['name']]=m;results.append({'name':row['name'],'pass':passed,'closed_bodies':len(m.decompose())if passed else 0,'trials':tr});print('SOLID',row['name'],passed,flush=True)
checks=[]
def ck(n,vol,limit=1e-7):checks.append({'check':n,'pass':abs(vol)<limit,'overlap_m3':vol})
wood=solids['SITE_V17_STORAGE_CONNECTED_TIMBER_ASSEMBLY_Geometry'];roof=solids['SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry'];ck('Retained timber does not penetrate roof tiles',float((wood^roof).volume()))
for i in [1,2]:
 post=solids[f'V24_11_Storage_Veranda_Column_{i}'];walls=[solids['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'],solids['V24_14_Storage_West_Sealed_Gable'],solids['V24_14_Storage_East_Sealed_Gable']]
 for j,m in enumerate(walls):ck(f'Round post {i} clear of masonry {j}',float((post^m).volume()))
for side,lo,hi in [('west',[13.13,-16.10,2.50],[13.204,-8.7,5.5]),('east',[18.686,-16.10,2.50],[19.1,-8.7,5.5])]:
 box=mf.Manifold.cube(np.array(hi)-lo).translate(lo);ck('No roof timber projecting through '+side+' exterior gable',float((wood^box).volume()))
good=all(r['pass']for r in results+checks);out={'status':'PASS_INDEPENDENT_SAVED_SOLIDS'if good else'FAIL_INDEPENDENT_SAVED_SOLIDS','model_sha256':idx['model_sha256'],'solids':results,'spatial_checks':checks};(R/'V24_14_Independent_Solid_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
boxes=[('Entry',[12.5,-15.63,-.37],[1.30,.65,2.02]),('Continuous veranda',[13.8,-15.58,-.37],[4.25,.60,2.02]),('End post bypass',[18.02,-15.35,-.37],[.45,.33,2.02]),('Recessed door opening',[15.64,-14.52,-.37],[.60,.45,1.95]),('East end portal',[18.47,-15.61,-.37],[.45,.59,2.02])];route=[]
for label,lo,sz in boxes:
 box=mf.Manifold.cube(sz).translate(lo);hits=[]
 for n,m in solids.items():
  if not rows[n]['obstacle']:continue
  if m.status()!=mf.Error.NoError:hits.append({'object':n,'error':str(m.status())});continue
  vol=(m^box).volume()
  if vol>1e-7:hits.append({'object':n,'overlap_m3':vol})
 route.append({'label':label,'origin':lo,'size':sz,'obstructions':hits})
good=all(not r['obstructions']for r in route);out={'status':'PASS_INDEPENDENT_CLEARANCE'if good else'FAIL_INDEPENDENT_CLEARANCE','model_sha256':idx['model_sha256'],'samples':route};(R/'V24_14_Independent_Clearance_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out['status'],flush=True)
for r in results+checks:
 if not r['pass']:print('FAIL',r,flush=True)
for r in route:
 if r['obstructions']:print('BLOCKED',r,flush=True)
