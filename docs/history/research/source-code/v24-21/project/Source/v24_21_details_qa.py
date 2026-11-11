import sys,json,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_16_common import solid,np,mf
D=W/'v24_21';O=Path('E:/jz/JIA/Rebuild_V24_21');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_21.blend';data=json.loads((D/'Saved_Detail_Index.json').read_text());checks=[]
for row in data['objects']:
 d=np.load(D/row['file']);m=solid(d['v'],d['f']);t=d['v'][d['f']];volume=float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6);good=m.status()==mf.Error.NoError and volume>0 and abs(volume-row['prepared_volume_m3'])<max(1e-4,row['prepared_volume_m3']*1e-5);checks.append({'check':'Saved exterior relief is a closed positive-volume solid / '+row['name'],'pass':good,'saved_signed_volume_m3':volume,'prepared_volume_m3':row['prepared_volume_m3'],'components':len(m.decompose())})
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
assert h==data['model_sha256'];fail=[r for r in checks if not r['pass']];(R/'V24_21_Exterior_Solid_QA.json').write_text(json.dumps({'status':'PASS_CLOSED_EXTERIOR_RELIEF'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail},ensure_ascii=False,indent=2));print('V21_DETAIL_QA',len(checks),'FAIL',len(fail),flush=True)
