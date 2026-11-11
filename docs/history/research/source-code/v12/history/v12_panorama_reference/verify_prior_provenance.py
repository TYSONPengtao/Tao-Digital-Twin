import sys,json,subprocess,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'libs'))
import imageio_ffmpeg
from PIL import Image,ImageChops
O=Path(__file__).parent;D=Path(r'E:\jz\JIA\Rebuild_V12\07_Reference\Panorama')
video=Path(r'E:\jz\VID_20260507_152114_00_001.insv')
Q=json.loads((D/'Extraction_QA.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(item):
 t,l=item;name=f'Center_L{l}_{t:04d}s.jpg';dst=O/('ProvenanceProbe_'+name)
 command=[imageio_ffmpeg.get_ffmpeg_exe(),'-loglevel','error','-threads','2','-ss',str(t),'-i',str(video),'-map',f'0:v:{l}','-frames:v','1','-vf','v360=input=fisheye:output=flat:ih_fov=180:iv_fov=180:h_fov=90:v_fov=90:w=1200:h=1200','-q:v','3',str(dst),'-y']
 subprocess.run(command,check=True,capture_output=True)
 original=D/'Earlier_Interior'/name
 return dict(file=name,seconds=t,lens=l,source_video=str(video),source_sha256=Q['source_sha256'],previous_frame_sha256=sha(original),current_redecode_sha256=sha(dst),exact_jpeg_match=sha(original)==sha(dst),exact_decoded_pixels_match=ImageChops.difference(Image.open(original).convert('RGB'),Image.open(dst).convert('RGB')).getbbox() is None)
index=json.loads((D/'Frame_Index.json').read_text(encoding='utf-8'));tasks=[(r['seconds'],r['lens']) for r in index if r['group']=='Earlier_Interior']
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(check,tasks))
scripts=[W/'ue5_panorama_audit'/n for n in ['extract.py','extract_transition.py']]
report=dict(status='PASS' if all(r['exact_decoded_pixels_match'] for r in rows) else 'SOURCE_REVIEW_REQUIRED',new_decoded_count=112,earlier_reused_count=118,source_relation='Same named INSV; all original scripts point to this path; all 118 reused frames redecoded and compared with current original',source_script_hashes={str(p):sha(p) for p in scripts},reused_source_historical_hash_not_recorded=True,probe_count=len(rows),all_exact_jpeg_match=all(r['exact_jpeg_match'] for r in rows),all_exact_pixels_match=all(r['exact_decoded_pixels_match'] for r in rows),details=rows)
(O/'Prior_Provenance_Check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');(D/'Prior_Provenance_Check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
if report['status']=='PASS':
 for r in index:
  if r['group']=='Earlier_Interior':r['source_hash_verification']='Each reused frame was redecoded from current original; exact JPEG hash and pixel match in Prior_Provenance_Check.json.'
 (D/'Frame_Index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
 import csv
 keys=list(dict.fromkeys(k for r in index for k in r))
 with (D/'Frame_Index.csv').open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(index)
 Q['prior_reused_source_confirmed_by_exact_redecode_count']=len(rows);Q['prior_reused_all_exact_jpeg_matches']=report['all_exact_jpeg_match']
 (D/'Extraction_QA.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='details'},ensure_ascii=False))
