import json,hashlib
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V12')
manifest=json.loads((O/'01_Source/Source_Manifest_V12.json').read_text(encoding='utf8'))
rows=[]
for i,row in enumerate(manifest['sources']):
 p=Path(row['source']);h=hashlib.sha256()
 with p.open('rb') as f:
  for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
 digest=h.hexdigest();assert digest==row['sha256'],str(p)
 st=p.stat();rows.append(dict(source=str(p),unchanged=True,sha256=digest,bytes=st.st_size,mtime_ns=st.st_mtime_ns))
 if i%10==0:print('Source preservation verified',i+1,'/',len(manifest['sources']),flush=True)
(O/'06_Report/Source_Preservation_QA.json').write_text(json.dumps(dict(status='PASS',sources=rows),ensure_ascii=False,indent=2),encoding='utf8')
print('Source preservation PASS',len(rows),flush=True)
