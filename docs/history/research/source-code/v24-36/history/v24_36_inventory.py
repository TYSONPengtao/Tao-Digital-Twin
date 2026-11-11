from pathlib import Path
import json,struct,collections,hashlib
W=Path(__file__).parent;D=W/'v24_36';D.mkdir(exist_ok=True);SRC=Path('D:/AJAVIS01/ContextCapture/CASES/新建工程/Productions/Production_PTJIA6/Scene/Data/Model');rows=[];levels=collections.Counter();formats=collections.Counter()
def level(n):
 import re
 m=re.search(r'_L(\d+)_',n);return int(m.group(1))if m else 0
for p in sorted(SRC.glob('*.3mxb')):
 with p.open('rb')as f:
  prefix=f.read(9);assert prefix[:5]==b'3MXBO',p.name;n=struct.unpack('<I',prefix[5:])[0];h=json.loads(f.read(n))
 links=list(dict.fromkeys(x for node in h['nodes']for x in node.get('children',[])));levels[level(p.name)]+=1
 for r in h.get('resources',[]):formats[r['format']]+=1
 rows.append({'name':p.name,'bytes':p.stat().st_size,'level':level(p.name),'links':links,'header':h})
index={r['name']:r for r in rows};(D/'3MX_Inventory.json').write_text(json.dumps({'source':str(SRC),'files':rows,'counts':dict(levels),'formats':dict(formats)},ensure_ascii=False,indent=2),encoding='utf8')
for cap in [17,18,19,20,21,22,23,27,99]:
 chosen=[];seen=set();stack=['Model.3mxb'];missing=[]
 while stack:
  n=stack.pop()
  if n in seen:continue
  seen.add(n);r=index.get(n)
  if r is None:missing.append(n);continue
  if r['level']>=cap or not r['links']:chosen.append(n)
  else:stack.extend(r['links'])
 assert not missing,missing;(D/f'Frontier_{cap}.json').write_text(json.dumps(chosen));print('FRONTIER',cap,len(chosen),sum(index[n]['bytes']for n in chosen),flush=True)
scene=SRC.parents[1]/'Production_PTJIA6.3mx';meta=json.loads(scene.read_text('utf8'));(D/'Scene_Metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8');print('FORMAT',dict(formats),'LEVELS',dict(levels),flush=True)
