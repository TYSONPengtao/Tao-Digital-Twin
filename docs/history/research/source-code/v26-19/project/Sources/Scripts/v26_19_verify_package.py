from pathlib import Path
import json,hashlib,re,urllib.parse
from PIL import Image
O=Path('E:/jz/JIA/Rebuild_V26_19');R=O/'Reports';checks=[]
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('PACKAGE_QA',n,bool(yes),kw if not yes else'',flush=True)
manifest=json.loads((R/'V26_19_Manifest.json').read_text('utf8'));invalid=[]
for q in manifest['files']:
 p=O/q['path']
 if not p.is_file()or p.stat().st_size!=q['bytes']or sha(p)!=q['sha256']:invalid.append(q['path'])
ck('Every delivered file matches its SHA256 and size',not invalid,files=len(manifest['files']),invalid=invalid)
text=(R/'V26_19_梁端窗角与院内构件复核.html').read_text('utf8');missing=[]
for url in re.findall(r'(?:href|src)="([^"]+)"',text):
 if url.startswith(('http:','https:','#','data:')):continue
 if not(R/urllib.parse.unquote(url)).exists():missing.append(url)
ck('All report images and artifact links resolve',not missing,missing=missing)
mh=sha(O/'Blender/Architecture_Complete_V26_19.blend');fh=sha(O/'Blender/Architecture_Complete_V26_19_Fast.blend');stale=[];failed=[]
for p in R.glob('V26_19_*QA.json'):
 if p.name=='V26_19_Package_QA.json':continue
 q=json.loads(p.read_text('utf8'));expected=fh if any(n in p.name for n in['Fast_Display','Runtime_Viewport'])else mh
 if q.get('model_sha256')!=expected:stale.append(p.name)
 if not q['status'].startswith('PASS')or q.get('failures'):failed.append(p.name)
ck('Final QA reports pass against the delivered model hashes',not stale and not failed,stale=stale,failed=failed)
ps=list((R/'Views').glob('*.png'))
for p in ps:
 with Image.open(p)as im:im.verify()
ck('Seven before-after pairs and four actual viewport images decode',len(ps)==18,image_count=len(ps))
ch=json.loads((R/'V26_19_Changes.json').read_text('utf8'));pairs=[]
for p in(R/'Views').glob('V26_18_*.json'):
 b=json.loads(p.read_text('utf8'));a=json.loads(p.with_name(p.name.replace('V26_18_','V26_19_',1)).read_text('utf8'));pairs.append(b['model_sha256']==ch['source_sha256']and a['model_sha256']==mh and b['camera']==a['camera']and b['world']==a['world']and b['temporary_lights']==a['temporary_lights']==0)
ck('All seven pairs use matching cameras and lighting with current model hashes',len(pairs)==7 and all(pairs))
runtime=json.loads((R/'V26_19_Runtime_Viewport_QA.json').read_text('utf8'));ck('Actual Fast viewport review uses the delivered file and no added lights',len(runtime['captures'])==4 and all(q['model_sha256']==fh and q['actual_viewport']and q['extra_lights']==0 for q in runtime['captures']))
ck('First actual viewport runs the human tour on the third-floor landing',runtime['captures'][0]['tour_running']and runtime['captures'][0]['grounded'])
cmd=(O/'启动漫游.cmd').read_text('utf8');ck('One launcher selects V26.19 Fast and its current runtime',sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd']and'Architecture_Complete_V26_19_Fast.blend'in cmd and all((O/'Roam'/n).exists()for n in['start_roam_fast.py','roam_controller_fast.py','roam_physics.py']))
ck('Source V26.18 is preserved byte for byte',sha(Path(ch['source']))==ch['source_sha256'])
run=json.loads((O/'Sources/Check_Run.json').read_text('utf8'));ck('All eight build and validation steps completed',len(run)==8 and all(q['successful_process']for q in run))
fail=[q for q in checks if not q['pass']];(R/'V26_19_Package_QA.json').write_text(json.dumps({'status':'PASS'if not fail else'FAIL','master_sha256':mh,'fast_sha256':fh,'checks':checks,'failures':fail},ensure_ascii=False,indent=2),'utf8');print('PACKAGE_VERIFIED',len(checks),len(fail),flush=True)
if fail:raise AssertionError(fail)
