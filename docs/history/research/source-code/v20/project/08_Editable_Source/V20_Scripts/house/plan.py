from pathlib import Path
exec((Path(__file__).parent/'inventory.py').read_text().split('rows=[]')[0])
from PIL import Image,ImageDraw,ImageFont
im=Image.new('RGB',(2250,780),'white');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
for fi,(level,label) in enumerate(zip([0,3.9,7.5],['F1','F2','F3'])):
 def pt(p):return (fi*750+35+p[0]*47,730-p[1]*64)
 for x in range(14):dr.line([pt([x,0]),pt([x,10])],fill='#eee');dr.text(pt([x,0]),str(x),font=font,fill='#aaa')
 for y in range(11):dr.line([pt([0,y]),pt([13,y])],fill='#eee');dr.text(pt([0,y]),str(y),font=font,fill='#aaa')
 for r in I:
  n=r['name']
  if not (n.startswith(('PARTITIONS','FACADE','KZ','DOOR','STAIR'))):continue
  d=np.load(B/'02_Data'/r['file']);v=d['vertices'];f=d['faces']
  z=level+.8
  if v[:,2].min()>z or v[:,2].max()<z:continue
  seg=[]
  for t in v[f]:
   ps=[]
   for a,b in zip(t,np.roll(t,-1,axis=0)):
    if (a[2]-z)*(b[2]-z)<0:ps.append(a+(b-a)*((z-a[2])/(b[2]-a[2])))
   if len(ps)==2:seg.append(np.array(ps)[:,:2])
  col='#b5321d' if n.startswith('DOOR') else '#aaa' if n.startswith('STAIR') else '#444'
  for a,b in seg:dr.line([pt(a),pt(b)],fill=col,width=2)
  if n.startswith('DOOR'):
   if '__LEAF' not in n:continue
   p=np.mean([v.min(0),v.max(0)],0);dr.text(pt(p),n.replace('DOOR_','').split('__')[0],font=font,fill=col)
 dr.text((fi*750+300,15),label+' native z='+str(z),font=font,fill='black')
im.save(Path(__file__).parent/'House_Plans.png')
