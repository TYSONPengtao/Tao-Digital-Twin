import sys,math
from pathlib import Path
sys.path.insert(0,str(Path('work/libs').resolve()))
import fitz
from PIL import Image,ImageDraw
for n in ['55030_full_official','55031_full_0','55038_full_official']:
 d=fitz.open('work/v4_audit_codes/'+n+'.pdf');can=Image.new('RGB',(1000,math.ceil(len(d)/5)*320),'#dddddd');dr=ImageDraw.Draw(can)
 for i,p in enumerate(d):
  pix=p.get_pixmap(matrix=fitz.Matrix(.6,.6));im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples).convert('RGB');im.thumbnail((190,285));x=i%5*200;y=i//5*320;can.paste(im,(x,y+25));dr.text((x+5,y+5),str(i+1),fill='black')
 can.save('work/v4_audit_codes/'+n+'_pages.png')
