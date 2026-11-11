import json,shutil,hashlib
from pathlib import Path
W=Path(__file__).parent;O=Path(r'E:\jz\JIA\Rebuild_V8_Hybrid');D=W/'v8_terrain_clear/contact_gap';ip=O/'02_Data/Patch_Index.json';I=json.loads(ip.read_text(encoding='utf-8'));rows=json.loads((D/'Candidate_Patch_Index_Rows.json').read_text(encoding='utf-8'))
for r in rows:
 previous=next((j for j,q in enumerate(I) if q['name']==r['name']),None)
 r['index']=I[previous]['index'] if previous is not None else len(I)
 shutil.copy2(D/r['file'],O/'02_Data'/r['file'])
 if previous is None:I.append(r)
 else:I[previous]=r
ip.write_text(json.dumps(I,ensure_ascii=False,indent=2),encoding='utf-8')
e=O/'07_Evidence/Final_Contact_Ground_Repair';e.mkdir(parents=True,exist_ok=True)
for p in D.iterdir():
 if p.is_file() and p.suffix in ['.npz','.json']:shutil.copy2(p,e/p.name)
qa=json.loads((D/'Contact_Gap_Ground_QA.json').read_text(encoding='utf-8'));qa['status']='APPLIED_PENDING_NATIVE_FINAL_QA';qa['applied_patch_names']=[r['name'] for r in rows];qa['patch_index_sha256']=hashlib.sha256(ip.read_bytes()).hexdigest()
(O/'06_Report/Contact_Gap_Ground_Integration_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print('Added only actual residual ground:',[r['name'] for r in rows],flush=True)
