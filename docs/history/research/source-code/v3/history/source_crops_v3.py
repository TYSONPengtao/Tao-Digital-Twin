import sys
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W/'libs'))
from PIL import Image,ImageDraw
im=Image.open(W/'CCM_Orthographic_Local.png');dr=ImageDraw.Draw(im)
for x in range(-25,24):
 px=(x+29)/52*2400;dr.line([(px,0),(px,2400)],fill=(255,180,50),width=1)
 for y in range(-20,14,2):py=(20-y)/52*2400;dr.text((px+3,py+3),f'{x},{y}',fill='yellow',stroke_width=1,stroke_fill='black')
for y in range(-25,18):py=(20-y)/52*2400;dr.line([(0,py),(2400,py)],fill=(255,180,50),width=1)
for name,box in [('SW_Gate_Grid',(-20,-17,-7,-5)),('Inner_Gate_Grid',(0,-19,14,-8)),('Kitchen_Grid',(3,-14,16,0))]:
 x0,y0,x1,y1=box;crop=im.crop(((x0+29)/52*2400,(20-y1)/52*2400,(x1+29)/52*2400,(20-y0)/52*2400));crop.resize((int(crop.width*1.5),int(crop.height*1.5))).save(W/'evidence_v3'/(name+'.png'))
