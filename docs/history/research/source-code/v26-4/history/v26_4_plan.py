from v26_2_common import *
from shapely.geometry import shape
from PIL import Image,ImageDraw,ImageFont
D=W/'v26_4';src=json.loads((W/'v26_3/Exact_House_Parts.json').read_text('utf8'))
im=Image.new('RGB',(1800,1250),'white');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
for j,z in enumerate([.5,1.8,2.7,3.1]):
 p=shape(next(r['outline']for r in src['layers']if r['z_m'][0]<=z<r['z_m'][1]));ox=30+(j%2)*900;oy=60+(j//2)*600;s=90
 def xy(a):return(ox+(a[0]-3.4)*s,oy+(10.4-a[1])*s)
 dr.text((ox,oy-40),'V26.3 一楼实际剖切 Z='+str(z)+' m',font=font,fill='black')
 for poly in [p]if p.geom_type=='Polygon'else p.geoms:
  dr.polygon([xy(a)for a in poly.exterior.coords],fill='#bbc5ca',outline='#152934')
  for h in poly.interiors:dr.polygon([xy(a)for a in h.coords],fill='white',outline='#152934')
 for x in [4,5,6,7,8,9,10,11,12,13]:dr.text(xy([x,5.5]),str(x),font=font,fill='black')
 for x,y,t in [(6.4,8.6,'楼梯间'),(9.7,8.5,'楼梯口卫生间'),(11.7,8.5,'右侧卫生间'),(11,6.3,'右侧房间')]:dr.text(xy([x-.6,y]),t,font=font,fill='#27617f')
 # crop each cell to the relevant part of the building
im.save(D/'F1_Plan_Before.png')
print('F1_PLAN_READY')
