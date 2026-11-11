import sys,json,math
from pathlib import Path
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs','v4_audit_junction']]+[str(Path(__file__).parent)]
sys.path.insert(0,str(Path(__file__).parent/'plotlibs'))
sys.path.insert(0,str(W))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PPoly,Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib import font_manager
import mutation as M
import v2_geometry as G
def data(g):
 if g['type']=='prism':
  q=np.array(g['profile']);n=len(q);v=np.vstack([q,q+np.array(g['vector'])]);f=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
  return v,f
 if g['type']=='box':
  x,y,z=g['origin'];a,b,c=g['size'];v=np.array([[x,y,z],[x+a,y,z],[x+a,y+b,z],[x,y+b,z],[x,y,z+c],[x+a,y,z+c],[x+a,y+b,z+c],[x,y+b,z+c]])
  return v,[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
 v,f,_,_=G.data(g);return v,f
S=json.loads((M.OUT/'Interior_Review_Scene.json').read_text(encoding='utf8'));E={e['name']:e for e in S['elements']}
fp=Path(r'C:\Windows\Fonts\msyh.ttc')
if fp.exists():font_manager.fontManager.addfont(str(fp));plt.rcParams['font.family']=font_manager.FontProperties(fname=str(fp)).get_name()
fig,axes=plt.subplots(1,2,figsize=(15,7),layout='constrained')
for ax,f,z in zip(axes,[1,2],[1,4.9]):
 q=M.xy_at(E[f'PARTITIONS_JOINED_F{f}'],z)
 for poly in M.J._polys(q):
  ax.add_patch(PPoly(np.asarray(poly.exterior.coords),fc='#6a6f6c',ec='#343938',lw=.6))
  for hole in poly.interiors:ax.add_patch(PPoly(np.asarray(hole.coords),fc='white',ec='#343938',lw=.6))
 ax.add_patch(Rectangle((3.9,7.4),1.3,2.3,fc='#d4dae0',ec='#4d5961',alpha=.6))
 for fn,col in [(1,'#cfa574'),(2,'#9eb6cb')]:
  ax.add_patch(Rectangle((5.2,8.56 if fn==1 else 7.44),2.6,1.1,fc=col,ec='#50443e',alpha=.75))
  for i in range(11):ax.plot([5.2+i*.26]*2,[8.56,9.66] if fn==1 else [7.44,8.54],c='#50443e',lw=.55)
 ax.annotate('上行第一跑\n右墙、左扶手',xy=(5.35,9.1),xytext=(7.4,9.1),ha='center',va='center',fontsize=8,arrowprops=dict(arrowstyle='->',lw=1.5))
 ax.annotate('第二跑',xy=(7.65,7.98),xytext=(5.6,7.98),ha='center',va='center',fontsize=8,arrowprops=dict(arrowstyle='->',lw=1.5))
 if f==1:
  ax.plot([7.8,7.8],[8.6,9.4],ls='--',c='#777777',lw=2)
  ax.annotate('旧门位置：已清除\n现在为无门梯口',xy=(7.8,9.0),xytext=(6.8,6.6),fontsize=8,ha='center',arrowprops=dict(arrowstyle='->',lw=1.1,color='#777777'))
  ax.annotate('新门 X9.1/Y8.6\n对面墙候选，偏距待量尺',xy=(9.1,9.0),xytext=(10.1,6.3),fontsize=8,ha='center',c='#92382e',arrowprops=dict(arrowstyle='->',lw=1.1,color='#92382e'))
 for r in S['door_registry']:
  if r['floor']!=f or r.get('nominal_opening_width_m',0)>2:continue
  x,y,_=r['origin'];a=r['angle'];w=r['nominal_opening_width_m'];ax.plot([x,x+w*math.cos(a)],[y,y+w*math.sin(a)],c='#b54339',lw=3)
  if r['door_id'] in ['DOOR_BATH_F1_R','DOOR_KITCHEN_F1','DOOR_BATH_F2_R']:
   if r['door_id']!='DOOR_KITCHEN_F1':ax.annotate('一层右卫（原图）' if f==1 else '右卫侧门（镜像左侧）',xy=(x,y),xytext=(x-.05,y-.6),fontsize=7,c='#92382e',ha='right')
 ax.set(xlim=(-.3,13.3),ylim=(.9,10.0),aspect='equal',title=f'V8 {f}层内墙：实际几何 1m 高水平切片',xlabel='设计坐标 X / m',ylabel='设计坐标 Y / m')
 ax.grid(alpha=.15)
fig.suptitle('门位与楼梯方向复核；尺寸沿用图纸/候选，未经实地量尺',fontsize=14)
fig.savefig(M.OUT/'V8_Interior_Plan_Review.png',dpi=145);plt.close(fig)

fig,ax=plt.subplots(figsize=(11,7),layout='constrained')
q=M.xy_at(E['PARTITIONS_JOINED_F1'],1)
for poly in M.J._polys(q):
 ax.add_patch(PPoly(np.asarray(poly.exterior.coords),fc='#737b76',ec='#343938',lw=.6))
 for hole in poly.interiors:ax.add_patch(PPoly(np.asarray(hole.coords),fc='white',ec='#343938',lw=.6))
ax.add_patch(Rectangle((3.9,7.4),1.3,2.3,fc='#e7ebed',ec='#819197'))
for yy,col in [(8.56,'#dec19b'),(7.44,'#bfd5e2')]:
 ax.add_patch(Rectangle((5.2,yy),2.6,1.1,fc=col,ec='#819197'))
 for i in range(11):ax.plot([5.2+i*.26]*2,[yy,yy+1.1],color='#8a8278',lw=.7)
ax.annotate('第一跑上行：右侧实体墙',xy=(5.6,9.13),xytext=(7.25,9.13),ha='center',va='center',fontsize=10,arrowprops=dict(arrowstyle='->',color='#584936',lw=2))
ax.annotate('第二跑',xy=(7.5,7.98),xytext=(5.7,7.98),ha='center',va='center',fontsize=10,arrowprops=dict(arrowstyle='->',color='#4b758c',lw=2))
ax.plot([7.8]*2,[8.6,9.4],c='#999999',lw=3,ls='--')
ax.text(7.67,8.40,'旧门清除\n开放梯口',ha='right',va='top',fontsize=10,c='#555555')
ax.plot([9.1]*2,[8.6,9.4],c='#b54736',lw=5)
ax.add_patch(Rectangle((9.2,8.6),1.5,1,fc='#ecd6ce',ec='#b54736',lw=1,alpha=.4))
ax.text(9.95,9.10,'楼梯对面洗手间\n范围为候选',ha='center',va='center',c='#963e2d',fontsize=11)
ax.annotate('候选门 X9.1/Y8.6\n偏距、墙界待量尺',xy=(9.1,8.95),xytext=(9.8,7.65),ha='center',fontsize=10,c='#963e2d',arrowprops=dict(arrowstyle='->',color='#963e2d',lw=1.5))
ax.text(8.45,9.30,'开放过道',ha='center',c='#3b7565',fontsize=10)
ax.set(xlim=(3.75,11),ylim=(7.15,10),aspect='equal',xlabel='继承图纸坐标 X / m',ylabel='继承图纸坐标 Y / m',title='V8 楼梯口与卫生间门局部复核：几何水平切片')
ax.grid(alpha=.15)
fig.savefig(M.OUT/'V8_Stair_Door_Candidate_Top.png',dpi=155);plt.close(fig)

fig=plt.figure(figsize=(11,8));ax=fig.add_subplot(111,projection='3d')
for e in S['elements']:
 if e['name'] in ['STAIR_F1_FLIGHT1','STAIR_F1_FLIGHT2','STAIR_LANDING_F1','STAIR_V4_RAIL_F1_1','STAIR_V4_RAIL_F1_2','STAIR_V4_RETURN_F1']:
  for p in e['parts']:
   v,f=data(p['geometry']);faces=[np.asarray(v)[ff] for ff in f]
   ax.add_collection3d(Poly3DCollection(faces,facecolors='#994d32' if p['material']=='M_Wood' else '#cfd1cb',edgecolors='#6b6d68',linewidths=.3,alpha=.98))
# Context wall, upper floor receiving platform, and rear wall right of the
# ascending direction (arrow). Draw exact inherited design coordinates.
for g in [dict(type='box',origin=[3.9,9.7,0],size=[5.0,.2,3.77]),dict(type='box',origin=[7.8,7.3,3.77],size=[1.3,2.4,.13])]:
 v,f=data(g);ax.add_collection3d(Poly3DCollection([np.asarray(v)[ff] for ff in f],facecolors='#ccd9df',edgecolors='#809398',linewidths=.2,alpha=.14))
ax.quiver(7.65,9.1,.35,-1.8,0,1.25,color='#d65338',linewidth=2,arrow_length_ratio=.16)
ax.text(6.2,9.14,2.3,'第一跑：实体墙在右侧',fontsize=11,color='#9a3526')
ax.set(xlim=(3.85,9.15),ylim=(7.2,9.9),zlim=(-.2,4.9),xlabel='X / m',ylabel='Y / m',zlabel='Z / m',title='V8 实际楼梯几何与内侧扶手（首层）')
ax.set_box_aspect((5.3,2.7,5.1));ax.view_init(elev=27,azim=25)
fig.savefig(M.OUT/'V8_Stair_Geometry_Review.png',dpi=150,bbox_inches='tight')
print('Wrote two actual-geometry previews')
