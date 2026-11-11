from pathlib import Path
import sys,json,hashlib
W=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(W/'np1'),str(W/'geomlibs')]
import numpy as np,manifold3d as mf
FD=W/'v26_5/Final';OD=W/'v26_4/Final';PD=W/'v26_1'
P=Path('E:/jz/JIA/Rebuild_V26_5/Blender/Architecture_Complete_V26_5.blend')
R=P.parents[1]/'Reports';R.mkdir(exist_ok=True)
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
assert h=='202625cfe023a542ce75b7cbee3e05f0dee1767543a4ac7633b401d796e6c51a'
assert 'READBACK_DONE 20 0' in (W/'v26_5_readback.log').read_text('utf8')
J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))}
OJ={r['name']:r for r in json.loads((OD/'Geometry_Index.json').read_text('utf8'))}
PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))}
checks=[]
def ck(n,yes,**kw):
 checks.append({'check':n,'pass':bool(yes),**kw});print(n,bool(yes),kw if not yes else '',flush=True)
def mesh(a):
 # Read native saved triangles directly; no prepared geometry or repair recipe.
 v=np.array(a['v'],np.float64);v,ix=np.unique(v,axis=0,return_inverse=True)
 f=ix[a['f']].astype(np.uint64)
 m=mf.Manifold(mf.Mesh64(np.array(v,copy=True),np.array(f,copy=True)))
 assert m.status()==mf.Error.NoError,m.status()
 return m
def cube(lo,hi):
 lo=np.array(lo);hi=np.array(hi);return mf.Manifold.cube(hi-lo).translate(lo)
def arr(n,d=FD,index=J):return np.load(d/index[n]['file'])
HN='V26_3_House_Connected_Walls_And_Stairs';house=mesh(arr(HN));oldhouse=mesh(arr(HN,OD,OJ))
q=cube([10.701,9.6,-.4],[10.754,9.679,3.04]);after=max(0,(house^q).volume());before=max(0,(oldhouse^q).volume())
ck('Screenshot001202 obsolete tall projection is absent',after<1e-10 and before>1e-5,before_intersection_m3=before,after_intersection_m3=after,region_m=[[10.701,9.6,-.4],[10.754,9.679,3.04]])
for k in [1,2,3]:
 wn=f'WINDOW_BACK_F1_{k}_Geometry';sn=f'CONSTRUCTION_SILL_WINDOW_BACK_F1_{k}_Geometry'
 wa=arr(wn);s=arr(sn);lo=wa['v'].min(0);hi=wa['v'].max(0);sl=s['v'].min(0);sh=s['v'].max(0)
 ck(f'Rear F1 window{k} sill and head remain within actual glazing jamb width',sl[0]>=lo[0]-2e-6 and sh[0]<=hi[0]+2e-6,window_x_m=[float(lo[0]),float(hi[0])],sill_x_m=[float(sl[0]),float(sh[0])])
 old=arr(wn,OD,OJ);equal=J[wn]['materials']==OJ[wn]['materials'] and all(np.array_equal(wa[z],old[z])for z in ['v','f','mi','uv'])
 ck(f'Rear F1 window{k} original frame glass UV and material assignment unchanged',equal)
 # The defective ears were below the original structural beam soffit3.05.
 ear=cube([lo[0]+.005,9.57,hi[2]+.001],[hi[0]-.005,9.679,3.049])
 av=max(0,(house^ear).volume());bv=max(0,(oldhouse^ear).volume())
 ck(f'Rear F1 window{k} obsolete head finish ears removed',av<1e-9,old_ear_volume_m3=bv,remaining_ear_volume_m3=av)
 # Check every head height and lateral position, including old end-gap zones.
 hs=[];bad=[]
 for x in np.linspace(lo[0]+.006,hi[0]-.006,31):
  for z in np.linspace(hi[2]+.002,3.315,7):
   hits=sorted(house.ray_cast([float(x),9.6,float(z)],[float(x),10.03,float(z)]),key=lambda h:h.position[1])
   valid=len(hits)==2 and hits[0].normal[1]<-.9 and hits[1].normal[1]>.9
   r={'x_m':float(x),'z_m':float(z),'hits':len(hits),'continuous':valid};hs.append(r)
   if not valid:bad.append(r)
 ck(f'Rear F1 window{k} full head reaches slab without end holes',not bad,samples=len(hs),failures=bad)
gap=cube([3.652,9.70,3.06],[3.698,9.88,3.30]);missing=max(0,(gap-house).volume());oldmissing=max(0,(gap-oldhouse).volume())
ck('Screenshot001426 old49.7mm right column head gap is filled',missing<1e-10 and oldmissing>.001,missing_volume_m3=missing,old_missing_volume_m3=oldmissing)
rear=[];bad=[]
for x in [.5,1.4,2.0,4.4,5.2,6.2,7.1,11.1,11.8,12.4]:
 for z in [-.2,.5,1.2,2.4,3.02]:
  hits=sorted(house.ray_cast([x,9.6,z],[x,10.03,z]),key=lambda h:h.position[1])
  r={'x_m':x,'z_m':z,'hits':len(hits)}
  if len(hits)==2:
   r['inner_y_m']=float(hits[0].position[1]);r['outer_y_m']=float(hits[1].position[1]);r['thickness_mm']=(r['outer_y_m']-r['inner_y_m'])*1000
   valid=abs(r['inner_y_m']-9.68)<3e-5 and abs(r['outer_y_m']-9.9002)<3e-5 and abs(r['thickness_mm']-220.2)<.06
  else:valid=False
  rear.append(r)
  if not valid:bad.append(r)
ck('Regular rear wall segments have220.2mm carrier and one pair of faces',not bad,samples=len(rear),failures=bad)
divider=[]
for y in [7.6,8.4,9.2,9.55,9.65]:
 for z in [.0,1.,2.,2.9]:
  hits=sorted(house.ray_cast([10.4,y,z],[10.9,y,z]),key=lambda h:h.position[0])
  r={'y_m':y,'z_m':z,'hits':len(hits)}
  r['thickness_mm']=(float(hits[-1].position[0]-hits[0].position[0])*1000)if len(hits)==2 else None
  r['pass']=r['thickness_mm']is not None and abs(r['thickness_mm']-100)<.05;divider.append(r)
ck('WC divider stays100mm from front to repaired rear connection',all(r['pass']for r in divider),samples=divider)
cores=[]
for r in json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components']:
 n=r['name'];lo,hi=np.array(r['bounds_m'])
 if not n.startswith(('KZ_','BEAM_')) or lo[2]>3.4 or hi[1]<9.5:continue
 m=mesh(np.load(PD/PI[n]['file']));loss=max(0,(m-house).volume());cores.append({'name':n,'missing_volume_m3':loss})
ck('All relevant original rear F1 beam and column cores remain intact',all(r['missing_volume_m3']<1e-6 for r in cores),components=cores)
fail=[r for r in checks if not r['pass']]
out={'model':str(P),'model_sha256':h,'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail,'basis':'Independent defect-coordinate volume probes and native saved triangle raycasts from fresh readback, original source glass/core comparisons; no prepared mesh or repair recipe used.','rear_wall_thickness_samples':rear,'visual_review':['After_09_F1_Right_WC_Rear_Corner_Cycles.png','After_10_F1_Left_Rear_Window_Head_Cycles.png','After_11_F1_Stair_WC_Window_Head_Cycles.png']}
fn=R/'V26_5_WC_Window_Regression_QA.json';fn.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('REGRESSION_DONE',len(checks),'FAIL',len(fail),str(fn),flush=True)
