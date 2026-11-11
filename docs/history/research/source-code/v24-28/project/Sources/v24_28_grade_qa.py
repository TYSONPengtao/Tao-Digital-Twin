import json,hashlib,numpy as np
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_28';R=Path('E:/jz/JIA/Rebuild_V24_28/Reports')
idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))};saved=json.loads((D/'Saved_Geometry_Index.json').read_text());prep={r['name']:r for r in json.loads((D/'Prepared_Geometry.json').read_text('utf8'))['raw_objects']};checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
for row in saved['objects']:
 if row['kind']!='ground':continue
 n=row['name'];a=np.load(D/row['file']);s=np.load(D/idx[n]['file']);r=np.load(D/prep[n]['file']);v=a['v'];f=a['f'];t=v[f];old=r['source_v'][f]
 normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);on=np.cross(old[:,1]-old[:,0],old[:,2]-old[:,0]);up=on[:,2]>1e-10;meaningful=up&(on[:,2]>1e-6);bad=up&(normal[:,2]<=0)
 ck('No resolvable horizontal surface reversed / '+n,(normal[meaningful,2]>0).all()and float(on[bad,2].sum())<1e-5,collapsed_original_double_area_m2=float(on[bad,2].sum()))
 ck('Finite geometry / '+n,np.isfinite(v).all())
 orig=s['v'][s['f']];areas=np.linalg.norm(np.cross(orig[:,1]-orig[:,0],orig[:,2]-orig[:,0]),axis=1);child=np.linalg.norm(on,axis=1);total=np.bincount(r['parent'],weights=child,minlength=len(areas))
 ck('Clipping and subdivision preserve every source face area / '+n,np.max(abs(total-areas))<1e-7,maximum_double_area_error_m2=float(np.max(abs(total-areas))))
 ck('Original materials inherited on both step sides / '+n,np.array_equal(a['mi'],s['mi'][r['parent']]))
 ck('Plan footprint unchanged / '+n,np.max(abs(v[:,:2]-r['source_v'][:,:2]))<3e-6)
 if 'SOIL' in n:
  c=t.mean(1);pick=up&(c[:,0]>-5.8)&(c[:,0]<-.3)&(c[:,1]>-11.0)&(c[:,1]<10.0)
  g=np.linalg.norm(normal[pick,:2],axis=1)/normal[pick,2]
  ck('Visible exterior ground is a horizontal plane',len(g)>0 and float(g.max())<.001,maximum_grade=float(g.max()),triangles=int(pick.sum()))
fail=[c for c in checks if not c['pass']]
(R/'V24_28_Grade_QA.json').write_text(json.dumps({'status':'PASS_FOOTPRINT_LEVEL_EXTERIOR_AND_CLIPPED_STEP'if not fail else'FAIL','model_sha256':saved['model_sha256'],'checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8')
print('V28_GRADE_QA',len(checks),'FAIL',len(fail),flush=True)
for c in fail:print('FAIL',c,flush=True)
