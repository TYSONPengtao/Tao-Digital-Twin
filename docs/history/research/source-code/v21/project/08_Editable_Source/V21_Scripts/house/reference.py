import sys,json,subprocess,math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
W=Path(__file__).parents[1];sys.path[:0]=[str(W/'libs')]
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).parent/'Reference';D.mkdir(exist_ok=True)
FF='C:/Users/PENG/anaconda3/Library/bin/ffmpeg.exe';V='E:/jz/VID_20260507_152114_00_001.insv'
tasks=[(t,l,0,0) for t in [170,185,200] for l in [0,1]]+[(155,0,25,-5),(165,0,-20,-5)]
def extract(a):
 t,l,y,p=a;n=f'INSV_L{l}_{t:04d}s_Y{y:+03d}_P{p:+03d}.jpg';dst=D/n
 vf=f'v360=input=fisheye:output=flat:ih_fov=180:iv_fov=180:h_fov=100:v_fov=100:yaw={y}:pitch={p}:w=1200:h=1200'
 if not dst.exists():
  r=subprocess.run([FF,'-v','error','-threads','2','-ss',str(t),'-i',V,'-map',f'0:v:{l}','-frames:v','1','-vf',vf,'-q:v','2',str(dst),'-y'],capture_output=True);assert r.returncode==0,r.stderr
 return {'file':n,'seconds':t,'lens':l,'yaw':y,'pitch':p}
with ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(extract,tasks))
f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);s=Image.new('RGB',(1440,780),'#ddd');dr=ImageDraw.Draw(s)
for i,r in enumerate(rows):
 im=Image.open(D/r['file']);im.thumbnail((360,360));x=i%4*360;y=i//4*390;s.paste(im,(x,y));dr.text((x+4,y+363),f"{r['seconds']}s L{r['lens']}",font=f,fill='black')
s.save(D/'House_Contact.jpg',quality=94);(D/'Frame_Index.json').write_text(json.dumps({'source':V,'projection':'individual fisheye uncalibrated flat; not metric survey','frames':rows},indent=2));print('frames',len(rows))
