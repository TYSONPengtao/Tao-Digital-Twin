import subprocess,json,hashlib
from pathlib import Path
V=Path('E:/VID_20260507_152114_00_001.mp4');O=Path(__file__).parent/'v24_10/Video';O.mkdir(parents=True,exist_ok=True)
FF='C:/Users/PENG/anaconda3/Library/bin/ffmpeg.exe'
tasks=[(4,-30,12),(8,-30,10),(10,-25,14),(12,-135,8),(14,-140,10),(34,-50,0),(38,40,15),(54,-100,0)]
rows=[]
for t,y,p in tasks:
 n=f'MP4_{t:02d}s_Y{y:+04d}_P{p:+03d}.jpg';vf=f'v360=input=e:output=flat:yaw={y}:pitch={p}:h_fov=100:v_fov=90:w=1200:h=1000'
 r=subprocess.run([FF,'-v','error','-threads','3','-ss',str(t),'-i',str(V),'-frames:v','1','-vf',vf,'-q:v','2','-y',str(O/n)],capture_output=True)
 assert r.returncode==0,r.stderr.decode(errors='replace')
 rows.append({'seconds':t,'yaw':y,'pitch':p,'file':n});print(n,flush=True)
(O/'Frame_Index.json').write_text(json.dumps({'source':str(V),'source_sha256':hashlib.file_digest(V.open('rb'),'sha256').hexdigest(),'projection':'Perspective from equirectangular MP4; qualitative appearance only, no metric calibration','views':rows},ensure_ascii=False,indent=2),encoding='utf8')
