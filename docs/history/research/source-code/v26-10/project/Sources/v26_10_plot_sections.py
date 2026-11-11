"""Draw measured saved-model sections, without third-party plotting packages."""
from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'))
from PIL import Image,ImageDraw,ImageFont
D=W/'v26_10';rows=json.loads((D/'Wall_Sections_Before_After.json').read_text('utf8'))['sections'];font='C:/Windows/Fonts/msyh.ttc'
f=ImageFont.truetype(font,21);small=ImageFont.truetype(font,17);title=ImageFont.truetype(font,28)
pick=[r for r in rows if abs(r['z_m']-({1:-.44999998807907104,2:3.450024366378784,3:7.050000190734863}[r['floor']]+1.25))<1e-6]
im=Image.new('RGB',(1560,225+len(pick)*215),'#edf1f4');d=ImageDraw.Draw(im)
d.text((35,22),'房间与卫生间交接：保存模型的水平截面',font=title,fill='#20343e');d.text((35,70),'灰红线：V26.9；蓝线：V26.10。按相邻墙面的定位清除旧柱块余量。',font=f,fill='#344c58');d.text((35,105),'每格相同比例；截面取各层地面以上 1.25m。尺寸为原模型和照片关系拟合，并非新增现场测量。',font=small,fill='#64737b')
def lines(g):
 if g['type']=='LineString':return[g['coordinates']]
 if g['type']in['MultiLineString']:return g['coordinates']
 if g['type']=='GeometryCollection':return[q for gg in g['geometries']for q in lines(gg)]
 return[]
for i,r in enumerate(pick):
 y=170+i*215;cx=r['center_x'];d.rounded_rectangle((25,y,1535,y+200),12,fill='white');d.text((45,y+16),f"{r['floor']} 楼 · 交角 X={cx:g}m",font=f,fill='#243d48')
 for ox,key,label,color in [(400,'before_outline','修改前','#ba7d75'),(1005,'after_outline','修改后','#167990')]:
  d.text((ox-80,y+8),label,font=small,fill=color)
  def pt(p):return(ox+(p[0]-cx)*190,y+114-(p[1]-7.3)*190)
  for seg in lines(r[key]):
   if len(seg)>1:d.line([pt(p)for p in seg],fill=color,width=4)
  d.line((ox+160,y+170,ox+198,y+170),fill='#637980',width=2);d.text((ox+156,y+174),'20cm',font=small,fill='#637980')
 d.text((45,y+57),'邻墙平面连续相接',font=small,fill='#637980');d.text((45,y+85),'清理多余凸棱，门洞保留',font=small,fill='#637980')
im.save(D/'Wall_Sections_Before_After.png')
print('SECTIONS_DRAWN',len(pick),flush=True)
