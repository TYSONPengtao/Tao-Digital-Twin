import sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['geomlibs','np1','libs']]
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely.affinity import rotate,translate
from PIL import Image,ImageDraw,ImageFont
from check_v5_layout import volume_parts,polys_at,world
O=Path(__file__).parent;A=json.loads(Path(r'E:\jz\JIA\Rebuild_V4\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'));B=json.loads(Path(r'E:\jz\JIA\Rebuild_V5\05_Intermediate\Architecture_Scene.json').read_text(encoding='utf-8'))
fonts={k:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',v) for k,v in [('title',38),('normal',24),('small',20),('tag',23)]}
COLORS={'wall':(83,93,109),'add':(92,175,104),'remove':(240,193,190),'door':(194,98,56),'old_door':(116,153,190),'grid':(220,226,231)}
imgs=[]
for f,z in enumerate(A['levels'][:3],1):
 I=Image.new('RGB',(3200,1600),'white');D=ImageDraw.Draw(I)
 D.text((90,22),f'{f}层门位与布局优化对照  |  V4 → V5',font=fonts['title'],fill=(35,45,60));D.text((90,80),'视频支持空间连接与相对门位；坐标、尺寸和房间轮廓暂沿图纸网格估计，仍需现场量尺。',font=fonts['normal'],fill=(100,55,30))
 ea={e['name']:e for e in A['elements']};eb={e['name']:e for e in B['elements']}
 pa=volume_parts(ea[f'PARTITIONS_JOINED_F{f}']);pb=volume_parts(eb[f'PARTITIONS_JOINED_F{f}']);old=polys_at(pa,z+1.2);new=polys_at(pb,z+1.2);added=new.difference(old);removed=old.difference(new)
 doorsA=[]
 for e in A['elements']:
  if e['layer']=='30_DOOR' and abs(e['origin'][2]-z)<.01:
   d=A['definitions'][e['definition']]['parameters'];doorsA.append(dict(door_id=e['name'],origin=e['origin'],angle=e.get('angle',0),width=d['Width']))
 doorsB=[dict(door_id=r['previous_id'],new_id=r['door_id'],origin=r['origin'],angle=r['angle'],width=r['nominal_opening_width_m']) for r in B['door_registry'] if r['floor']==f]
 order=[r['door_id'] for r in doorsA];lookupA={r['door_id']:r for r in doorsA};lookupB={r['door_id']:r for r in doorsB}
 for col,(S,ds,label) in enumerate([(A,doorsA,'V4 原图纸推定平面'),(B,doorsB,'V5 视频支持的逐层修订')]):
  left=140+col*1570;bottom=1310;scale=96.
  def pix(q):return (left+q[0]*scale,bottom-q[1]*scale)
  def drawpoly(P,color,outline=None):
   parts=list(P.geoms) if hasattr(P,'geoms') else [P]
   for p in parts:
    if p.geom_type!='Polygon':continue
    D.polygon([pix(q) for q in p.exterior.coords],fill=color,outline=outline)
    for r in p.interiors:D.polygon([pix(q) for q in r.coords],fill='white')
  D.text((left,143),label,font=fonts['title'],fill=(35,45,60))
  for x in S['grid_x']:
   D.line([pix((x,-.2)),pix((x,10.7))],fill=COLORS['grid'],width=2);D.text((pix((x,0))[0]-35,1335),f'X={x:g}',font=fonts['small'],fill=(80,88,97))
  for y in S['grid_y']:
   D.line([pix((-.3,y)),pix((13.4,y))],fill=COLORS['grid'],width=2);D.text((left-100,pix((0,y))[1]-14),f'Y={y:g}',font=fonts['small'],fill=(80,88,97))
  for e in S['elements']:
   if e['layer'] in ['10_WALL_EXT','11_WALL_INT','20_COLUMN']:
    try:
     for P,a,b in volume_parts(e):
      if a<z+1.2<b:drawpoly(P,COLORS['wall'] if e['layer']!='20_COLUMN' else (45,50,60))
    except ValueError:pass
  # Fixed window frames/glazing show the actual perimeter at this cut height.
  for e in S['elements']:
   if e['layer']!='31_WINDOW' or 'definition' not in e:continue
   q=dict(e);q['parts']=S['definitions'][e['definition']]['parts']
   try:
    for P,a,b in volume_parts(q):
     if a<z+1.2<b:drawpoly(P,(126,174,197))
   except ValueError:pass
  if col==1:
   drawpoly(added,COLORS['add']);drawpoly(removed,COLORS['remove'])
   # Show old door positions as thin dashed lines in the updated panel.
   for name in order:
    a=lookupA[name];b=lookupB[name]
    if a['origin']!=b['origin'] or a['angle']!=b['angle']:
     x,y=a['origin'][:2];ang=a['angle'];p0=pix((x,y));p1=pix((x+math.cos(ang)*a['width'],y+math.sin(ang)*a['width']))
     for k in range(0,12,2):D.line([(p0[0]+(p1[0]-p0[0])*k/12,p0[1]+(p1[1]-p0[1])*k/12),(p0[0]+(p1[0]-p0[0])*(k+1)/12,p0[1]+(p1[1]-p0[1])*(k+1)/12)],fill=COLORS['old_door'],width=5)
  for r in ds:
   P=world(box(0,-.03,r['width'],.03),r);drawpoly(P,COLORS['door']);C=P.centroid;xx,yy=pix((C.x,C.y));idx=order.index(r['door_id'])+1;D.ellipse((xx-20,yy-20,xx+20,yy+20),fill=(255,232,163),outline=(172,118,60),width=2);D.text((xx-7,yy-17),str(idx),font=fonts['tag'],fill=(40,40,40))
  if col==1:
   for rr in [r for r in S.get('rooms',[]) if r['floor']==f]:
    if rr['room_id']=='F1-R07':continue
    P=Polygon(rr['review_polygon_xy_m']);c=P.representative_point();xx,yy=pix((c.x,c.y));txt=rr['room_id']+'\n'+rr['label'];D.multiline_text((xx-75,yy-26),txt,font=fonts['small'],fill=(95,103,112),spacing=3)
 D.text((90,1410),'绿色=新增或补墙  粉色=移除隔墙  蓝虚线=旧门位  棕色=当前门；蓝色=窗框玻璃；仅画墙柱门窗，楼梯/栏杆/楼板省略。',font=fonts['normal'],fill=(65,75,90))
 for idx,id in enumerate(order,1):
  x=90+(idx-1)%3*1020;y=1460+(idx-1)//3*45;a=lookupA[id];b=lookupB[id];target=b.get('new_id',id);txt=f'{idx}. {target}：({a["origin"][0]:g},{a["origin"][1]:g}) → ({b["origin"][0]:g},{b["origin"][1]:g})';D.text((x,y),txt,font=fonts['small'],fill=(60,65,75))
 I.save(O/f'V5_F{f}_Before_After_Plan.png');imgs.append(I)
C=Image.new('RGB',(3200,4800),'white')
for i,I in enumerate(imgs):C.paste(I,(0,i*1600))
C.save(O/'V5_All_Floors_Before_After.jpg',quality=96)
print('Three floor comparison images written')
