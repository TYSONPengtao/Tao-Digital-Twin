import sys, json, subprocess, math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'libs'))
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
O=Path(__file__).resolve().parent
VIDEO=Path(r'E:\jz\VID_20260507_152114_00_001.insv')
ff=imageio_ffmpeg.get_ffmpeg_exe()
T=[158,162,205,210,212,218,223,228,232,237,268,315,338,355,410,440,455,530,570,588]
tasks=[(t,l,0) for t in T for l in [0,1]]
tasks += [(t,l,y) for t,l in [(160,0),(215,0),(230,0),(235,0),(265,1),(350,0),(450,0),(580,0)] for y in [-40,40]]
def run(a):
 t,l,y=a;fn=f'Wide_L{l}_{t:04d}s_Y{y:+03d}.jpg'
 cmd=[ff,'-loglevel','error','-threads','2','-ss',str(t),'-i',str(VIDEO),'-map',f'0:v:{l}','-frames:v','1','-vf',f'v360=input=fisheye:output=flat:ih_fov=180:iv_fov=180:h_fov=110:v_fov=110:yaw={y}:w=1200:h=1200','-q:v','3',str(O/fn),'-y']
 r=subprocess.run(cmd,capture_output=True)
 return dict(t=t,lens=l,yaw=y,file=fn,success=r.returncode==0,metric_use=False)
rows=[]
with ThreadPoolExecutor(max_workers=3) as ex:
 for f in as_completed([ex.submit(run,a) for a in tasks]):
  r=f.result(); rows.append(r);print(len(rows),r['file'],r['success'],flush=True)
rows.sort(key=lambda r:(r['t'],r['lens'],r['yaw']))
(O/'View_Index.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',20)
for start in range(0,len(rows),16):
 chunk=rows[start:start+16];s=Image.new('RGB',(1536,414*math.ceil(len(chunk)/4)),'#ddd')
 for i,r in enumerate(chunk):
  if not r['success']:continue
  im=Image.open(O/r['file']);im.thumbnail((384,384));x=i%4*384;y=i//4*414;s.paste(im,(x,y));ImageDraw.Draw(s).text((x+4,y+388),f"t={r['t']} L{r['lens']} Y{r['yaw']}",font=font,fill='black')
 s.save(O/f'Wide_Contact_{start//16+1:02d}.jpg',quality=94)
print('done',flush=True)
