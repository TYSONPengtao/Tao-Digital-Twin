import sys,json,subprocess,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
W=Path(__file__).parent;sys.path[:0]=[str(W/'libs')]
from PIL import Image,ImageDraw,ImageFont
O=Path(r'E:/jz/JIA/Rebuild_V19/07_Reference/INSV_Perimeter');V=Path(r'E:/jz/VID_20260507_152114_00_001.insv');FF=r'C:/Users/PENG/anaconda3/Library/bin/ffmpeg.exe';tasks=[(890,0,-50,5),(890,1,50,5),(870,0,-45,10),(875,0,-55,15),(925,1,45,10),(935,1,45,15),(945,1,25,15),(950,1,0,15)]
def one(a):
 t,l,y,p=a;fp=O/f'INSV_{t:04d}s_L{l}_Y{y:+03d}_P{p:+03d}.jpg';vf=f'v360=input=fisheye:output=flat:ih_fov=180:iv_fov=180:h_fov=85:v_fov=85:yaw={y}:pitch={p}:w=2200:h=2200';r=subprocess.run([FF,'-v','error','-threads','2','-ss',str(t),'-i',str(V),'-map',f'0:v:{l}','-frames:v','1','-vf',vf,'-q:v','2',str(fp),'-y'],capture_output=True);assert r.returncode==0,r.stderr;print('DETAIL',t,l,y,p,flush=True);return {'file':fp.name,'seconds':t,'lens':l,'yaw':y,'pitch':p,'sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'projection':'Uncalibrated fish-eye face view; texture and visible relationship reference only'}
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(one,tasks))
can=Image.new('RGB',(1800,965),(240,240,240));dr=ImageDraw.Draw(can);ft=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for j,r in enumerate(rows):
 pic=Image.open(O/r['file']);pic.thumbnail((450,450));x=j%4*450;y=j//4*482;can.paste(pic,(x,y));dr.text((x+5,y+453),f"{r['seconds']}s L{r['lens']} Y{r['yaw']} P{r['pitch']}",font=ft,fill='black')
can.save(O/'Perimeter_Detail_Contact.jpg',quality=94);idx=json.loads((O/'Frame_Index.json').read_text(encoding='utf8'));idx['detail_rows']=rows;(O/'Frame_Index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2),encoding='utf8')
