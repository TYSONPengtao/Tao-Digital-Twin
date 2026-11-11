import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'v8_interior/plotlibs'),str(W/'libs')]
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
D=W/'v24_30';idx={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))}
def source(n):return np.load(D/idx[n]['file'])
fig,ax=plt.subplots(figsize=(14,10));ax.set_aspect('equal')
for n,col in [('SITE_V16_GRADED_INTERIOR_SOIL_Geometry','#d5caa4'),('SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','#555555'),('SITE_PERIMETER_JOINED_RETAINING_WALL_1_Geometry','#777777'),('SITE_V15_GATE_TO_INNER_GATE_CONTINUOUS_PAVEMENT_Geometry','#b5d5ea'),('SITE_V12_OUTER_GATE_SCORED_CONCRETE_RAMP_Geometry','#99bbdd'),('SITE_V12_REBUILT_COURT_0_-20_0_Geometry','#dddddd'),('SITE_V12_REBUILT_COURT_0_0_0_Geometry','#dddddd'),('V24_24_House_Front_Matching_Stone_Paving','#ccaaaa'),('SITE_KITCHEN_STONE_FLOOR_Geometry','#ddb38c'),('HOUSE_V20_ONE_SOLID_ENTRY_STEP_AND_PORCH_SUPPORT_Geometry','#eeeeff')]:
 a=source(n);t=a['v'][a['f']];sel=np.abs(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,2])>1e-7;ax.add_collection(PolyCollection(t[sel,:,:2],facecolor=col,edgecolor='none',alpha=.85))
for x0,y0,x1,y1,label in [(0,0,13,10,'HOUSE'),(.36,-7.1,3.96,-3.6,'PAVILION'),(8.34,-11.4,13.5,-2.855,'KITCHEN'),(5,-12.3,8.3,-11.2,'INNER GATE')]:
 ax.add_patch(plt.Rectangle((x0,y0),x1-x0,y1-y0,fill=False,color='black',lw=1.4));ax.text((x0+x1)/2,(y0+y1)/2,label,ha='center')
segs=json.loads((W/'v16/Drain_Segments.json').read_text())
for r in segs:
 a=np.array(r['a']);b=np.array(r['b']);ax.plot([a[0],b[0]],[a[1],b[1]],color='red',lw=.8)
 if r['j']%6==0:ax.text(*a,f"{r['ci']}:{r['j']}",fontsize=8,color='red')
ax.set_xlim(-27,17);ax.set_ylim(-19,14);ax.grid();ax.set_xlabel('X / m');ax.set_ylabel('Y / m');fig.savefig(D/'Plan.png',dpi=140)
print('SEGMENTS',json.dumps([r for r in segs if r['j']%6==0],ensure_ascii=False))
route=json.loads((W/'v24_18/Prepared_Geometry.json').read_text())['uv_route'];(D/'Perimeter_Route.json').write_text(json.dumps(route));print('UVROUTE',str(route)[:500])
for n in ['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry','SITE_V19_CONTINUOUS_PERIMETER_EAVE_BANDS_AND_FRAMES_Geometry']:
 a=source(n);v=a['v'];m=(v[:,1]>9)&(v[:,0]>-3)&(v[:,0]<15);print('NORTH_WALL',n,np.unique(np.round(v[m],4),axis=0).tolist()[:160])
