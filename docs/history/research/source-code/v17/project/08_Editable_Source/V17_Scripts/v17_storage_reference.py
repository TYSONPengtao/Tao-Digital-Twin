import sys,json,subprocess,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
W=Path(__file__).parent;sys.path[:0]=[str(W/'libs')]
from PIL import Image,ImageDraw,ImageFont
O=Path(r'E:/jz/JIA/Rebuild_V17/07_Reference/INSV_Storage');O.mkdir(exist_ok=True);V=Path(r'E:/jz/VID_20260507_152114_00_001.insv');FF=r'C:/Users/PENG/anaconda3/Library/bin/ffmpeg.exe'
def one(a):
 t,l=a;p=O/f'INSV_{t}s_L{l}.jpg';vf='v360=input=fisheye:output=flat:ih_fov=180:iv_fov=180:h_fov=110:v_fov=110:w=1200:h=1200'
 r=subprocess.run([FF,'-v','error','-threads','2','-ss',str(t),'-i',str(V),'-map',f'0:v:{l}','-frames:v','1','-vf',vf,'-q:v','2',str(p),'-y'],capture_output=True);assert r.returncode==0,r.stderr;print('FRAME',t,l,flush=True);return {'file':p.name,'seconds':t,'lens':l,'yaw':0,'pitch':0,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_video':str(V),'projection':'Uncalibrated fisheye to flat view; no metric calibration'}
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(one,[(t,l) for t in [688,705,715] for l in [0,1]]))
im=Image.new('RGB',(1500,1030),'#eeeeee');dr=ImageDraw.Draw(im);font=ImageFont.truetype(r'C:/Windows/Fonts/arial.ttf',18)
for i,r in enumerate(rows):
 pic=Image.open(O/r['file']);pic.thumbnail((500,480));x=i%3*500;y=i//3*515;im.paste(pic,(x,y));dr.text((x+5,y+485),f"{r['seconds']} s / lens {r['lens']}",font=font,fill='black')
im.save(O/'Storage_Reference_Contact.jpg',quality=94);(O/'Frame_Index.json').write_text(json.dumps({'source':str(V),'source_bytes':V.stat().st_size,'source_sha256_previously_verified':'3651a3e01ca8d94447aef544ce379a4ef984f6e91a7d7099699812f7a28c237f','rows':rows},ensure_ascii=False,indent=2),encoding='utf8')
