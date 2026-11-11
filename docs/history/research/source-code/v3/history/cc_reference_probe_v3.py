import sys,struct,json,csv,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs')]
import numpy as np,fitz
rows=list(csv.DictReader((W/'CASES_Model_Files_V3.csv').open(encoding='utf-8-sig')))
for row in rows:
 if row['ext']=='.obj' and row['case'] in ['PTHOUSE','JIA']:
  p=Path(row['path']);v=[];nf=0
  with p.open(encoding='utf-8',errors='replace') as f:
   for line in f:
    if line.startswith('v '):v.append([float(x) for x in line.split()[1:4]])
    elif line.startswith('f '):nf+=1
  a=np.array(v);print(row['case'],p.parent.name,'BBOX',a.min(0).tolist(),a.max(0).tolist(),'V',len(a),'F',nf)
roots=json.loads((W/'3MX_Roots_V3.json').read_text(encoding='utf-8'))
for row in roots:
 if row['case'] not in ['JIA','ui','PT666PT666','MB501','ZZCLDQ']:continue
 p=Path(row['root']);child=p.parent/row['header']['nodes'][0]['children'][0];print('CHILD',child,'exists',child.exists())
 if child.exists():
  with child.open('rb') as f:prefix=f.read(9);h=json.loads(f.read(struct.unpack('<I',prefix[5:])[0]))
  (W/(row['case']+'_'+p.stem+'_3MX_Child.json')).write_text(json.dumps(h,indent=2),encoding='utf-8');print(json.dumps(h)[:2400])
doc=fitz.open(r'C:\Program Files\Bentley\ContextCapture Center\doc\3MX Specifications.pdf')
text='\n'.join(p.get_text() for p in doc);(W/'3MX_Specifications.txt').write_text(text,encoding='utf-8')
