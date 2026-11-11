from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json
R=Path('E:/jz/JIA/Rebuild_V24_33/Reports');font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24);head=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',36);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
labels=[('01_Landing_Threshold','01 楼梯口白缝归并为同标高灰色楼面'),('02_Terrace_Flush_Floor','02 删除露台凸板，清除穿出的屋面瓦片'),('03_Stair_Flat_Wall','03 复核楼梯白墙，横向凸带已收平'),('04_F3_Well_Edge','04 三楼护栏下的楼面交接统一为灰色'),('05_Kitchen_Clean_Brick','05 厨房砖墙上的旧柱头与悬挂木件清除'),('06_Storage_Flush_Passage','06 删除叠加门槛，廊下地面齐平连接'),('07_F3_Opposite_Door','07 保留对侧铰链与向室内开启，动作复核'),('08_South_Continuous_Blue_Brick','08 青砖墙连续恢复，打叉的多余端柱删除')]
im=Image.new('RGB',(1920,2965),'#f4f3ef');d=ImageDraw.Draw(im);d.text((30,20),'V24.33  模型问题修正',font=head,fill='#202a30');d.text((32,76),'对应本次 8 张标注图 · 原生模型最终状态 · 原楼层标高与踏步保留',font=small,fill='#4c5358')
for i,(tag,label) in enumerate(labels):
 x=i%2*960;y=120+i//2*700;p=Image.open(R/('V24_33_'+tag+'.png')).convert('RGB');p=ImageOps.contain(p,(940,646),Image.Resampling.LANCZOS);im.paste(p,(x+10+(940-p.width)//2,y+(646-p.height)//2));d.text((x+20,y+653),label,font=font,fill='#222e34')
im.save(R/'V24_33_Repair_Contact_Sheet.jpg',quality=94)
views=json.loads((Path(__file__).parent/'v24_33/Views.json').read_text('utf8'));over=Image.new('RGB',(1920,850),'#f4f3ef');dr=ImageDraw.Draw(over);dr.text((30,18),'V24.33  整体核对',font=head,fill='#202a30')
for i,tag in enumerate(['09_Exterior','10_Whole_Site']):
 p=ImageOps.contain(Image.open(R/('V24_33_'+tag+'.png')).convert('RGB'),(940,700),Image.Resampling.LANCZOS);over.paste(p,(i*960+10+(940-p.width)//2,90))
over.save(R/'V24_33_Overall_Review.jpg',quality=94)
