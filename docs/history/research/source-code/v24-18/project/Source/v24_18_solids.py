import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,manifold3d as mf
from v24_18_common import solid,cube,union
D=W/'v24_18';R=Path('E:/jz/JIA/Rebuild_V24_18/Reports');idx=json.loads((D/'Solid_Export_Index.json').read_text());rows={r['name']:r for r in idx['objects']};prep=json.loads((D/'Prepared_Geometry.json').read_text());checks=[];cache={};stats=[]
def data(n):return np.load(D/rows[n]['file'])
def m(n,mat=None):
 key=(n,mat)
 if key not in cache:
  d=data(n);f=d['f']if mat is None else d['f'][d['mi']==mat];cache[key]=solid(d['v'],f,n)
 return cache[key]
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
skip={'SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_V16_GRADED_INTERIOR_SOIL_Geometry'}
for row in prep['objects']:
 n=row['name']
 if n in skip:continue
 try:
  a=m(n);stats.append({'name':n,'pass':a.status()==mf.Error.NoError and a.volume()>0,'volume_m3':a.volume(),'closed_bodies':len(a.decompose())})
 except Exception as e:stats.append({'name':n,'pass':False,'error':str(e)})
plinth=m('V24_18_House_Continuous_Grade_Plinth');slab=m('SLAB_JOINED_F1_Geometry');v=(plinth^slab).volume();ck('Continuous plinth positively contacts retained first-floor slab',v>.5,overlap_m3=v);ck('One connected closed plinth below whole house',len(plinth.decompose())==1)
sam=[]
for p in prep['proof']['house_grounding']['grade_samples']:
 if p['z']is None:continue
 x,y=p['xy'];z=p['z'];inside=(plinth^cube([x-.002,y-.002,z-.003],[x+.002,y+.002,z+.003])).volume();sam.append({'xy':[x,y],'grade_z':z,'plinth_volume_at_ground_m3':inside})
from shapely.geometry import Polygon,Point
hp=Polygon(prep['house_uv_route']['xy']);inside_samples=[p for p in sam if hp.buffer(-.005).contains(Point(p['xy']))]
soil=data('SITE_V16_GRADED_INTERIOR_SOIL_Geometry');tt=soil['v'][soil['f']];A=tt[:,1,:2]-tt[:,0,:2];B=tt[:,2,:2]-tt[:,0,:2];det=A[:,0]*B[:,1]-A[:,1]*B[:,0];safe=np.where(abs(det)>1e-12,det,1)
edge_samples=[];pp=np.array(hp.exterior.coords);signed=sum(np.cross(a,b)for a,b in zip(pp[:-1],pp[1:]));sign=1 if signed>0 else-1
for a,b in zip(pp[:-1],pp[1:]):
 d=b-a;L=np.linalg.norm(d)
 if L<.30:continue
 u=d/L;n=sign*np.array([-u[1],u[0]]);p=(a+b)/2+n*.02;q=p-tt[:,0,:2];v1=(q[:,0]*B[:,1]-q[:,1]*B[:,0])/safe;v2=(A[:,0]*q[:,1]-A[:,1]*q[:,0])/safe;ok=(abs(det)>1e-12)&(v1>=-1e-6)&(v2>=-1e-6)&(v1+v2<=1+1e-6)
 if not ok.any():continue
 zz=tt[:,0,2]+v1*(tt[:,1,2]-tt[:,0,2])+v2*(tt[:,2,2]-tt[:,0,2]);z=float(zz[ok].max())
 if z<-1.2 or z>-.2:continue
 x,y=p;vol=(plinth^cube([x-.002,y-.002,z-.003],[x+.002,y+.002,z+.003])).volume();edge_samples.append({'xy':p.tolist(),'grade_z':z,'plinth_volume_at_ground_m3':vol})
ck('Plinth reaches original grade at interior and perimeter stations',len(inside_samples)>=6 and len(edge_samples)>=10 and all(p['plinth_volume_at_ground_m3']>9.5e-8 for p in inside_samples+edge_samples),interior_samples=inside_samples,edge_samples=edge_samples)
for r in prep['proof']['removed_corner_post_regions']:
 v=(m(f"FACADE_CONTINUOUS_F{r['floor']}_Geometry")^cube(r['lo'],r['hi'])).volume();ck('No marked false white column at '+str((r['floor'],r['center_x'])),abs(v)<1e-7,overlap_m3=v)
gate=union([m(n)for n in rows if n.startswith('V24_XIESHAN_')])
for n in ['V24_Kitchen_Gable_Upper_Brick_Infill','V24_Kitchen_Curved_Gable_Coping','SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry']:
 v=(m(n)^gate).volume();ck('Kitchen clears unchanged inner gate / '+n,abs(v)<1e-6,overlap_m3=v)
white=m('SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry');v=(white^cube([3.201,-17.99,3.101],[10.839,-16.01,7.9])).volume();ck('No old white finish projects into recessed fan',abs(v)<1e-7,overlap_m3=v)
from v24_18_screen import center,h,X0,X1,JL,JR,HY
shell=m('SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL_Geometry');core=m('SITE_SOUTH_SCREENWALL_V12_STEPPED_MASONRY_UNDEREAVE_Geometry');v=(shell^core).volume();ck('Recessed roof bears on continuous original wall-centred carrier',v>1e-4,overlap_m3=v)
for end,junction in [(X0,JL),(X1,JR)]:
 x=end+(junction-end)*.045;t=abs((x-junction)/(end-junction));edge=h(x,HY*t);mid=h(x,0);ck('Triangular fan centre below raised fork edges / '+str(end),edge-mid>.35,edge_z=edge,centre_z=mid,recess_m=edge-mid)
roofparts=union([shell,core,m('V24_09_Screenwall_Solid_Fork_and_Ridge_Seats'),m('SITE_SOUTH_SCREENWALL_CURVED_EAVE_AND_RIDGE_BORDER_Geometry')]);pp=[p for p in roofparts.decompose()if p.volume()>1e-7];ck('Roof bed carrier and branch ridge seats connected',len(pp)==1,positive_bodies=len(pp))
collision=[]
for w in prep['windows']:
 fixed=m(w['name'])
 for s in w['sashes']:
  name='V24_18_'+s['name']+'_Outward_Hinge';moving=union([m(name+'_Frame'),m(name+'_Glass')]);pivot=np.array(s['pivot']);full=math.radians(s['angle_degrees']);out=[]
  for f,fac in [(1,0),(20,.5),(40,1)]:
   a=full*(fac-1);c=math.cos(a);ss=math.sin(a);rot=np.array([[c,-ss,0],[ss,c,0],[0,0,1]]);posed=moving.transform(np.c_[rot,pivot-rot@pivot]);v=(posed^fixed).volume();out.append({'frame':f,'overlap_with_fixed_window_m3':v});ck('Outward sash clears fixed frame / '+name+' / '+str(f),abs(v)<1e-7,overlap_m3=v)
  collision.append({'sash':name,'poses':out})
good=all(r['pass']for r in checks+stats);out={'status':'PASS_INDEPENDENT_NATIVE_SOLIDS'if good else'FAIL_INDEPENDENT_NATIVE_SOLIDS','model_sha256':idx['model_sha256'],'solids':stats,'checks':checks,'window_collision':collision};(R/'V24_18_Independent_Solid_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('SOLID_QA',good,len(stats),len(checks),flush=True)
for r in stats+checks:
 if not r['pass']:print('FAIL',r,flush=True)
