import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs'),str(W/'geomlibs'),str(W/'v8_interior/plotlibs')]
import numpy as np
from shapely.geometry import MultiPoint,Polygon,box
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family']='Microsoft YaHei';plt.rcParams['axes.unicode_minus']=False
D=W/'v24_10';ss=np.array(json.loads((D/'AsBuilt_Section_Segments.json').read_text())['-0.8']).reshape(-1,2)
q=ss[(ss[:,0]>=13.03)&(ss[:,0]<22)&(ss[:,1]<-8.8)]
# West edge is an internal join into the retained kitchen footing, not a cadastral boundary.
q=np.vstack([q,[13.039361953735352,-8.80]])
poly=MultiPoint(q).convex_hull.simplify(.035,preserve_topology=True)
old=Polygon([[13.21,-17.04],[20.26,-17.04],[21.437,-15.185],[21.59,-13.0],[21.09,-10.20],[18.92,-9.56],[13.21,-9.56]])
pts=list(poly.exterior.coords)[:-1]
out={'source':'E:/jz/实景三维场景模型.3dm','source_section_z_m':-.8,'method':'Outer retaining wall section contour; 35 mm simplification of convex regularization; not a cadastral or independent survey','outline':pts,'area_m2':poly.area,'old_local_storage_plinth_approx_area_m2':old.area,'area_reduction_m2':old.area-poly.area,'max_x':poly.bounds[2],'bounds':list(poly.bounds)}
(D/'AsBuilt_Plan.json').write_text(json.dumps(out,indent=2),encoding='utf8')
fig,ax=plt.subplots(figsize=(9,10));ax.scatter(q[:,0],q[:,1],s=4,c='black',label='原实景3dm挡墙截线点');ox,oy=old.exterior.xy;ax.plot(ox,oy,c='#c73a24',lw=1.6,label='上一版局部近似外轮廓');px,py=poly.exterior.xy;ax.plot(px,py,c='#087e71',lw=2,label='按实景修正后的外轮廓');ax.set_aspect('equal');ax.set(xlim=(12,23),ylim=(-18.5,-7.5),xlabel='局部 X（米）',ylabel='局部 Y（米）',title='储藏房局部占地轮廓核对');ax.grid(alpha=.2);ax.legend(loc='upper right');fig.tight_layout(rect=(0,.035,1,1));fig.text(.08,.015,'依据原实景模型 Z=-0.80m 截线；西侧为与保留厨房基础的内部接缝。',fontsize=10,color='#444444');fig.savefig(D/'Plot_Boundary_Comparison.png',dpi=150)
print(json.dumps(out),flush=True)
