from pathlib import Path
import sys,json,hashlib
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import numpy as np,manifold3d as mf
part=json.loads(Path(__file__).with_name('Preview_Material_Settings_Partial.json').read_text('utf8'))
checks=part['checks'];P=Path(part['model']);h=part['model_sha256'];R=P.parents[1]/'Reports'
with P.open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==h
def ck(n,b,**kw):
 checks.append({'check':n,'pass':bool(b),**kw});print(n,bool(b),kw if not b else'',flush=True)
# Native saved triangles independently verify the actual20mm soffit return.
def read(d):
 idx={r['name']:r for r in json.loads((d/'Geometry_Index.json').read_text('utf8'))};r=idx['V26_3_House_Connected_Walls_And_Stairs'];a=np.load(d/r['file']);return r,a
def solid(a):
 v,ix=np.unique(a['v'],axis=0,return_inverse=True);m=mf.Manifold(mf.Mesh64(np.array(v,np.float64),np.array(ix[a['f']],np.uint64)));assert m.status()==mf.Error.NoError;return m
r,a=read(W/'v26_6/Final');oldr,olda=read(W/'v26_5/Final');m=solid(a);om=solid(olda)
box=mf.Manifold.cube([.05,2.02,.04]).translate([8.97,7.54,3.03]);newlocal=m^box;oldlocal=om^box;diff=max(0.,(newlocal-oldlocal).volume())+max(0.,(oldlocal-newlocal).volume())
ck('Original F1 stair hall20mm beam soffit return geometry retained',diff<1e-9,local_symmetric_difference_m3=diff,old_volume_m3=oldlocal.volume(),new_volume_m3=newlocal.volume())
t=a['v'][a['f']];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(n,axis=1)/2;n/=np.maximum(area[:,None]*2,1e-30)
sel=(n[:,2]<-.99)&(abs(t[:,:,2].mean(1)-3.05)<.00002)&(t[:,:,0].min(1)>8.9799)&(t[:,:,0].max(1)<9.0001)&(t[:,:,1].min(1)>7.5499)&(t[:,:,1].max(1)<9.5501)
aa=float(area[sel].sum());mats=sorted({r['materials'][int(i)]for i in a['mi'][sel]})
ck('Retained soffit remains white ceiling surface',abs(aa-.04)<2e-6 and mats==['M_V26_3_Neutral_White_Interior_Ceiling'],area_m2=aa,materials=mats)
fail=[q for q in checks if not q['pass']]
part.update(status='PASS'if not fail else'FAIL',checks=checks,failures=fail)
fn=R/'V26_6_Neutral_White_Preview_QA.json';fn.write_text(json.dumps(part,ensure_ascii=False,indent=2),encoding='utf8')
print('FINAL_PREVIEW_QA_DONE',len(checks),'FAIL',len(fail),str(fn),flush=True)
