import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,manifold3d as mf
D=W/'v24_15';R=Path('E:/jz/JIA/Rebuild_V24_15/Reports');idx=json.loads((D/'Solid_Export_Index.json').read_text());results=[];solids={};rows={r['name']:r for r in idx['objects']}
def solid(d):
 trials=[];m=mf.Manifold(mf.Mesh64(np.array(d['v'],dtype=np.float64,order='C'),np.array(d['f'],dtype=np.uint64,order='C')));trials.append({'method':'saved_vertex_indices','status':str(m.status()),'volume_m3':m.volume()})
 if m.status()==mf.Error.NoError and m.volume()>0:return m,trials
 for dec in [9,8,7,6,5]:
  v,ix=np.unique(np.round(d['v'],dec),axis=0,return_inverse=True);f=ix[d['f']];t=v[f];ok=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-13;f=f[ok];m=mf.Manifold(mf.Mesh64(np.array(v,dtype=np.float64,order='C'),np.array(f,dtype=np.uint64,order='C')));trials.append({'coordinate_precision_m':10.**-dec,'status':str(m.status()),'volume_m3':m.volume()})
  if m.status()==mf.Error.NoError and m.volume()>0:return m,trials
 return m,trials
def union(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
for row in idx['objects']:
 m,tr=solid(np.load(D/row['file']));passed=m.status()==mf.Error.NoError and m.volume()>0;solids[row['name']]=m;results.append({'name':row['name'],'pass':passed,'closed_bodies':len(m.decompose())if passed else 0,'trials':tr});print('SOLID',row['name'],passed,flush=True)
checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
woodnames=[n for n in solids if (n.startswith('V24_15_Storage_')and 'Amber_Panes'not in n)or n=='V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails'];wood=union([solids[n]for n in woodnames]);roof=solids['SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry'];vol=(wood^roof).volume();ck('New timber clear of accepted roof shell',abs(vol)<1e-7,overlap_m3=vol)
for i in [1,2]:
 post=solids[f'V24_11_Storage_Veranda_Column_{i}']
 for n in ['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','V24_14_Storage_West_Sealed_Gable','V24_14_Storage_East_Sealed_Gable']:
  vol=(post^solids[n]).volume();ck(f'Round veranda post {i} clear of '+n,abs(vol)<1e-7,overlap_m3=vol)
for side,lo,hi in [('west',[13.13,-16.10,2.50],[13.204,-8.7,5.5]),('east',[18.686,-16.10,2.50],[19.1,-8.7,5.5])]:
 box=mf.Manifold.cube(np.array(hi)-lo).translate(lo);vol=(wood^box).volume();ck('No new timber projects through '+side+' exterior gable',abs(vol)<1e-7,overlap_m3=vol)
glass=solids['V24_15_Storage_Upper_Transom_Amber_Panes'];glazeoverlap=(glass^wood).volume();ck('Glazing divided around wood muntins without material intersections',abs(glazeoverlap)<1e-7,overlap_m3=glazeoverlap)
parts=wood.decompose();partrows=[]
for p in parts:partrows.append({'volume_m3':p.volume(),'bounds':p.bounding_box()})
# A carved relief line may be a separate closed cell. Structural members
# must form one connected assembly, allowing only tiny ornamental cells.
large=[p for p in parts if p.volume()>2e-4];ck('Roof and veranda structural timber connected with no loose beam ends',len(large)==1,closed_body_count=len(parts),large_body_count=len(large),bodies=partrows)
rear=solids['V24_15_Storage_Rear_Round_Posts'];base=solids['SITE_V17_STORAGE_TIMBER_COLUMNS_AND_STONE_BASES_Geometry'];vol=(rear^base).volume();ck('Rear round posts seat into existing stone bases',vol>1e-6,contact_overlap_m3=vol)
good=all(r['pass']for r in results+checks);out={'status':'PASS_INDEPENDENT_SAVED_SOLIDS'if good else'FAIL_INDEPENDENT_SAVED_SOLIDS','model_sha256':idx['model_sha256'],'solids':results,'spatial_checks':checks};(R/'V24_15_Independent_Solid_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
boxes=[('Entry',[12.5,-15.63,-.37],[1.30,.65,2.02]),('Continuous veranda',[13.8,-15.58,-.37],[4.25,.60,2.02]),('End post bypass',[18.02,-15.35,-.37],[.45,.33,2.02]),('Storage door opening',[15.64,-14.52,-.37],[.60,.45,1.95]),('East end portal',[18.47,-15.61,-.37],[.45,.59,2.02])];route=[]
for label,lo,sz in boxes:
 box=mf.Manifold.cube(sz).translate(lo);hits=[]
 for n,m in solids.items():
  if not rows[n]['obstacle']:continue
  if m.status()!=mf.Error.NoError:hits.append({'object':n,'error':str(m.status())});continue
  vol=(m^box).volume()
  if vol>1e-7:hits.append({'object':n,'overlap_m3':vol})
 route.append({'label':label,'origin':lo,'size':sz,'obstructions':hits})
good=all(not r['obstructions']for r in route);out={'status':'PASS_INDEPENDENT_CLEARANCE'if good else'FAIL_INDEPENDENT_CLEARANCE','model_sha256':idx['model_sha256'],'samples':route};(R/'V24_15_Independent_Clearance_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(out['status'],flush=True)
for r in results+checks:
 if not r['pass']:print('FAIL',r,flush=True)
for r in route:
 if r['obstructions']:print('BLOCKED',r,flush=True)
