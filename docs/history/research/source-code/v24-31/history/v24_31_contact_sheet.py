from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path('E:/jz/JIA/Rebuild_V24_31/Reports');font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',26);head=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',38);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
im=Image.new('RGB',(1920,2230),'#f4f3ef');d=ImageDraw.Draw(im);d.text((35,20),'V24.31  模型修复检查图',font=head,fill='#202a30');d.text((36,77),'补齐地面与窗下墙 · 白色天花 · 平整白墙 · 实景木扶手',font=small,fill='#4c5358')
views=[('Storage_Ground_Closed','内门与储藏间前：缺口补齐，灰色材质统一'),('Outer_Pad_Curb','外院白色场地与路沿：重叠面清理'),('Bay_Right_Complete','窗下墙体完整接至楼板边'),('Bathroom_Smooth_Wall','卫生间高窗：凸块和旧窗套清除'),('Stair_Upper_Reference','按实景拟合深红木色车木扶手'),('White_Ceiling','白色天花，墙面交接收平')]
for i,(tag,label)in enumerate(views):
 x=(i%2)*960;y=125+(i//2)*700;p=Image.open(R/('V24_31_'+tag+'.png')).convert('RGB');p=p.resize((940,646),Image.Resampling.LANCZOS);im.paste(p,(x+10,y));d.text((x+20,y+652),label,font=font,fill='#222e34')
im.save(R/'V24_31_Repair_Contact_Sheet.jpg',quality=94)
