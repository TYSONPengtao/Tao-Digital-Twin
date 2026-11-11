import sys,json,subprocess,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/'libs')]
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent/'Reference';O.mkdir(exist_ok=True)
V=Path('E:/jz/VID_20260507_152114_00_001.insv');FF='C:/Users/PENG/anaconda3/Library/bin/ffmpeg.exe'
tasks=[(600,0,-30,-20),(600,0,0,-20),(625,1,-30,-20),(645,0,35,20),(650,0,40,20),(657,0,0,25),(657,1,0,25),(1040,1,50,15)]
def one(a):
 t,l,y,p=a;f=O/f'INSV_{t:04d}s_L{l}_Y{y:+03d}_P{p:+03d}.jpg'
 if not f.exists():
  vf=f'v360=input=fisheye:output=flat:ih_fov=180:iv_fov=180:h_fov=100:v_fov=100:yaw={y}:pitch={p}:w=1500:h=1500'
  r=subprocess.run([FF,'-v','error','-threads','2','-ss',str(t),'-i',str(V),'-map',f'0:v:{l}','-frames:v','1','-vf',vf,'-q:v','2',str(f),'-y'],capture_output=True);assert r.returncode==0,r.stderr
 return {'file':f.name,'seconds':t,'lens':l,'yaw':y,'pitch':p,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
with ThreadPoolExecutor(max_workers=2) as p:rows=list(p.map(one,tasks))
C=Image.new('RGB',(1600,860),(230,230,230));d=ImageDraw.Draw(C);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
for i,r in enumerate(rows):
 im=Image.open(O/r['file']);im.thumbnail((400,400));x=i%4*400;y=i//4*430;C.paste(im,(x,y));d.text((x+4,y+403),r['file'],font=font,fill='black')
C.save(O/'V20_Gate_Pavilion_Contact.jpg',quality=94)
(O/'Frame_Index.json').write_text(json.dumps({'source_video':str(V),'rows':rows,'projection':'unstitched fisheye rectification, relationship evidence only, no metric survey'},indent=2),encoding='utf8')
print('REFERENCE READY',len(rows))
