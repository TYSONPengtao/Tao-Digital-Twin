from pathlib import Path
import sys,json,subprocess
from concurrent.futures import ThreadPoolExecutor
W=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(W/'libs'))
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent;V=Path('E:/jz/VID_20260507_152114_00_001.insv');ff=imageio_ffmpeg.get_ffmpeg_exe();tasks=[(t,l)for t in [170,175,180,185,190,195,200,205]for l in [0,1]]
def extract(q):
 t,l=q;fn=f'Actual_F3Terrace_t{t}_Lens{l}_Yaw0_FOV110.jpg';cmd=[ff,'-loglevel','error','-threads','2','-ss',str(t),'-i',str(V),'-map',f'0:v:{l}','-frames:v','1','-vf','v360=input=fisheye:output=flat:ih_fov=180:iv_fov=180:h_fov=110:v_fov=110:yaw=0:w=1200:h=1200','-q:v','3',str(O/fn),'-y'];r=subprocess.run(cmd,capture_output=True);return {'time_seconds':t,'video_lens_stream':l,'source_video':str(V),'file':fn,'yaw_degrees':0,'horizontal_fov_degrees':110,'not_calibrated_for_metric_measurement':True,'success':r.returncode==0,'error':r.stderr.decode('utf8','replace')if r.returncode else''}
with ThreadPoolExecutor(max_workers=3)as ex:rows=list(ex.map(extract,tasks))
(O/'Frame_Provenance.json').write_text(json.dumps(rows,indent=2),'utf8')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for start in [0,8]:
 chunk=rows[start:start+8];sheet=Image.new('RGB',(1600,860),'white');dr=ImageDraw.Draw(sheet)
 for i,r in enumerate(chunk):
  im=Image.open(O/r['file']);im.thumbnail((400,400));x=(i%4)*400;y=(i//4)*430;sheet.paste(im,(x,y));dr.text((x+10,y+402),f"t={r['time_seconds']}s L{r['video_lens_stream']} yaw0",font=font,fill='black')
 sheet.save(O/f'Actual_Contact_{start//8+1}.jpg',quality=94)
print('EXTRACTED',len(rows),'FAIL',sum(not r['success']for r in rows))
