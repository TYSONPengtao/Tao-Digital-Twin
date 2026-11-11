from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path('E:/jz/JIA/Rebuild_V24_34/Reports');font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
def sheet(files,out,width=960,height=700):
 canvas=Image.new('RGB',(width*2,height*((len(files)+1)//2)),(238,239,240));d=ImageDraw.Draw(canvas)
 for i,(fn,label) in enumerate(files):
  im=Image.open(R/fn).convert('RGB');im.thumbnail((width,height-48));x=(i%2)*width+(width-im.width)//2;y=(i//2)*height;canvas.paste(im,(x,y));d.text(((i%2)*width+16,y+height-40),label,font=font,fill=(30,30,30))
 canvas.save(R/out,quality=92)
files=[('V24_34_01_Expanded_Site.png','扩展后全景'),('V24_34_Expanded_Top.png','原建筑、已有外景与新增外围'),('V24_34_02_Original_House_And_Context.png','保留的原建筑与院落'),('V24_34_03_Added_South_Road.png','新增外景道路的人眼高度')]
if all((R/f).exists()for f,_ in files):sheet(files,'V24_34_Exterior_Review.jpg')
files=[(f'V24_34_Viewport_{tag}_{pose}.png',tag+' '+pose)for tag,pose in [('01_Expanded_Site','A'),('01_Expanded_Site','B'),('03_Added_South_Road','A'),('03_Added_South_Road','B'),('02_Original_House_And_Context','A'),('05_East_Context','A')]]
if all((R/f).exists()for f,_ in files):sheet(files,'V24_34_Viewport_Review.jpg',800,580)
