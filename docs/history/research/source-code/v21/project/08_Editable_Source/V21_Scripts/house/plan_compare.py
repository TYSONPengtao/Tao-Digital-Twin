exec(open('work/v21_house/qa.py',encoding='utf-8-sig').read().split('report={')[0])
from PIL import Image,ImageDraw,ImageFont
im=Image.new('RGB',(1800,1080),'white');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
for pi in [0,1]:
 def xy(q):return (40+900*pi+(q[0]-2.8)*100,930-(q[1]-5.5)*170)
 for x in [3,4,5,6,7,8,9,10,11]:
  dr.line([xy([x,5.5]),xy([x,10.1])],fill='#eee');dr.text(xy([x,5.35]),str(x),font=small,fill='#999')
 for y in [6,7,8,9,10]:
  dr.line([xy([2.8,y]),xy([10.9,y])],fill='#eee');dr.text(xy([2.75,y]),str(y),font=small,fill='#999')
 for n,e in E.items():
  if not n.startswith(('PARTITIONS','DOOR','KZ_','STAIR','HOUSE_V20_F1')):continue
  if pi and n in REM:continue
  if pi and n in QE:
   ee=QE[n];pol=[]
   for p in ex.expand_parts(ee):
    v,f=ex.world_part(p,ee);pol.extend(v[triangles(v,f)])
   t=np.array(pol)
  elif n in ii:
   dd=np.load(B/'02_Data'/ii[n]['file']);t=dd['vertices'][dd['faces']]
  else:continue
  color='#454545' if not n.startswith('DOOR') else '#945740'
  for tr in t:
   ps=[]
   for a,b in zip(tr,np.roll(tr,-1,axis=0)):
    if (a[2]-8.3)*(b[2]-8.3)<0:ps.append(a+(b-a)*((8.3-a[2])/(b[2]-a[2])))
   if len(ps)==2 and np.all(np.asarray(ps)[:,0]>2.8) and np.all(np.asarray(ps)[:,0]<10.9) and np.all(np.asarray(ps)[:,1]>5.5):dr.line([xy(q) for q in ps],fill=color,width=3)
 dr.text((40+pi*900,30),'V20 原位置' if not pi else 'V21 按实景修正',font=font,fill='#222')
 if pi:
  dr.line([xy([9.1,7.6]),xy([9.1,8.4])],fill='#cc4139',width=8)
  dr.rectangle([xy([8.86,7.04]),xy([9.35,6.16])],outline='#138262',width=4)
  dr.text((1100,940),'红：旧洞封实    绿：卧室门改至柱南侧内开',font=small,fill='#333')
  dr.text((1100,978),'西侧檐廊保留 900 mm 白色无门洞',font=small,fill='#333')
 else:dr.text((130,940),'原错误卧室门在柱北侧，正对卫生间',font=small,fill='#333')
dr.text((40,1028),'依据：用户 150915 标注 + 原始 INSV 160 / 165 / 265 秒；尺寸沿用现有模型，未实测。',font=small,fill='#555')
im.save(D/'F3_Door_Position_Comparison.png')

