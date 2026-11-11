from pathlib import Path
import sys,subprocess,json,hashlib
from concurrent.futures import ThreadPoolExecutor
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'libs'))
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).parent/'References';D.mkdir(exist_ok=True)
V=Path('E:/jz/VID_20260507_152114_00_001.insv');FF='C:/Users/PENG/anaconda3/Library/bin/ffmpeg.exe'
def extract(task):
 t,l=task;f=D/f'Actual_t{t:04d}_L{l}_Pitch-40.jpg'
 if not f.exists():
  vf='v360=input=fisheye:output=flat:ih_fov=180:iv_fov=180:h_fov=110:v_fov=105:pitch=-40:w=1000:h=950'
  r=subprocess.run([FF,'-v','error','-threads','2','-ss',str(t),'-i',str(V),'-map',f'0:v:{l}','-frames:v','1','-vf',vf,'-q:v','2',str(f),'-y'],capture_output=True);assert r.returncode==0,r.stderr
 return {'file':f.name,'time_seconds':t,'lens':l,'projection':'uncalibrated fisheye to flat yaw0 pitch-40 FOV110x105','metric_use':False,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
with ThreadPoolExecutor(max_workers=2)as p:rows=list(p.map(extract,[(t,l)for t in[115,120,125,135,140,145,150,155,270,275]for l in[0,1]]))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
for page,start in enumerate(range(0,len(rows),12),1):
 im=Image.new('RGB',(1440,1050),'#e8e8e8');dr=ImageDraw.Draw(im)
 for i,r in enumerate(rows[start:start+12]):
  f=Image.open(D/r['file']);f.thumbnail((360,310));x=i%4*360;y=i//4*350;im.paste(f,(x,y));dr.text((x+5,y+313),f"t{r['time_seconds']} L{r['lens']}",font=font,fill='black')
 im.save(D/f'Contact_{page}.jpg',quality=95)
(D/'Frame_Provenance.json').write_text(json.dumps({'video':str(V),'rows':rows},indent=2),'utf8')
print('DONE',len(rows),flush=True)
