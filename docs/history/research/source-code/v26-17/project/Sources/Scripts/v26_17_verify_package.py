from pathlib import Path
import json,hashlib,re,urllib.parse,xml.etree.ElementTree as ET
from PIL import Image
O=Path('E:/jz/JIA/Rebuild_V26_17');R=O/'Reports';checks=[]
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def ck(name,yes,**data):checks.append({'check':name,'pass':bool(yes),**data});print('PACKAGE_QA',name,bool(yes),data if not yes else'',flush=True)
manifest=json.loads((R/'V26_17_Manifest.json').read_text('utf8'));bad=[]
for row in manifest['files']:
 p=O/row['path']
 if not p.is_file()or p.stat().st_size!=row['bytes']or sha(p)!=row['sha256']:bad.append(row['path'])
ck('Every delivered file matches its SHA256 and size',not bad,files=len(manifest['files']),invalid=bad)
report=R/'V26_17_梁柱板与窗边复核.html';text=report.read_text('utf8');missing=[]
for url in re.findall(r'(?:href|src)="([^"]+)"',text):
 if url.startswith(('http:','https:','#','data:')):continue
 if not(report.parent/urllib.parse.unquote(url)).exists():missing.append(url)
ck('Every report image and artifact link resolves',not missing,invalid=missing)
mh=sha(O/'Blender/Architecture_Complete_V26_17.blend');fh=sha(O/'Blender/Architecture_Complete_V26_17_Fast.blend');stale=[];failed=[]
for p in R.glob('V26_17_*QA.json'):
 if p.name=='V26_17_Package_QA.json':continue
 q=json.loads(p.read_text('utf8'));expected=fh if any(t in p.name for t in['Fast_Display','Runtime_Viewport'])else mh
 if q.get('model_sha256')!=expected:stale.append(p.name)
 if not q['status'].startswith('PASS')or q.get('failures'):failed.append(p.name)
ck('All final checks pass against the current native model hashes',not stale and not failed,stale=stale,failed=failed)
images=list((R/'Views').glob('*.png'))
for p in images:
 with Image.open(p)as im:im.verify()
ck('Ten before-after pairs and five actual viewport images decode',len(images)==25,image_count=len(images))
svg=list(R.glob('V26_17_*.svg'))
for p in svg:ET.parse(p)
ck('Both structural SVG diagrams are well-formed',len(svg)==2)
ch=json.loads((R/'V26_17_Changes.json').read_text('utf8'));pairs=[]
for p in(R/'Views').glob('V26_16_*.json'):
 b=json.loads(p.read_text('utf8'));a=json.loads(p.with_name(p.name.replace('V26_16_','V26_17_',1)).read_text('utf8'));pairs.append(b['model_sha256']==ch['source_sha256']and a['model_sha256']==mh and b['camera']==a['camera']and b['world']==a['world']and b['temporary_lights']==a['temporary_lights']==0)
ck('All ten pairs use current source/result models, identical cameras and lighting',len(pairs)==10 and all(pairs))
runtime=json.loads((R/'V26_17_Runtime_Viewport_QA.json').read_text('utf8'));ck('Actual Fast viewport review uses the delivered file and no added lights',len(runtime['captures'])==5 and all(r['model_sha256']==fh and r['actual_viewport']and r['extra_lights']==0 for r in runtime['captures']))
cmd=(O/'启动漫游.cmd').read_text('utf8');ck('One launcher selects this Fast model and its current runtime',sorted(p.name for p in O.glob('*.cmd'))==['启动漫游.cmd']and'Architecture_Complete_V26_17_Fast.blend'in cmd and all((O/'Roam'/p).exists()for p in['start_roam_fast.py','roam_controller_fast.py','roam_physics.py']))
ck('Source V26.16 is preserved byte for byte',sha(Path(ch['source']))==ch['source_sha256'])
run=json.loads((O/'Sources/Check_Run.json').read_text('utf8'));ck('All ten build and validation steps completed',len(run)==10 and all(r['successful_process']for r in run))
fail=[q for q in checks if not q['pass']];out={'status':'PASS'if not fail else'FAIL','master_sha256':mh,'fast_sha256':fh,'checks':checks,'failures':fail};(R/'V26_17_Package_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8');print('PACKAGE_VERIFIED',len(checks),len(fail),flush=True)
if fail:raise AssertionError(fail)
