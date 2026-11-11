from pathlib import Path
from html.parser import HTMLParser
import hashlib,json
O=Path('E:/jz/JIA/Rebuild_V26_6')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
m=json.loads((O/'Manifest_SHA256.json').read_text('utf8'));errors=[]
listed={r['file'] for r in m['files']}
actual={str(p.relative_to(O))for p in O.rglob('*')if p.is_file()and p.name!='Manifest_SHA256.json'}
assert listed==actual,{'missing':list(listed-actual),'unlisted':list(actual-listed)}
for r in m['files']:
 p=O/r['file']
 if p.stat().st_size!=r['bytes'] or sha(p)!=r['sha256']:errors.append(r['file'])
assert not errors,errors
assert sha(O/'Blender/Architecture_Complete_V26_6.blend')==m['model_sha256']
assert sha(m['source_model'])==m['source_sha256']
for r in m['checks']:
 q=json.loads((O/'Reports'/r['file']).read_text('utf8'))
 assert q['model_sha256']==m['model_sha256'] and not q['failures'] and all(c['pass']for c in q['checks'])
class Links(HTMLParser):
 def __init__(self):super().__init__();self.paths=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['src','href']and v and not v.startswith(('http:','https:','#')):self.paths.append(v)
page=O/'Reports/V26_6_实景依据与修正复核.html';parser=Links();parser.feed(page.read_text('utf8'))
missing=[s for s in parser.paths if not(page.parent/s).is_file()]
assert not missing,missing
assert [p.name for p in O.glob('*.cmd')]==['启动漫游.cmd']
assert not list(O.rglob('*.3dm'))
assert len(list((O/'Blender').glob('*.blend')))==1
assert len(list((O/'Reports').glob('After_*_Cycles.png')))==10
print('FINAL_PACKAGE_PASS','FILES',len(actual),'CHECKS',sum(q['checks']for q in m['checks']),'LOCAL_HTML_LINKS',len(parser.paths),'MODEL_SHA256',m['model_sha256'])
