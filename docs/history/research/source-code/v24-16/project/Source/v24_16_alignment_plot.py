import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W/'v8_interior/plotlibs')]
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.font_manager import fontManager
fontManager.addfont('C:/Windows/Fonts/msyh.ttc');plt.rcParams['font.family']='Microsoft YaHei';plt.rcParams['axes.unicode_minus']=False
D=W/'v24_16';R=Path('E:/jz/JIA/Rebuild_V24_16/Reports');src={r['name']:r for r in json.loads((D/'Inventory.json').read_text())};saved=json.loads((D/'Solid_Export_Index.json').read_text());dst={r['name']:r for r in saved['objects']}
def data(n,old=False):return np.load(D/(src[n]['file']if old else dst[n]['file']))
def section(d,x):
 t=d['v'][d['f']];q=t[:,:,0]-x;sel=(q.min(1)<-1e-7)&(q.max(1)>1e-7);out=[]
 for tri,dd in zip(t[sel],q[sel]):
  p=[]
  for a,b in [(0,1),(1,2),(2,0)]:
   if dd[a]*dd[b]<0:p.append((tri[a]+(tri[b]-tri[a])*(-dd[a]/(dd[b]-dd[a])))[1:])
  if len(p)==2:out.append(p)
 return np.array(out)
wall='SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry';roof='SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL_Geometry';corn='SITE_SOUTH_SCREENWALL_V12_STEPPED_MASONRY_UNDEREAVE_Geometry';foot='V24_11_Screenwall_Continuous_Stepped_Stone_Plinth';proof=json.loads((R/'V24_16_Corrections.json').read_text());trace=np.array(proof['screen']['centerline_xy'])
fig,axs=plt.subplots(2,3,figsize=(13,8),gridspec_kw={'height_ratios':[4,1.25]},layout='constrained')
for k,x in enumerate([3.5,7.,10.5]):
 cy=float(np.interp(x,trace[:,0],trace[:,1]))
 for ax in axs[:,k]:
  ax.axvline(cy,color='#077869',ls='--',lw=1.5);ax.set_xlim(cy-1.05,cy+1.05);ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('横向坐标 Y（米）')
 ax=axs[0,k]
 for n,old,color,ls,lw in [(wall,False,'#454545','-',1.8),(corn,False,'#956d32','-',1.4),(roof,True,'#c04c4c','--',1.1),(roof,False,'#2062ac','-',1.8)]:ax.add_collection(LineCollection(section(data(n,old),x),colors=color,linestyles=ls,linewidths=lw))
 ax.set_ylim(2.75,4.9);ax.set_title(f'照壁截面 X = {x:.1f} m')
 ax=axs[1,k];ax.add_collection(LineCollection(section(data(wall),x),colors='#454545',linewidths=1.8));ax.add_collection(LineCollection(section(data(foot),x),colors='#956d32',linewidths=1.6));ax.set_ylim(-.8,-.10)
axs[0,0].set_ylabel('高程 Z（米）');axs[1,0].set_ylabel('底座')
from matplotlib.lines import Line2D
fig.legend([Line2D([],[],color=c,ls=s,lw=1.7)for c,s in [('#c04c4c','--'),('#2062ac','-'),('#956d32','-'),('#454545','-'),('#077869','--')]],['原屋顶','V24.16 屋顶','承托 / 底座','保留墙身','原墙身中线'],loc='outside lower center',ncol=5,frameon=False)
fig.suptitle('照壁中线核对：屋顶、连续承托与底座跟随墙身',fontsize=16)
path=R/'V24_16_Screenwall_Alignment_Sections.png';fig.savefig(path,dpi=155);plt.close(fig)
(R/'V24_16_Alignment_Diagram_State.json').write_text(json.dumps({'model_sha256':saved['model_sha256'],'file':path.name,'x_sections':[3.5,7.,10.5],'meaning':'Actual saved mesh sections; geometric bearing alignment, not an engineering structural calculation.'},indent=2));print(path)
