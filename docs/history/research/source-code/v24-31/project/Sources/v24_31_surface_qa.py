import sys,json,hashlib
from pathlib import Path
W=Path(__file__).parent;D=W/'v24_31';O=Path('E:/jz/JIA/Rebuild_V24_31');R=O/'Reports';P=O/'Blender/Architecture_Complete_V24_31.blend';sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree
idx={r['name']:r for r in json.loads((D/'Final_Geometry_Index.json').read_text('utf8'))};cache={};checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw,flush=True)
def up(n):
 if n in cache:return cache[n]
 a=np.load(D/idx[n]['file']);t=a['v'][a['f']];no=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);t=t[no[:,2]>1e-9];ps=[Polygon(q[:,:2])for q in t];cache[n]=(t,ps,STRtree(ps));return cache[n]
def near_overlap(a,b,tol=.002):
 ta,pa,_=up(a);tb,pb,tree=up(b);area=0.;pairs=0;worst=None
 for t,p in zip(ta,pa):
  for j in tree.query(p):
   q=p.intersection(pb[j])
   if q.area<1e-10:continue
   c=q.representative_point();pt=np.array([c.x,c.y]);za=[]
   for tr in [t,tb[j]]:
    A=tr[1,:2]-tr[0,:2];B=tr[2,:2]-tr[0,:2];Q=pt-tr[0,:2];det=A[0]*B[1]-A[1]*B[0];u=(Q[0]*B[1]-Q[1]*B[0])/det;v=(A[0]*Q[1]-A[1]*Q[0])/det;za.append(tr[0,2]+u*(tr[1,2]-tr[0,2])+v*(tr[2,2]-tr[0,2]))
   diff=abs(za[0]-za[1])
   if diff<tol:area+=q.area;pairs+=1;worst=min(worst,diff)if worst is not None else diff
 return area,pairs,worst
road='V24_31_Continuous_Gray_Road_And_Storage_Approach';pad='V24_30_Outer_Yard_White_Building_Pad';curb='V24_30_Individual_Roadside_Curb_Stones';soil='SITE_V16_GRADED_INTERIOR_SOIL_Geometry';body='V24_30_Graded_Approach_Curb_Retaining_Base';low='V24_30_Low_Main_Court';high='V24_30_High_North_Lane_And_Rear'
for a,b in [(pad,curb),(pad,road),(pad,soil),(road,soil),(road,low+'_Running_Bond_Stone'),(road,'SITE_KITCHEN_STONE_FLOOR_Geometry'),(curb,body),(low+'_Running_Bond_Stone',low+'_Joint_Base'),(high+'_Running_Bond_Stone',high+'_Joint_Base')]:
 area,pairs,d=near_overlap(a,b);ck('No overlapping visible ground skins within 2mm / '+a+' | '+b,area<2e-5,near_coplanar_area_m2=area,triangle_pairs=pairs,minimum_separation_m=d)
prep=json.loads((D/'Prepared_Geometry.json').read_text('utf8'));ck('Original exact pad cap overlap was removed geometrically',prep['proof']['pad_curb']['before_coplanar_overlap_m2']>1.5 and prep['proof']['pad_curb']['after_coplanar_overlap_m2']<1e-7,before_m2=prep['proof']['pad_curb']['before_coplanar_overlap_m2'],after_m2=prep['proof']['pad_curb']['after_coplanar_overlap_m2'])
for n in [road,pad,'V24_31_Stair_Rounded_Handrails']:
 a=np.load(D/idx[n]['file']);v=a['v'];f=a['f'];ids=np.sort(np.round(v[f],6),axis=1);keys=[tuple(sorted(tuple(q)for q in t))for t in v[f].round(6)];dups=len(keys)-len(set(keys));ck('No duplicate triangles in repaired mesh / '+n,dups==0,duplicate_triangles=dups)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[r for r in checks if not r['pass']];(R/'V24_31_Surface_QA.json').write_text(json.dumps({'status':'PASS_GROUND_SURFACE_OWNERSHIP_AND_NO_NEAR_COPLANAR_SKINS'if not fail else'FAIL','model_sha256':h,'checks':checks,'failures':fail,'tolerance_m':.002,'tested_scope':'Repaired inner and outer ground, road, curb, joint beds and new rail mesh. Hidden collider excluded.'},ensure_ascii=False,indent=2),encoding='utf8');print('V31_SURFACE_QA',len(checks),'FAIL',len(fail),flush=True)
