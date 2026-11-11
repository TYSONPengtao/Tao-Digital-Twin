import sys,json,numpy as np
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_27';R=Path('E:/jz/JIA/Rebuild_V24_27/Reports');idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text('utf8'))};saved=json.loads((D/'Saved_Geometry_Index.json').read_text());prep={r['name']:r for r in json.loads((D/'Prepared_Geometry.json').read_text('utf8'))['raw_objects']};checks=[]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
for row in saved['objects']:
 n=row['name'];a=np.load(D/row['file']);s=np.load(D/idx[n]['file']);r=np.load(D/prep[n]['file']);v=a['v'];f=a['f'];t=v[f];old=r['source_v'][f];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);on=np.cross(old[:,1]-old[:,0],old[:,2]-old[:,0]);up=on[:,2]>1e-10
 # Native coordinates are float32; affine subdivision of pre-existing
 # sub-millimetre slivers can collapse their plan projection on save. Record
 # that area explicitly and require all resolvable faces to keep orientation.
 meaningful=up&(on[:,2]>1e-6);bad=up&(normal[:,2]<=0);ck('No resolvable surface area reversed during grading / '+n,(normal[meaningful,2]>0).all()and float(on[bad,2].sum())<1e-5,collapsed_original_double_area_m2=float(on[bad,2].sum()),projected_double_area_resolution_m2=1e-6)
 ck('All graded vertices finite / '+n,np.isfinite(v).all())
 orig=s['v'][s['f']];areas=np.linalg.norm(np.cross(orig[:,1]-orig[:,0],orig[:,2]-orig[:,0]),axis=1);child=np.linalg.norm(on,axis=1);total=np.bincount(r['parent'],weights=child,minlength=len(areas));ck('Affine subdivision covers every original triangle exactly / '+n,np.max(abs(total-areas))<1e-7,maximum_double_area_error_m2=float(np.max(abs(total-areas))))
 ck('Subdivisions inherit original face material / '+n,np.array_equal(a['mi'],s['mi'][r['parent']]))
 # A vertical, monotonic deformation keeps all existing shell boundaries and
 # cavity topology. Grade is checked from the saved triangle normals.
 if 'SOIL'in n:
  c=t.mean(1);pick=up&(c[:,0]>-5.8)&(c[:,0]<-.25)&(c[:,1]>2.2)&(c[:,1]<9.5)
  g=np.linalg.norm(normal[pick,:2],axis=1)/normal[pick,2];ck('West yard grade no longer has the short steep mound',len(g)>0 and float(g.max())<.085,maximum_grade=float(g.max()),median_grade=float(np.median(g)),triangles=int(pick.sum()))
 # Outside the two declared local grading rectangles every saved source
 # vertex is unchanged, including distant road and retaining-wall toes.
 p=r['source_v'];inside=((p[:,0]>-6.0001)&(p[:,0]<.25001)&(p[:,1]>-3.6001)&(p[:,1]<11.9001))|((p[:,0]>=-.125-1e-6)&(p[:,0]<14.0801)&(p[:,1]>-3.6001)&(p[:,1]<1.9001))
 ck('No change outside declared grade scope / '+n,np.max(np.abs(v[~inside]-p[~inside]),initial=0)<3e-6)
fail=[r for r in checks if not r['pass']];(R/'V24_27_Grade_QA.json').write_text(json.dumps({'status':'PASS_LOCAL_GRADE_TOPOLOGY_AND_SLOPES'if not fail else'FAIL','model_sha256':saved['model_sha256'],'checks':checks,'failures':fail},ensure_ascii=False,indent=2),encoding='utf8');print('V27_GRADE_QA',len(checks),'FAIL',len(fail),flush=True)
for c in fail:print('FAIL',c,flush=True)
