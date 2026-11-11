from v26_2_common import *
from PIL import Image,ImageDraw,ImageFont
D=W/'v26_4';FD=D/'Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};O=Path('E:/jz/JIA/Rebuild_V26_4');R=O/'Reports'
im=Image.new('RGB',(1700,1000),'white');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',25);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21);title=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',33);s=155
def xy(p):return(70+(p[0]-3.35)*s,115+(10.4-p[1])*s)
dr.text((70,30),'V26.4 一楼楼梯与两个卫生间的实际模型剖切',font=title,fill='#182c3d')
for lo,hi,color in [((9.2,7.4),(10.6,9.68),'#e2f0eb'),((10.7,7.4),(12.88,9.68),'#e7eef8'),((9.22,4.9),(12.88,7.2),'#f8f0e8')]:dr.rectangle([xy([lo[0],hi[1]]),xy([hi[0],lo[1]])],fill=color)
for n,color,width in [('V26_3_House_Connected_Walls_And_Stairs','#253e4e',3),('DOOR_KITCHEN_F1__FRAME_Geometry','#a44332',6),('DOOR_BATH_F1_R__FRAME_Geometry','#a44332',6)]:
 a=np.load(FD/J[n]['file']);m=solid(a['v'],a['f'],n)
 for contour in m.slice(1.).to_polygons():
  pts=[xy(q)for q in contour];dr.line(pts+[pts[0]],fill=color,width=width)
for x,y,label in [(5.65,8.85,'楼梯间'),(9.36,8.14,'楼梯口卫生间'),(11.12,8.6,'右侧卫生间'),(10.9,6.35,'右侧房间')]:dr.text(xy([x,y]),label,font=font,fill='#254c65')
dr.text(xy([9.32,9.1]),'从楼梯口进入 →',font=small,fill='#a44332');dr.text(xy([10.79,7.07]),'↑ 从右侧房间进入',font=small,fill='#a44332');dr.text(xy([10.72,8.03]),'100 mm 隔墙',font=small,fill='#226b6b')
dr.rectangle((0,880,1700,1000),fill='white');dr.line((70,895,1630,895),fill='#d5dce1',width=1)
for x in range(4,14):dr.text((xy([x,5.2])[0],850),str(x),font=small,fill='#617787')
dr.text((70,905),'剖切高度 Z=1.00 m；坐标单位 m。普通墙段厚度不超过 240 mm，转角与原梁柱交接单独处理。',font=small,fill='#4b6270');dr.text((70,945),'轮廓来自重新打开的 V26.4 Blender 文件；楼梯轮廓为此高度的实际截面。',font=small,fill='#4b6270');im.save(R/'V26_4_F1_Room_Relationships.png')
print('SAVED_NATIVE_F1_PLAN',flush=True)
