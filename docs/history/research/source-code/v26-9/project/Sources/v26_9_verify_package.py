from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import json,hashlib
O=Path('E:/jz/JIA/Rebuild_V26_9');checks=[]
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('PACKAGE',n,bool(p),kw if not p else'',flush=True)
M=json.loads((O/'Manifest_SHA256.json').read_text('utf8'));bad=[]
for r in M['files']:
 p=O/r['file']
 if not p.exists()or p.stat().st_size!=r['bytes']or sha(p)!=r['sha256']:bad.append(r['file'])
ck('All packaged files match recorded size and SHA256',not bad,files=len(M['files']),invalid=bad)
ck('V26.8 source remains byte-identical',sha(M['source_model'])==M['source_sha256'])
ck('Both native models match verified checks',sha(O/'Blender/Architecture_Complete_V26_9.blend')==M['model_sha256']and sha(O/'Blender/Architecture_Complete_V26_9_Fast.blend')==M['fast_model_sha256'])
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  self.links += [v for k,v in attrs if k in ['src','href']and v and not v.startswith(('#','https:','http:'))]
page=O/'Reports/V26_9_实景与修正复核.html';x=Links();x.feed(page.read_text('utf8'));bad=[s for s in x.links if not(page.parent/unquote(s)).resolve().is_file()];ck('Every local review-page image and link resolves',not bad,links=len(x.links),invalid=bad)
bad=[];count=0
for r in M['checks']:
 q=json.loads((O/'Reports'/r['file']).read_text('utf8'));count+=len(q['checks'])
 if q['failures']or not all(c['pass']for c in q['checks']):bad.append(r['file'])
ck('All145 saved-model and visual checks pass',not bad and count==145,checks=count,invalid=bad)
ck('One default Fast roam launcher and no Rhino export',sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd']and not list(O.rglob('*.3dm')))
references=json.loads((O/'References/Reference_Index.json').read_text('utf8'));bad=[]
for r in references:
 if r['packaged_path']and sha(O/r['packaged_path'])!=r['sha256']:bad.append(r['name'])
ck('Locally available source images copied unchanged; chat-only images explicitly indexed',not bad and all(r['status']for r in references),local_images=sum(bool(r['packaged_path'])for r in references),chat_attachment_records=sum(not r['packaged_path']for r in references),invalid=bad)
fail=[r for r in checks if not r['pass']];(O/'Reports/V26_9_Package_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':M['model_sha256'],'fast_model_sha256':M['fast_model_sha256'],'checks':checks,'failures':fail,'files_verified':len(M['files'])},ensure_ascii=False,indent=2),'utf8');print('V26_9_PACKAGE_VERIFIED',len(M['files']),len(fail),flush=True)
if fail:raise AssertionError(fail)
