from pathlib import Path
import json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).parent;D=W/'v24_36';p=np.load(D/'Roam_Ground_Grid.npz')['p'];proj=json.loads((D/'Top_Projection.json').read_text());x,y=proj['center'][:2];width=proj['width_m'];height=width*2/3;im=plt.imread('E:/jz/JIA/Rebuild_V24_36/Reports/V24_36_Context_Top.png');fig,ax=plt.subplots(figsize=(9,12));ax.imshow(im,extent=[x-width/2,x+width/2,y-height/2,y+height/2]);sel=(p[:,0]>-110)&(p[:,0]<10)&(p[:,1]>-10)&(p[:,1]<170);q=p[sel];ax.scatter(q[:,0],q[:,1],c=q[:,2],s=2,cmap='turbo',vmin=-10,vmax=12,alpha=.5)
for xy in [(-25,9),(-40,20),(-58,35),(-66,52),(-80,100),(-88,135),(-120,147),(-157,141)]:
 print('GOAL',xy,p[(p[:,0]==xy[0])&(p[:,1]==xy[1])].tolist());ax.plot(*xy,'rx');ax.annotate(str(xy),xy,fontsize=9,color='red')
ax.set_xlim(-110,10);ax.set_ylim(-10,170);ax.set_aspect('equal');ax.set_xticks(range(-110,11,10));ax.set_yticks(range(-10,171,10));ax.grid();fig.savefig(D/'Route_Local_Debug.png',dpi=150)
