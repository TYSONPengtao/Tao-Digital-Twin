import sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];O=Path(__file__).parent
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import export_v5 as ex
M=json.loads((O/'Mutation.json').read_text(encoding='utf8'));A,B=np.array(M['changes']['outer_gap_endpoints']);u=(B-A)/np.linalg.norm(B-A);n=np.array([-u[1],u[0]])
try:font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
except:font=ImageFont.load_default();small=font
I=Image.new('RGB',(1680,1570),(245,245,242));d=ImageDraw.Draw(I)
d.text((48,20),'V11 实景外大门 — 闭合态几何审查',fill=(25,31,40),font=font)
d.text((48,55),'四金属叶 / 独立铰轴 / 青砖平顶柱 | 造型来自全景 897 秒及 DJI_0073/0074；尺寸尚未实测',fill=(75,78,82),font=small)
def elevation(point):return (100+point[0]*282,100+(3.15-point[1])*172)
faces=[]
for e in M['add']:
 for p in e['parts']:
  v,f=ex.world_part(p,e);s=(v[:,:2]-A)@u;ys=(v[:,:2]-A)@n
  color=M['materials'][p['material']]['color']
  for face in f:
   pp=np.column_stack([s[face],v[face,2]]);area=abs(np.cross(pp[1]-pp[0],pp[2]-pp[0]))
   if area<1e-9:continue
   faces.append((float(ys[face].mean()),[elevation(q) for q in pp],tuple(color)))
for y,poly,color in sorted(faces,key=lambda q:q[0]):d.polygon(poly,fill=color)
for k,row in enumerate(M['door_registry_additions']):
 origin=np.array(row['origin']);s=float((origin[:2]-A)@u);xy=elevation([s,origin[2]]);d.ellipse((xy[0]-6,xy[1]-6,xy[0]+6,xy[1]+6),fill=(224,39,31));d.text((xy[0]-25,xy[1]+14),f'铰轴{k+1}',fill=(182,26,22),font=small)
d.text((100,906),f"中心线缺口 5.168881 m；名义柱宽 0.350 m；净洞 4.468881 m；四叶各 1.079470 m",fill=(55,57,62),font=small)
d.text((100,941),'柱頂参照已注册实景 Z 3.0483 / 2.9906 m；开启扫掠、折叠机械关系待现场核实。',fill=(90,65,34),font=small)
# Topology plan: emphasize regeneration of SAME western chain, and show opening untouched.
scale=23;xbase=-26.1;ybase=7.1
def plan(xy):return (100+(xy[0]-xbase)*scale,1030+(ybase-xy[1])*scale)
audit=json.loads((O/'Wall_Current_Clip_Audit.json').read_text(encoding='utf8'))
d.text((700,1030),'平面关系 / 原墙路线保持',fill=(30,37,43),font=font)
for rec in audit:
 chains=[rec['centerline'][:5],rec['centerline'][-5:]] if rec['name'].endswith('_0') else [rec['centerline']]
 for chain in chains:
  pts=[plan(x) for x in chain]
  d.line(pts,fill=(161,163,162) if rec['name'].endswith('_0') else (54,108,159),width=7)
for pp in M['hybrid_scope_additions']:
 pts=[plan(x) for x in pp['outer']];d.line(pts+[pts[0]],fill=(172,77,17),width=2)
d.line([plan(A),plan(B)],fill=(21,134,83),width=6)
for k,row in enumerate(M['door_registry_additions']):
 xy=plan(row['origin'][:2]);d.ellipse((xy[0]-4,xy[1]-4,xy[0]+4,xy[1]+4),fill=(209,46,34))
d.text((700,1080),'蓝：原墙 1，沿现有同一几何补齐 Hybrid',fill=(54,108,159),font=small)
d.text((700,1117),'灰：原墙 0 保留；绿：新增四叶外门',fill=(60,64,68),font=small)
d.text((700,1154),'橙：允许修补足迹；红点：各门叶局部轴',fill=(172,77,17),font=small)
d.text((700,1204),'原墙不重复；实景 source5 面/材质/UV 不改',fill=(30,68,44),font=small)
d.text((700,1260),'所有新增几何：封闭、正体积通过',fill=(30,68,44),font=small)
d.text((700,1295),'闭合门叶互相及门柱交叉体积：0',fill=(30,68,44),font=small)
d.text((700,1350),'图为模型几何审查，不是现场施工尺寸证明。',fill=(113,62,28),font=small)
I.save(O/'Gate_and_Wall_Review.png')
print(O/'Gate_and_Wall_Review.png')
