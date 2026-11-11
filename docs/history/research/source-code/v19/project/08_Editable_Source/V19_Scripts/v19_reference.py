import sys,json,subprocess,hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
W=Path(__file__).parent;sys.path[:0]=[str(W/'libs')]
from PIL import Image,ImageDraw,ImageFont
O=Path(r'E:/jz/JIA/Rebuild_V19/07_Reference/INSV_Perimeter');O.mkdir(parents=True,exist_ok=True);V=Path(r'E:/jz/VID_20260507_152114_00_001.insv');FF=r'C:/Users/PENG/anaconda3/Library/bin/ffmpeg.exe'
tasks=[(t,l,0,0) for t in [870,880,890,900,910,930,950,972,1000,1040,1080,1120,1170,1210] for l in [0,1]]
def one(a):
 t,l,y,p=a;fp=O/f'INSV_{t:04d}s_L{l}_Y{y:+03d}_P{p:+03d}.jpg';vf=f'v360=input=fisheye:output=flat:ih_fov=180:iv_fov=180:h_fov=110:v_fov=110:yaw={y}:pitch={p}:w=1400:h=1400'
 if not fp.exists():
  r=subprocess.run([FF,'-v','error','-threads','2','-ss',str(t),'-i',str(V),'-map',f'0:v:{l}','-frames:v','1','-vf',vf,'-q:v','2',str(fp),'-y'],capture_output=True);assert r.returncode==0,r.stderr.decode(errors='replace')
 print('FRAME',t,l,y,p,flush=True);return {'file':fp.name,'seconds':t,'lens':l,'yaw':y,'pitch':p,'sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'projection':'Uncalibrated fisheye to flat reference view, not survey photogrammetry'}
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(one,tasks))
font=ImageFont.truetype(r'C:/Windows/Fonts/arial.ttf',18)
for page in range(3):
 rr=rows[page*12:(page+1)*12]
 if not rr:continue
 can=Image.new('RGB',(1600,1245),(240,240,240));dr=ImageDraw.Draw(can)
 for j,r in enumerate(rr):
  pic=Image.open(O/r['file']);pic.thumbnail((400,385));x=j%4*400;y=j//4*415;can.paste(pic,(x,y));dr.text((x+6,y+390),f"{r['seconds']//60:02d}:{r['seconds']%60:02d} / lens {r['lens']}",font=font,fill=(25,25,25))
 can.save(O/f'Perimeter_Contact_{page+1:02d}.jpg',quality=94)
(O/'Frame_Index.json').write_text(json.dumps({'source':str(V),'source_bytes':V.stat().st_size,'source_sha256_previously_verified':'3651a3e01ca8d94447aef544ce379a4ef984f6e91a7d7099699812f7a28c237f','user_confirmed_reference_seconds':890,'rows':rows},ensure_ascii=False,indent=2),encoding='utf8')
print('PERIMETER REFERENCE READY',len(rows),flush=True)
