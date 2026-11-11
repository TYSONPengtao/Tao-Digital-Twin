import json,numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle,Circle
W=Path(__file__).parent;D=W/'v24_20';R=Path('E:/jz/JIA/Rebuild_V24_20/Reports');font=FontProperties(fname='C:/Windows/Fonts/msyh.ttc');plt.rcParams['font.family']=font.get_name();plt.rcParams['axes.unicode_minus']=False
idx={r['name']:r for r in json.loads((D/'Inventory.json').read_text())};ss=json.loads((D/'Solid_Export_Index.json').read_text());saved={r['name']:r for r in ss['objects']};h=ss['model_sha256'];prep=json.loads((D/'Prepared_Geometry.json').read_text(encoding='utf8'));qa=json.loads((R/'V24_20_Fresh_Native_QA.json').read_text(encoding='utf8'))
def load(n):return np.load(D/(saved[n]['file']if n in saved else idx[n]['file']))
def section(d,z):
 seg=[]
 for t in d['v'][d['f']]:
  pp=[]
  for a,b in zip(t,np.roll(t,-1,axis=0)):
   if(a[2]-z)*(b[2]-z)<0:pp.append(a+(b-a)*(z-a[2])/(b[2]-a[2]))
  if len(pp)==2:seg.append(np.array(pp)[:,:2])
 return seg
def save(fig,name,method):
 fig.tight_layout();fig.savefig(R/(name+'.png'),dpi=170);(R/(name+'_State.json')).write_text(json.dumps({'model_sha256':h,'file':name+'.png','frame':40,'draft':False,'method':method},indent=2));plt.close(fig)
fig,ax=plt.subplots(figsize=(13,6));ax.add_patch(Rectangle((9.2,7.4),1.4,2.35,facecolor='#e2f1ef',edgecolor='none'));ax.add_patch(Rectangle((10.7,7.4),2.09,2.35,facecolor='#e8effa',edgecolor='none'))
for n in ['FACADE_CONTINUOUS_F1_Geometry','PARTITIONS_JOINED_F1_Geometry','HOUSE_V20_F1_PHOTO_MISSING_INFILL_WALLS_Geometry']:
 ax.add_collection(LineCollection(section(load(n),1),colors='#283944',linewidths=2))
for n in ['DOOR_BATH_F1_L__FRAME_Geometry','DOOR_BATH_F1_R__FRAME_Geometry','DOOR_KITCHEN_F1__FRAME_Geometry']:
 d=load(n);v=d['v'].copy()
 if 'F1_R'in n:v[:,0]-=1.2
 ax.add_collection(LineCollection(section({'v':v,'f':d['f']},1),colors='#a9402c',linewidths=3))
ax.add_patch(Rectangle((10.7,7.25),.8,.10,facecolor='#a9402c',edgecolor='none'));ax.annotate('右侧卫生间新门位\n沿原墙面左移',xy=(11.1,7.3),xytext=(11.25,6.7),arrowprops={'arrowstyle':'->','color':'#a9402c'},ha='center',fontsize=11,color='#a9402c')
ax.add_patch(Rectangle((9.05,8.6),.10,.8,facecolor='#a9402c',edgecolor='none'));ax.annotate('楼梯对面原门保留',xy=(9.1,9.0),xytext=(7.2,9.9),arrowprops={'arrowstyle':'->','color':'#a9402c'},fontsize=11,color='#a9402c')
ax.add_patch(Rectangle((10.6,7.395),.10,2.43,facecolor='#087bd1',edgecolor='none',alpha=.82));ax.annotate('按蓝线新增隔墙',xy=(10.65,9.05),xytext=(11.55,10.05),arrowprops={'arrowstyle':'->','color':'#087bd1'},fontsize=11,color='#087bd1')
ax.text(9.86,8.25,'楼梯口卫生间',ha='center',fontsize=10,color='#227a70');ax.text(11.65,8.55,'右侧分区',ha='center',fontsize=12,color='#32658f');ax.text(8.25,8.15,'楼梯口\n通道保留',ha='center',fontsize=11)
ax.set(xlim=(3.5,13.5),ylim=(6.35,10.25),aspect='equal',xlabel='X / 米',ylabel='Y / 米',title='首层楼梯口与卫生间平面（Z=1米剖切）');ax.grid(alpha=.14);save(fig,'V24_20_F1_Plan','Saved wall meshes cross-section; door frame position checked by fresh native QA. Plan is not a measured survey.')
fig,ax=plt.subplots(figsize=(8,11));n='SITE_KITCHEN_STONE_FLOOR_Geometry';d=load(n)
for t in d['v'][d['f']]:
 if abs(np.cross(t[1]-t[0],t[2]-t[0])[2])>1e-8:ax.fill(t[:,0],t[:,1],color='#e1e8ea',linewidth=0)
ax.add_collection(LineCollection(section(load('SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry'),1),colors='#717c82',linewidths=5))
for row in qa['post_floor_contacts']:
 x,y=row['xy'];ax.add_patch(Circle((x,y),.118,facecolor='#976132',edgecolor='#684020',zorder=5))
ax.text(10.6,-6.7,'厨房室内',ha='center',fontsize=16);ax.annotate('柱列沿外墙内侧转折\n柱脚与地板接触',xy=(13.45,-5.94),xytext=(10.6,-4.2),arrowprops={'arrowstyle':'->','color':'#976132'},fontsize=12,color='#976132');ax.annotate('原墙脚缺口已补齐',xy=(13.7,-5),xytext=(14.45,-6.8),arrowprops={'arrowstyle':'->'},rotation=90,ha='center',fontsize=10)
ax.set(xlim=(8.7,14.8),ylim=(-12.1,-2.4),aspect='equal',xlabel='X / 米',ylabel='Y / 米',title='厨房柱位与连续地面平面');ax.grid(alpha=.14);save(fig,'V24_20_Kitchen_Plan','Saved floor and wall mesh, with verified native column-foot coordinates from QA; photo-fitted positions.')
print('V20_PLANS_SAVED',h,flush=True)
