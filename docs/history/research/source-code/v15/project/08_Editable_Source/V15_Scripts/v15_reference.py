import sys,json,subprocess,hashlib,math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
W=Path(__file__).parent;sys.path[:0]=[str(W/'libs')]
from PIL import Image,ImageDraw,ImageFont
O=Path(r'E:/jz/JIA/Rebuild_V15/07_Reference/INSV');O.mkdir(parents=True,exist_ok=True);V=Path(r'E:/jz/VID_20260507_152114_00_001.insv');FF=r'C:/Users/PENG/anaconda3/Library/bin/ffmpeg.exe'
tasks=[]
for t,l,y,p in [(160,0,0,0),(160,1,0,0),(215,0,0,0),(232,0,-30,-25),(235,0,-35,0),(235,0,35,-25),(265,1,0,0),(268,1,0,0),(674,0,0,0),(674,1,0,0),(700,0,0,0),(700,1,0,0),(725,0,0,0),(725,1,0,0),(749,0,0,-25),(749,1,0,0),(775,0,0,-35),(775,1,0,0),(950,1,0,0),(972,1,0,0),(1040,1,0,0),(1121,1,0,0)]:tasks.append((t,l,y,p))
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def extract(a):
 t,l,y,p=a;fn=f'INSV_L{l}_{t:04d}s_Y{y:+03d}_P{p:+03d}.jpg';dst=O/fn
 vf=f'v360=input=fisheye:output=flat:ih_fov=180:iv_fov=180:h_fov=100:v_fov=100:yaw={y}:pitch={p}:w=1200:h=1200'
 r=subprocess.run([FF,'-v','error','-threads','2','-ss',str(t),'-i',str(V),'-map',f'0:v:{l}','-frames:v','1','-vf',vf,'-q:v','2',str(dst),'-y'],capture_output=True);assert r.returncode==0,r.stderr.decode(errors='replace')
 print('FRAME',fn,flush=True);return {'file':fn,'seconds':t,'lens':l,'yaw':y,'pitch':p,'sha256':sh(dst),'source_video':str(V),'projection':'Uncalibrated 180 degree fisheye to 100 degree flat view; not stitched; used to identify visible relationships, not derive metric dimensions'}
rows=[]
with ThreadPoolExecutor(max_workers=3) as ex:
 for fu in as_completed([ex.submit(extract,a) for a in tasks]):rows.append(fu.result())
rows.sort(key=lambda r:(r['seconds'],r['lens'],r['yaw']));font=ImageFont.truetype(r'C:/Windows/Fonts/arial.ttf',18)
for start in range(0,len(rows),12):
 ch=rows[start:start+12];s=Image.new('RGB',(1440,390*math.ceil(len(ch)/4)),'#ddd')
 for i,r in enumerate(ch):
  im=Image.open(O/r['file']);im.thumbnail((360,360));x=i%4*360;y=i//4*390;s.paste(im,(x,y));ImageDraw.Draw(s).text((x+4,y+363),f"{r['seconds']}s L{r['lens']} Y{r['yaw']} P{r['pitch']}",font=font,fill='black')
 s.save(O/f'V15_Contact_{start//12+1:02d}.jpg',quality=93)
prior=json.loads(Path(r'E:/jz/JIA/Rebuild_V12/07_Reference/Panorama/Extraction_QA.json').read_text(encoding='utf8'));h=hashlib.sha256()
with V.open('rb') as f:
 for b in iter(lambda:f.read(16*1024*1024),b''):h.update(b)
assert h.hexdigest()==prior['source_sha256']
(O/'Frame_Index.json').write_text(json.dumps({'source_sha256':h.hexdigest(),'duration_seconds':1274.7735,'source_bytes':V.stat().st_size,'new_frames':rows},ensure_ascii=False,indent=2),encoding='utf8');print('REFERENCE PASS',len(rows),flush=True)
