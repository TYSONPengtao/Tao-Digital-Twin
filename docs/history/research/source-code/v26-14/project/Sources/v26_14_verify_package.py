from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import json,hashlib
O=Path('E:/jz/JIA/Rebuild_V26_14');checks=[]
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw});print('PACKAGE',n,bool(p),kw if not p else'',flush=True)
M=json.loads((O/'Manifest_SHA256.json').read_text('utf8'));bad=[]
for r in M['files']:
 p=O/r['file']
 if not p.exists()or p.stat().st_size!=r['bytes']or sha(p)!=r['sha256']:bad.append(r['file'])
ck('Every packaged file matches recorded size and SHA256',not bad,files=len(M['files']),invalid=bad)
ck('Original V26.13 source file is byte-identical',sha(M['source_model'])==M['source_sha256'])
ck('Both delivered models match the verified hashes',sha(O/'Blender/Architecture_Complete_V26_14.blend')==M['model_sha256']and sha(O/'Blender/Architecture_Complete_V26_14_Fast.blend')==M['fast_model_sha256'])
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,t,a):self.links +=[v for k,v in a if k in['src','href']and v and not v.startswith(('#','https:','http:'))]
page=O/'Reports/V26_14_卫浴墙角复核.html';x=Links();x.feed(page.read_text('utf8'));bad=[s for s in x.links if not(page.parent/unquote(s)).resolve().is_file()]
ck('All report images and links resolve',not bad,links=len(x.links),invalid=bad)
bad=[];count=0
for r in M['checks']:
 q=json.loads((O/'Reports'/r['file']).read_text('utf8'));count+=len(q['checks']);want=M['fast_model_sha256']if any(k in r['file']for k in['Fast_Display','Runtime_Viewport'])else M['model_sha256']
 if q['failures']or not all(c['pass']for c in q['checks'])or q['model_sha256']!=want:bad.append(r['file'])
ck('Native, geometry, door, physics, Fast, runtime and visual checks all pass for delivered hashes',not bad,checks=count,invalid=bad)
cmd=(O/'启动漫游.cmd').read_text('utf8');ck('Single default launcher targets V26.14 Fast and its runtime',sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd']and'Architecture_Complete_V26_14_Fast.blend'in cmd and'start_roam_fast.py'in cmd and(O/'Roam/start_roam_fast.py').is_file()and not list(O.rglob('*.3dm')))
refs=json.loads((O/'References/Reference_Index.json').read_text('utf8'));available=[r for r in refs if r['file']];bad=[r['file']for r in available if sha(O/'References'/r['file'])!=r['sha256']or sha(r['source'])!=r['sha256']];ck('Available original feedback photo is unchanged; missing older chat photo is explicitly recorded',len(available)==1 and len(refs)==2 and not bad,invalid=bad)
views=list((O/'Reports').glob('V26_14_0*.json'))+list((O/'Reports').glob('Viewport_0*.json'));bad=[p.name for p in views if json.loads(p.read_text('utf8'))['model_sha256']!=(M['fast_model_sha256']if p.name.startswith('Viewport_')else M['model_sha256'])];ck('Five saved-model views and two actual material viewport views match the delivered files',len(views)==7 and not bad,invalid=bad)
A=O/'Sources/Geometry_Archive';src=json.loads((A/'Source_Index.json').read_text('utf8'));prep=json.loads((A/'Prepared.json').read_text('utf8'));sf={r['file']for r in src['objects']if'file'in r};of={r['file']for r in prep['objects']};ck('Source geometry and generated geometry have separate archived filenames',not(sf&of)and all(n.startswith('Source_')for n in sf))
fail=[r for r in checks if not r['pass']];(O/'Reports/V26_14_Package_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','model_sha256':M['model_sha256'],'fast_model_sha256':M['fast_model_sha256'],'files_verified':len(M['files']),'saved_model_checks':count,'checks':checks,'failures':fail},ensure_ascii=False,indent=2),'utf8');print('PACKAGE_VERIFIED',len(M['files']),len(fail),flush=True)
if fail:raise AssertionError(fail)
