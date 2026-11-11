import sys,json,csv,math
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'))
from PIL import Image,ImageDraw,ImageOps,ImageFont
O=Path(r'E:\jz\JIA\Rebuild_V7_Hybrid\07_Evidence\DJI_All_Target_Images');O.mkdir(parents=True,exist_ok=True)
rows=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for group in ['0002','0003']:
 folder=Path(r'D:\DJI')/group/'DCIM/101MEDIA';jpgs=sorted(folder.glob('*.JPG'))
 for idx,p in enumerate(jpgs):
  im=Image.open(p);raw=p.with_suffix('.DNG');ex=im.getexif()
  rows.append({'collection':group,'jpg':str(p),'raw':str(raw) if raw.exists() else '', 'width':im.width,'height':im.height,'datetime':str(ex.get(306,'')),'page':idx//60+1,'slot':idx%60+1,'raw_is_capture_pair':raw.exists()})
 for start in range(0,len(jpgs),60):
  page=Image.new('RGB',(1920,2380),'#ddd');d=ImageDraw.Draw(page);d.text((15,10),f'DJI {group}/DCIM/101MEDIA - ALL JPG captures {start+1}..{min(start+60,len(jpgs))} / {len(jpgs)} (DNG pairs indexed)',font=font,fill='black')
  for j,p in enumerate(jpgs[start:start+60]):
   with Image.open(p) as im:
    im=ImageOps.exif_transpose(im);im.thumbnail((310,210));x=(j%6)*320+5;y=(j//6)*232+40;page.paste(im,(x+(310-im.width)//2,y));d.text((x,y+212),p.name,font=font,fill='black')
  page.save(O/f'ALL_{group}_Page_{start//60+1:02}.jpg',quality=93)
  print(group,'page',start//60+1,flush=True)
(O/'All_Target_Captures.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
with (O/'All_Target_Captures.csv').open('w',encoding='utf-8-sig',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
print('ALL',len(rows),'JPG captures, RAW pairs',sum(r['raw_is_capture_pair'] for r in rows),flush=True)
