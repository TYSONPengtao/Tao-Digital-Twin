import json,struct,csv,math,hashlib
from pathlib import Path
W=Path(__file__).parent;inv=json.loads((W/'CASES_Inventory_V3.json').read_text(encoding='utf-8'));rows=[]
for ref in inv['references']:
 for layer in ref.get('metadata',{}).get('layers',[]):
  root=Path(ref['path']).parent/layer['root'];row={'case':ref['case'],'scene':ref['path'],'SRS':layer.get('SRS'),'origin':layer.get('SRSOrigin'),'root':str(root)}
  if root.exists():
   with root.open('rb') as f:
    prefix=f.read(9);n=struct.unpack('<I',prefix[5:9])[0];header=json.loads(f.read(n));row['header']=header;row['bytes']=root.stat().st_size
  rows.append(row);print(json.dumps(row,ensure_ascii=False)[:2400])
(W/'3MX_Roots_V3.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
