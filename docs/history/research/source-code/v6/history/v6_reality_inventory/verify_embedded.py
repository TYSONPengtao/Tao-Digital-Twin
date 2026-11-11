import sys,json,hashlib,base64
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'libs'));import rhino3dm as r
O=Path(__file__).resolve().parent
f=r.File3dm.Read(r'E:\jz\纯场地版本.3dm')
data=json.loads((O/'Pure_Baseline_Hashes.json').read_text(encoding='utf-8'))
for t in data['textures']:
 try:
  blob=f.GetEmbeddedFileAsBase64(t['source']);b=base64.b64decode(blob);t['embedded_bytes']=len(b);t['embedded_sha256']=hashlib.sha256(b).hexdigest();t['embedded_matches_external']=t['sha256']==t['embedded_sha256']
 except Exception as e:t['embedded_hash_error']=str(e)
 print(t['source'],t.get('embedded_matches_external',False),t.get('embedded_hash_error',''),flush=True)
(O/'Pure_Baseline_Hashes.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
