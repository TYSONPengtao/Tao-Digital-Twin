from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont,ImageOps
W=Path(__file__).parent;R=Path('E:/jz/JIA/Rebuild_V24_37/Reports');font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
def sheet(jobs,dest,w=1600,tileh=610):
 out=Image.new('RGB',(w,tileh*((len(jobs)+1)//2)),(238,242,246));d=ImageDraw.Draw(out);tw=w//2
 for i,(name,caption)in enumerate(jobs):
  im=Image.open(R/name).convert('RGB');thumb=ImageOps.contain(im,(tw-20,tileh-55));x=(i%2)*tw+(tw-thumb.width)//2;y=(i//2)*tileh+45;out.paste(thumb,(x,y));d.text(((i%2)*tw+15,(i//2)*tileh+8),caption,font=font,fill=(28,44,64))
 out.save(R/dest)
q=json.loads((R/'V24_37_Viewport_QA.json').read_text('utf8'));sheet([(r['file'],r['camera']+' '+r['pose'])for r in q['captures']],'V24_37_Viewport_Contact.png',1600,600)
if all((R/('V24_37_'+tag+'.png')).exists()for tag in ['Kitchen_Wall_Eave','House_And_Context','Expanded_Context','PTJIA6_Road_Eye','PTJIA6_Field','Clean_Context_Top']):
 sheet([('V24_37_'+tag+'.png',label)for tag,label in [('Kitchen_Wall_Eave','青砖墙、瓦顶和烟管'),('House_And_Context','原建筑与实景衔接'),('Expanded_Context','连片保留的外景主体'),('Clean_Context_Top','完整田块、道路和植被特征'),('PTJIA6_Road_Eye','PTJIA6道路实景'),('PTJIA6_Field','PTJIA6田块细节')]],'V24_37_Review_Sheet.jpg',1800,670)
print('REVIEW_SHEETS_SAVED')
