import sys,json,math
from pathlib import Path
W=Path(__file__).parent;sys.path.insert(0,str(W));from v24_19_common import *
R=Path('E:/jz/JIA/Rebuild_V24_19/Reports');idx=json.loads((D/'Solid_Export_Index.json').read_text());rows={r['name']:r for r in idx['objects']};prep=json.loads((D/'Prepared_Geometry.json').read_text());checks=[];stats=[];cache={}
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
def m(n):
 if n not in cache:
  a=np.load(D/rows[n]['file']);cache[n]=solid(a['v'],a['f'],n)
 return cache[n]
for row in prep['objects']:
 n=row['name']
 try:
  a=m(n);stats.append({'name':n,'pass':a.status()==mf.Error.NoError and a.volume()>0,'closed_bodies':len(a.decompose()),'volume_m3':a.volume()})
 except Exception as e:stats.append({'name':n,'pass':False,'error':str(e)})
gate=union([m(n)for n in ['V24_XIESHAN_01_Upper_Two_Main_Slopes','V24_XIESHAN_02_Four_Lower_Hipped_Eaves','V24_XIESHAN_07_Closed_Pale_Ceiling','V24_XIESHAN_08_Five_Continuous_Stepped_Eave_Bands','V24_XIESHAN_09_Continuous_Eave_Bearing_Core']])
for n in ['SITE_KITCHEN_CHINESE_TILE_ROOF_Geometry','V24_19_Kitchen_True_Tiled_Verge_Courses','V24_Kitchen_Curved_Gable_Coping','V24_Kitchen_Gable_Upper_Brick_Infill']:
 v=(m(n)^gate).volume();ck('Kitchen new work clears unchanged gate / '+n,abs(v)<2e-6,overlap_m3=v)
for side in ['East','West']:
 n=f'V24_14_Storage_{side}_Sealed_Gable';a=m(n);bb=a.bounding_box();ck('Compact faceted brick head / '+side,abs(bb[5]-4.91)<2e-5 and len(a.decompose())==1,peak_z=bb[5])
 d=np.load(D/rows[n]['file']);vv=d['v'];q=vv[abs(vv[:,2]-4.91)<2e-5];ck('Short flat crown / '+side,len(q)>=4 and abs(np.ptp(q[:,1])-.24)<2e-5)
 bed=m('SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry');tile=m('SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry');x=18.79 if side=='East'else 13.10;probe=cube([x-.045,-14.03,3.65],[x+.045,-13.97,4.0]);ck('Raised clay course exists outside gable / '+side,(tile^probe).volume()>1e-6)
 ck('Continuous ceramic roof bed carries projecting edge / '+side,(bed^probe).volume()>1e-5)
row=next(r for r in prep['objects']if r['name']=='V24_03_Kitchen_Rear_Gable_Wall');expected=solid(row['v'],row['f']);actual=m(row['name']);delta=(expected-actual).volume()+(actual-expected).volume();ck('North gable UV subdivisions retain solid geometry',delta<1e-5,symmetric_difference_m3=delta)
for row in prep['raw_objects']:
 n=row['name'];d=np.load(D/rows[n]['file']);v=d['v'];f=d['f'];src=np.load(D/INDEX[n]['file']);old=src['v'][src['f']];t=v[f]
 # The horizontal projection of every surface is retained by deformation;
 # upward faces remain upward, so no folded/crossed ground facets appear.
 nxy=np.cross(t[:,1,:2]-t[:,0,:2],t[:,2,:2]-t[:,0,:2]);oldxy=np.cross(old[:,1,:2]-old[:,0,:2],old[:,2,:2]-old[:,0,:2]);area=float(abs(nxy).sum()/2);oa=float(abs(oldxy).sum()/2)
 ck('Ground projection area preserved / '+n,abs(area-oa)<2e-3,original_projected_surface_area_m2=oa,final_projected_surface_area_m2=area)
 # Check thickness at native old paired top/bottom XY vertices. The paving
 # is translated locally as a volume, not collapsed into a surface.
 if 'REBUILT_COURT'in n:
  def span(tr,x,y):
   A=tr[:,1,:2]-tr[:,0,:2];B=tr[:,2,:2]-tr[:,0,:2];de=A[:,0]*B[:,1]-A[:,1]*B[:,0];safe=np.where(abs(de)>1e-10,de,1);q=[x,y]-tr[:,0,:2];a=(q[:,0]*B[:,1]-q[:,1]*B[:,0])/safe;b=(A[:,0]*q[:,1]-A[:,1]*q[:,0])/safe;good=(abs(de)>1e-10)&(a>=-1e-7)&(b>=-1e-7)&(a+b<=1+1e-7)
   if not good.any():return None
   z=(tr[:,0,2]+a*(tr[:,1,2]-tr[:,0,2])+b*(tr[:,2,2]-tr[:,0,2]))[good];return float(z.max()-z.min())
  samples=[]
  for p in old.mean(1):
   a=span(old,*p[:2]);b=span(t,*p[:2])
   if a is not None and a>.1 and b is not None:samples.append({'xy':p[:2].tolist(),'before_thickness_m':a,'after_thickness_m':b})
  minimum=min((q['after_thickness_m']for q in samples),default=0);ratio=min((q['after_thickness_m']/q['before_thickness_m']for q in samples),default=0)
  ck('Pavement retains solid thickness while following revised grade / '+n,bool(samples)and minimum>.12 and ratio>.75,minimum_measured_thickness_m=minimum,minimum_retained_thickness_ratio=ratio,maximum_thickness_change_m=max(abs(q['before_thickness_m']-q['after_thickness_m'])for q in samples)if samples else None,samples=samples)
good=all(r['pass']for r in checks+stats);out={'status':'PASS_INDEPENDENT_NATIVE_GEOMETRY'if good else'FAIL_INDEPENDENT_NATIVE_GEOMETRY','model_sha256':idx['model_sha256'],'solids':stats,'checks':checks};(R/'V24_19_Independent_Geometry_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('V19_INDEPENDENT_QA',good,len(stats),len(checks),flush=True)
for r in stats+checks:
 if not r['pass']:print('FAIL',{k:v for k,v in r.items()if k!='samples'},flush=True)
