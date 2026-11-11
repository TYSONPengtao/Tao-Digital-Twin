from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import json,hashlib
O=Path('E:/jz/JIA/Rebuild_V26_12');checks=[]
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('PACKAGE',n,bool(p),kw if not p else'',flush=True)
M=json.loads((O/'Manifest_SHA256.json').read_text('utf8'));bad=[]
for r in M['files']:
 p=O/r['file']
 if not p.exists()or p.stat().st_size!=r['bytes']or sha(p)!=r['sha256']:bad.append(r['file'])
ck('Every packaged file matches its recorded size and SHA256',not bad,files=len(M['files']),invalid=bad)
ck('Both original V24 and V26.11 source files remain byte-identical',sha(M['source_model'])==M['source_sha256']and sha(M['reference_model'])==M['reference_sha256'])
ck('Both delivered native models match their verified hashes',sha(O/'Blender/Architecture_Complete_V26_12.blend')==M['model_sha256']and sha(O/'Blender/Architecture_Complete_V26_12_Fast.blend')==M['fast_model_sha256'])
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,t,a):self.links +=[v for k,v in a if k in['src','href']and v and not v.startswith(('#','https:','http:'))]
page=O/'Reports/V26_12_内大门浮雕复核.html';x=Links();x.feed(page.read_text('utf8'));bad=[s for s in x.links if not(page.parent/unquote(s)).resolve().is_file()]
ck('All review-page images and links resolve',not bad,links=len(x.links),invalid=bad)
bad=[];count=0
for r in M['checks']:
 q=json.loads((O/'Reports'/r['file']).read_text('utf8'));count+=len(q['checks']);want=M['fast_model_sha256']if any(k in r['file']for k in['Fast_Display','Runtime_Viewport'])else M['model_sha256']
 if q['failures']or not all(c['pass']for c in q['checks'])or q['model_sha256']!=want:bad.append(r['file'])
ck('All native, gate, physics, Fast, runtime and visual checks pass for delivered hashes',not bad,checks=count,invalid=bad)
ck('One default Fast tour launcher, with no Rhino export',sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd']and'Architecture_Complete_V26_12_Fast.blend'in(O/'启动漫游.cmd').read_text('utf8')and not list(O.rglob('*.3dm')))
refs=json.loads((O/'References/Reference_Index.json').read_text('utf8'));bad=[r['file']for r in refs if sha(O/'References'/r['file'])!=r['sha256']]
ck('Feedback and original V24 reference images are preserved unchanged',len(refs)==3 and not bad,invalid=bad)
views=list((O/'Reports').glob('V26_12_0*.json'))+list((O/'Reports').glob('Viewport_0*.json'));bad=[p.name for p in views if json.loads(p.read_text('utf8'))['model_sha256']!=(M['fast_model_sha256']if p.name.startswith('Viewport_')else M['model_sha256'])]
ck('Four native rendered views and two actual viewport captures match delivered files',len(views)==6 and not bad,views=len(views),invalid=bad)
fail=[q for q in checks if not q['pass']]
(O/'Reports/V26_12_Package_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':M['model_sha256'],'fast_model_sha256':M['fast_model_sha256'],'files_verified':len(M['files']),'saved_model_checks':count,'checks':checks,'failures':fail},ensure_ascii=False,indent=2),'utf8');print('PACKAGE_VERIFIED',len(M['files']),len(fail),flush=True)
if fail:raise AssertionError(fail)
