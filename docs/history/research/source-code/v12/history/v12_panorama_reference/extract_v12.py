import sys, json, subprocess, math, csv, hashlib, re, shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'libs'))
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
O=Path(r'E:\jz\JIA\Rebuild_V12\07_Reference\Panorama')
VIDEO=Path(r'E:\jz\VID_20260507_152114_00_001.insv')
FF=imageio_ffmpeg.get_ffmpeg_exe()
O.mkdir(parents=True,exist_ok=True)
PROJECTION='uncalibrated equidistant 180 degree fisheye to flat 90 degree view, no lens stitching'

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()

def extract(a):
 group,t,l,y,p=a
 fn=f'{group}_L{l}_{t:04d}s_Y{y:+03d}_P{p:+03d}.jpg'
 dst=O/fn
 vf=f'v360=input=fisheye:output=flat:ih_fov=180:iv_fov=180:h_fov=90:v_fov=90:yaw={y}:pitch={p}:w=1600:h=1600'
 cmd=[FF,'-loglevel','error','-threads','2','-ss',str(t),'-i',str(VIDEO),'-map',f'0:v:{l}','-frames:v','1','-vf',vf,'-q:v','2',str(dst),'-y']
 r=subprocess.run(cmd,capture_output=True)
 row=dict(file=fn,group=group,seconds=t,stream=f'0:v:{l}',lens=l,yaw_degrees=y,pitch_degrees=p,horizontal_fov_degrees=90,vertical_fov_degrees=90,projection=PROJECTION,source_video=str(VIDEO),output_sha256=digest(dst) if dst.exists() else None,metric_use=False,observations='pending visual inspection',uncertainty='uncalibrated lens intrinsics; held-camera rotation; inferred field angle; no metric scale',success=r.returncode==0,error=r.stderr.decode(errors='replace') if r.returncode else '')
 print('FRAME',fn,row['success'],flush=True)
 return row

tasks=[]
# Early kitchen eave exterior and later interior return route.
for t in [0,2,5,8,12,1025,1040,1046,1055,1070,1090,1121]:
 for l in [0,1]:tasks.append(('Kitchen',t,l,0,0))
for t,l in [(2,0),(5,0),(8,0),(12,0),(1040,0),(1046,0),(1046,1),(1055,0),(1070,0),(1090,1),(1121,0),(1121,1)]:
 tasks.append(('Kitchen',t,l,0,35))
for t,l in [(5,0),(1046,0),(1046,1)]:
 for y in [-35,35]:tasks.append(('Kitchen',t,l,y,10))
# Eye level and downward reference covering court, gate, pavement, road gradients.
for t in [20,40,65,79,600,625,650,674,700,725,749,775,800,823,850,875,897,925,950,972]:
 for l in [0,1]:tasks.append(('Ground',t,l,0,0))
for t in [20,40,65,79,600,625,650,674,725,775,823,875,897,925,972]:
 for l in [0,1]:tasks.append(('Ground',t,l,0,-35))

meta=subprocess.run([FF,'-hide_banner','-i',str(VIDEO)],capture_output=True).stderr.decode('utf-8',errors='replace')
(O/'Video_Metadata.txt').write_text(meta,encoding='utf-8')
rows=[]
with ThreadPoolExecutor(max_workers=3) as pool:
 hf=pool.submit(digest,VIDEO)
 for future in as_completed([pool.submit(extract,a) for a in tasks]):rows.append(future.result())
 source_hash=hf.result()
rows.sort(key=lambda r:(r['group'],r['seconds'],r['lens'],r['yaw_degrees'],r['pitch_degrees']))
for r in rows:r['source_sha256']=source_hash
(O/'Frame_Index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with (O/'Frame_Index.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',20)
for group in ['Kitchen','Ground']:
 rs=[r for r in rows if r['group']==group]
 for start in range(0,len(rs),16):
  chunk=rs[start:start+16];sheet=Image.new('RGB',(1440,390*math.ceil(len(chunk)/4)),'#dddddd')
  for i,r in enumerate(chunk):
   if not r['success']:continue
   im=Image.open(O/r['file']);im.thumbnail((360,360));x=i%4*360;y=i//4*390;sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+4,y+363),f"{r['seconds']}s L{r['lens']} Y{r['yaw_degrees']} P{r['pitch_degrees']}",font=font,fill='black')
  sheet.save(O/f'{group}_Contact_{start//16+1:02d}.jpg',quality=94)
raw=O/'Raw_L0_0005s.jpg'
r=subprocess.run([FF,'-loglevel','error','-threads','2','-ss','5','-i',str(VIDEO),'-map','0:v:0','-frames:v','1','-q:v','2',str(raw),'-y'],capture_output=True)
qa=dict(status='PASS' if all(r['success'] for r in rows) and r.returncode==0 else 'FAIL',source=str(VIDEO),source_sha256=source_hash,source_bytes=VIDEO.stat().st_size,duration_seconds=1274.77,dual_fisheye_streams=2,stream_pixels=[3840,3840],extracted_views=len(rows),redecoded_from_original=True,raw_fisheye_frame=str(raw),raw_sha256=digest(raw),projection=PROJECTION,stitched=False,metric_use=False)
(O/'Extraction_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(qa,ensure_ascii=False),flush=True)
