import json
from pathlib import Path
from PIL import Image,ImageDraw
W=Path(__file__).parent;D=W/'v24_31';rows=json.loads((D/'Plan_Outlines.json').read_text('utf8'))
im=Image.new('RGB',(1600,1100),'white');dr=ImageDraw.Draw(im);s=30;origin=(820,440)
def p(q):return (origin[0]+q[0]*s,origin[1]-q[1]*s)
colors=['#c8c9cd','#d5bc93','#d4d7a8','#e8d9a7','#e5c3b6','#c4c8cf','#919ac9','#9d8e77','#bbceec','#f3f2e7','#9cccae','#96c7c8','#7b8495','#ccc191','#f49a8c','#f7b4ba']
for i,r in enumerate(rows[:16]):
 g=r['outline'];polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
 for poly in polys:
  dr.polygon([p(q)for q in poly[0]],fill=colors[i],outline='black')
  for hole in poly[1:]:dr.polygon([p(q)for q in hole],fill='white',outline='gray')
for x in range(-26,23,2):
 a=p((x,-19));b=p((x,15));dr.line([a,b],fill='#999999',width=1);dr.text((a[0],a[1]-12),str(x),fill='black')
for y in range(-18,15,2):
 a=p((-26,y));b=p((23,y));dr.line([a,b],fill='#999999',width=1);dr.text(a,str(y),fill='black')
for i,r in enumerate(rows[:16]):dr.rectangle((15,15+i*17,30,28+i*17),fill=colors[i]);dr.text((38,15+i*17),r['name'],fill='black')
im.save(D/'Plan.png')
