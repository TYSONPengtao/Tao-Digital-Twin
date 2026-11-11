from pathlib import Path
import json,hashlib,re,urllib.parse
from PIL import Image
O=Path('E:/jz/JIA/Rebuild_V26_15');R=O/'Reports';checks=[]
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ck(n,b,**kw):checks.append({'check':n,'pass':bool(b),**kw});print('PACKAGE_QA',n,bool(b),kw if not b else'',flush=True)
manifest=json.loads((R/'V26_15_Manifest.json').read_text('utf8'));bad=[]
for r in manifest['files']:
 p=O/r['path']
 if not p.is_file()or p.stat().st_size!=r['bytes']or sha(p)!=r['sha256']:bad.append(r['path'])
ck('Every delivered file matches manifest SHA256 and size',not bad,file_count=len(manifest['files']),invalid=bad)
report=R/'V26_15_重面墙角与地面复核.html';text=report.read_text('utf8');missing=[]
for url in re.findall(r'(?:href|src)="([^"]+)"',text):
 if url.startswith(('https:','http:','#','data:')):continue
 if not (report.parent/urllib.parse.unquote(url)).exists():missing.append(url)
ck('Every HTML image and artifact link resolves locally',not missing,invalid=missing)
mh=sha(O/'Blender/Architecture_Complete_V26_15.blend');fh=sha(O/'Blender/Architecture_Complete_V26_15_Fast.blend');stale=[];failed=[]
for p in R.glob('V26_15_*QA.json'):
 if p.name=='V26_15_Package_QA.json':continue
 q=json.loads(p.read_text('utf8'));expected=fh if any(s in p.name for s in['Fast_Display','Runtime_Viewport'])else mh
 if q.get('model_sha256')!=expected:stale.append(p.name)
 if not q['status'].startswith('PASS')or q.get('failures'):failed.append(p.name)
ck('All QA reports pass against current delivered master or Fast hashes',not stale and not failed,stale=stale,failed=failed)
images=[]
for p in(R/'Views').glob('*.png'):
 with Image.open(p)as im:im.verify()
 images.append(p.name)
ck('All native model and viewport image files decode correctly',len(images)==15,images=len(images))
master_views=[]
for p in(R/'Views').glob('V26_15_*.json'):
 q=json.loads(p.read_text('utf8'));master_views.append(q['model_sha256']==mh and not q['model_file_modified']and q['temporary_lights']==0)
runtime=json.loads((R/'V26_15_Runtime_Viewport_QA.json').read_text('utf8'));ck('All review views identify current actual models and no added lights',len(master_views)==5 and all(master_views)and len(runtime['captures'])==5 and all(q['model_sha256']==fh and q['actual_viewport']for q in runtime['captures']))
cmd=(O/'启动漫游.cmd').read_text('utf8');ck('One launch entry selects current Fast model and existing runtime files',sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd']and'Architecture_Complete_V26_15_Fast.blend'in cmd and all((O/'Roam'/p).exists()for p in['start_roam_fast.py','roam_controller_fast.py','roam_physics.py']))
source=json.loads((R/'V26_15_Changes.json').read_text('utf8'));ck('Saved V26.14 source remains byte-identical',sha(Path(source['source']))==source['source_sha256'])
fail=[q for q in checks if not q['pass']];out={'status':'PASS'if not fail else'FAIL','master_sha256':mh,'fast_sha256':fh,'checks':checks,'failures':fail};(R/'V26_15_Package_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('PACKAGE_VERIFIED',len(checks),len(fail),flush=True)
if fail:raise AssertionError(fail)
