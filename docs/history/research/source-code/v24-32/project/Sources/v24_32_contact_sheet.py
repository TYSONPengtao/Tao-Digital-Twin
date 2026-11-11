from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path('E:/jz/JIA/Rebuild_V24_32/Reports');font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25);head=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',38);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
im=Image.new('RGB',(1920,2230),'#f4f3ef');d=ImageDraw.Draw(im);d.text((35,20),'V24.32  外墙、扶手与门开向修正',font=head,fill='#202a30');d.text((36,77),'高窗下凸块与楼层饰带清除 · 窗下重面清理 · 扶手接续 · 露台瓷砖补齐',font=small,fill='#4c5358')
views=[('Exterior_Right_Flat','高窗下墙面收平，楼层饰带去除'),('Exterior_Back_Flat','后立面连续，楼板残留凸块清除'),('Stair_Joints','扶手与端柱连接，删除多余短栏杆'),('F3_Rear_Guard','三楼楼梯口缺失的后侧护栏补齐'),('F3_Terrace_Wall','旧门洞形白色缺块补齐同材质瓷砖'),('F3_Opposite_Door','三楼标记房门换到另一侧铰接')]
for i,(tag,label)in enumerate(views):
 x=(i%2)*960;y=125+(i//2)*700;p=Image.open(R/('V24_32_'+tag+'.png')).convert('RGB');p=p.resize((940,646),Image.Resampling.LANCZOS);im.paste(p,(x+10,y));d.text((x+20,y+652),label,font=font,fill='#222e34')
im.save(R/'V24_32_Repair_Contact_Sheet.jpg',quality=94)
