import sys
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'libs')]
from PIL import Image,ImageDraw,ImageFont
O=Path(r'E:\jz\JIA\Rebuild_V3');im=Image.open(O/'09_Report/V3_Orthographic_Plan.png').convert('RGB');im=im.resize((1800,1800))
canvas=Image.new('RGB',(2440,2020),(247,248,248));canvas.paste(im,(50,150));d=ImageDraw.Draw(canvas)
font=lambda size:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
d.text((50,30),'V3 场地与构筑物核查图',font=font(46),fill=(24,45,52))
d.text((52,100),'总图 + JIA / PTHOUSE / ui 实景 + DJI 各集合照片交叉核查',font=font(26),fill=(60,75,82))
labels=[
 (1,'主楼及罗马柱',6.5,5,(35,94,143),'图纸尺寸；饰面及弧梁按近景'),
 (2,'中式木构厨房',10.5,-7.1,(165,96,32),'木柱、木梁、格扇及两扇单门'),
 (3,'砖石内院门楼',6.6,-11.7,(95,86,131),'灰色框体、深色双扇木门'),
 (4,'南侧连续照壁',6.5,-16.9,(125,72,130),'实体墙身、抬升瓦顶；不开门'),
 (5,'西南金属车辆门',-13.76,-10.55,(36,111,122),'真实外围入口及坡面衔接'),
 (6,'低木栅栏',-7,-9.8,(165,96,32),'分隔土院与车辆通道'),
 (7,'内院西侧瓦墙',0,-9,(104,103,92),'灰砖外侧、白色内侧、瓦顶'),
 (8,'绿灰色轻型棚',1.8,-5,(36,111,122),'金属覆面；不归类为瓦亭'),
 (9,'茅草棚架',-9,-8,(165,96,32),'木棚架、茅草覆盖'),
 (10,'金属覆面棚屋',-16,5,(36,111,122),'灰色及蓝色棚顶'),
 (11,'东南砖石瓦房',16,-12,(104,103,92),'砖石墙及瓦顶；隐蔽结构待核'),
 (12,'道路与周边地形',-21,-8,(69,107,57),'实景采样重建；非地籍边界')]
for i,title,x,y,color,note in labels:
 px=50+(x+29)/52*1800;py=150+(20-y)/52*1800
 d.ellipse((px-24,py-24,px+24,py+24),fill=color,outline='white',width=3)
 txt=str(i);bb=d.textbbox((0,0),txt,font=font(25));d.text((px-(bb[2]-bb[0])/2,py-19),txt,font=font(25),fill='white')
 yy=195+(i-1)*140;d.ellipse((1900,yy,1948,yy+48),fill=color);d.text((1911,yy+5),txt,font=font(24),fill='white')
 d.text((1964,yy),title,font=font(29),fill=(24,45,52));d.text((1900,yy+62),note,font=font(22),fill=(64,75,78))
d.line([(145,345),(180,247)],fill=(30,48,50),width=5);d.polygon([(180,247),(156,275),(185,285)],fill=(30,48,50));d.text((189,240),'N',font=font(30),fill=(30,48,50))
d.text((52,1968),'现状范围由实景描取；本图用于核查构筑物分类，未经独立控制测量。',font=font(24),fill=(60,75,82))
canvas.save(O/'09_Report/V3_Site_Classification.png');print('Annotated site classification map saved')
