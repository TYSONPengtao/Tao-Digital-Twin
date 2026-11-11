import sys,json,subprocess,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
W=Path(__file__).parent.parent;sys.path[:0]=[str(W/'libs')]
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent/'Reference';O.mkdir(exist_ok=True)
V=Path('E:/jz/VID_20260507_152114_00_001.insv');FF='C:/Users/PENG/anaconda3/Library/bin/ffmpeg.exe'
tasks=[(710,0,0,0),(710,1,0,0),(715,0,-25,5),(715,1,25,5),(720,0,0,0),(720,1,0,0),(725,0,0,0),(725,1,0,0)]
def one(a):
 t,l,y,p=a;fp=O/f'INSV_{t:04d}s_L{l}_Y{y:+03d}_P{p:+03d}.jpg'
 vf=f'v360=input=fisheye:output=flat:ih_fov=180:iv_fov=180:h_fov=95:v_fov=95:yaw={y}:pitch={p}:w=1700:h=1700'
 if not fp.exists():
  r=subprocess.run([FF,'-v','error','-threads','2','-ss',str(t),'-i',str(V),'-map',f'0:v:{l}','-frames:v','1','-vf',vf,'-q:v','2',str(fp),'-y'],capture_output=True);assert r.returncode==0,r.stderr
 return {'file':fp.name,'seconds':t,'lens':l,'yaw':y,'pitch':p,'sha256':hashlib.sha256(fp.read_bytes()).hexdigest()}
with ThreadPoolExecutor(max_workers=2) as p:rows=list(p.map(one,tasks))
can=Image.new('RGB',(1600,850),(240,240,240));dr=ImageDraw.Draw(can);ft=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for j,r in enumerate(rows):
 im=Image.open(O/r['file']);im.thumbnail((400,400));x=j%4*400;y=j//4*425;can.paste(im,(x,y));dr.text((x+4,y+402),f"{r['seconds']}s L{r['lens']} Y{r['yaw']} P{r['pitch']}",font=ft,fill='black')
can.save(O/'Storage_Walk_Contact.jpg',quality=94)
(O/'Frame_Index.json').write_text(json.dumps({'source':str(V),'projection':'Uncalibrated fisheye extraction; topology and surface reference, not measured dimensions','rows':rows},ensure_ascii=False,indent=2),encoding='utf8')
print('REFERENCE',len(rows),flush=True)
