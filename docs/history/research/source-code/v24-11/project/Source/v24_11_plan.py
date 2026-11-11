import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W/'v8_interior/plotlibs'),str(W)]
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle,Circle
from matplotlib.font_manager import FontProperties
from v24_11_geometry import POSTS,south_edge,north_boundary
font=FontProperties(fname='C:/Windows/Fonts/msyh.ttc');plt.rcParams['font.family']=font.get_name();plt.rcParams['axes.unicode_minus']=False
D=W/'v24_11';R=Path('E:/jz/JIA/Rebuild_V24_11/Reports');proof=json.loads((R/'V24_11_Corrections.json').read_text(encoding='utf8'));plot=json.loads((W/'v24_10/AsBuilt_Plan.json').read_text())['outline'];p=np.array(plot)
fig,ax=plt.subplots(figsize=(12,8.5),facecolor='#faf9f5');ax.set_facecolor('#faf9f5');ax.add_patch(Polygon(p,closed=True,facecolor='#e8e6dd',edgecolor='#76786d',lw=1.5,label='原始场景拟合地基轮廓'))
cx=np.linspace(13.20,18.65,100);cy=np.array([north_boundary(x)for x in cx]);ax.fill_between(cx,cy-.285,cy,color='#535e65',alpha=.9,label='随地基转弧的后墙')
# Room front remains set back within the eave, with the entry at the west end.
ax.plot([13.50,18.53],[-14.85,-14.85],color='#9b764e',lw=7,label='木门窗立面')
ax.plot([13.40,13.40],[-14.79,-9.3],color='#757d82',lw=8,label='入口侧山墙')
fy=lambda x:-16.6828994751+.10589*(x-13.0393619537)
rx=np.array([13.55,18.65]);ax.plot(rx,[fy(x)+.075 for x in rx],color='#9b9a8e',lw=5,label='石围栏')
post=np.array(POSTS);ax.plot(post[:,0],post[:,1],'--',color='#d85b40',lw=2.2,label='两柱连线：与围栏斜交')
for i,(x,y)in enumerate(post):
 ax.add_patch(Rectangle((x-.175,y-.175),.35,.35,color='#bcbbb0',zorder=7));ax.add_patch(Circle((x,y),.106,color='#7a4f2c',zorder=8));ax.annotate('柱1：在山墙后'if i==0 else'柱2：廊端',xy=(x,y),xytext=(x-.3 if i==0 else x+.4,y+.6 if i==0 else y+.55),fontsize=11,arrowprops={'arrowstyle':'-','color':'#7a4f2c'},ha='left')
ax.annotate('入口一端较宽',xy=(13.90,-15.60),xytext=(14.5,-15.7),fontsize=12,color='#a13f2f',arrowprops={'arrowstyle':'->','color':'#a13f2f'})
ax.add_patch(Rectangle((11.72,-16.94),1.48,.44,facecolor='#8e9799',edgecolor='#677176',lw=1.5,zorder=5))
ax.annotate('次照壁端部在瓦檐之下',xy=(13.08,-16.70),xytext=(11.5,-17.65),fontsize=11,arrowprops={'arrowstyle':'->','color':'#59646c'})
ex=np.linspace(13.3,18.73,80);exx=ex-.48*np.maximum(0,1-(ex-13.3)/2)**2;ey=np.array([south_edge(x)for x in ex]);ax.plot(exx,ey,color='#438d9a',lw=2.2,label='调整后的前瓦檐')
ax.text(16.0,-12.8,'储藏房',fontsize=22,ha='center',color='#5e6464');ax.text(16.3,-15.2,'檐廊',fontsize=13,ha='center',color='#956842');ax.text(19.7,-13.4,'外侧储藏区\n原薄铁皮棚保留',fontsize=11,ha='center',color='#666b69')
ax.set_xlim(11.1,21.35);ax.set_ylim(-18.1,-8.2);ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_xlabel('模型局部 X（米）');ax.set_ylabel('模型局部 Y（米）');ax.legend(loc='upper right',fontsize=9,framealpha=.95);ax.set_title('V24.11 储藏房入口、两柱斜廊与后墙关系',fontsize=17,pad=18);fig.text(.09,.035,'柱身均竖直；红虚线仅表示平面连线。依据实景模型、视频和用户标记拟合。',fontsize=10,color='#6d716a');fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(R/'V24_11_Veranda_and_Rear_Wall_Plan.png',dpi=170);plt.close(fig)
