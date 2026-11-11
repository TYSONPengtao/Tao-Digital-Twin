from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
W=Path(__file__).parent;D=W/'v24_34';p=np.load(D/'Roam_Ground_Grid.npz')['p'];fig,ax=plt.subplots(figsize=(13,13));ax.imshow(plt.imread('E:/jz/JIA/Rebuild_V24_34/Reports/V24_34_Expanded_Top.png'),extent=[7-79,7+79,-9-79,-9+79]);sc=ax.scatter(p[:,0],p[:,1],c=p[:,2],s=5,cmap='turbo',vmin=-16,vmax=15,alpha=.8);fig.colorbar(sc,ax=ax)
for xy in [(-25,9),(-24,-7),(-10,-20),(26,-19),(45,-25),(27,-29),(5,-38),(-22,-47),(-44,-47)]:ax.annotate(str(xy),xy,fontsize=9,color='red');ax.plot(*xy,'rx')
ax.set_aspect('equal');ax.set_xlim(-65,70);ax.set_ylim(-77,55);ax.set_xticks(range(-60,71,10));ax.set_yticks(range(-70,56,10));ax.grid();fig.savefig(D/'Route_Support_Map.png',dpi=160)
