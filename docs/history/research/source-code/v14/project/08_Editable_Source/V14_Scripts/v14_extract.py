import sys,json,subprocess,math,hashlib
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'))
from PIL import Image,ImageDraw,ImageFont
P=Path(r'E:\VID_20260507_152114_00_001.mp4');O=Path(r'E:\jz\JIA\Rebuild_V14\07_Reference\MP4');O.mkdir(parents=True,exist_ok=True)
FF=r'C:\Users\PENG\anaconda3\Library\bin\ffmpeg.exe';font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',18)
rows=[]
for t in range(0,65,2):
 if t>=64.39:continue
 p=O/f'Panorama_{t:04d}s.jpg'
 r=subprocess.run([FF,'-v','error','-threads','2','-ss',str(t),'-i',str(P),'-frames:v','1','-vf','scale=2400:1200','-q:v','2','-y',str(p)],capture_output=True)
 assert r.returncode==0,r.stderr
 rows.append({'file':p.name,'seconds':t,'projection':'equirectangular 360 panorama','source':str(P),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 print('FRAME',t,flush=True)
for start in range(0,len(rows),8):
 chunk=rows[start:start+8];im=Image.new('RGB',(1600,430*math.ceil(len(chunk)/2)),'#eeeeee');d=ImageDraw.Draw(im)
 for i,row in enumerate(chunk):
  pic=Image.open(O/row['file']);pic.thumbnail((800,400));x=i%2*800;y=i//2*430;im.paste(pic,(x,y));d.text((x+8,y+400),f"MP4 {row['seconds']}s",font=font,fill='black')
 im.save(O/f'Contact_{start//8+1:02d}.jpg',quality=93)
meta={'source':str(P),'source_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'duration_seconds':64.397734,'frame_count':len(rows),'rows':rows,'metric_use':False}
(O/'Frame_Index.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
print('DONE',len(rows),flush=True)
