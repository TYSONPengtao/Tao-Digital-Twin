import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs'),str(W)]
import numpy as np,manifold3d as mf
from v24_13_geometry import roof_z,north_boundary
D=W/'v24_17';R=Path('E:/jz/JIA/Rebuild_V24_17/Reports');idx=json.loads((D/'Solid_Export_Index.json').read_text());rows={r['name']:r for r in idx['objects']};solids={};results=[];checks=[]
def solid(d):
 v=d['v'];f=d['f'];m=mf.Manifold(mf.Mesh64(np.array(v,dtype=np.float64,order='C'),np.array(f,dtype=np.uint64,order='C')))
 if m.status()==mf.Error.NoError and m.volume()>0:return m
 for dec in [9,8,7,6,5]:
  vv,ix=np.unique(np.round(v,dec),axis=0,return_inverse=True);ff=ix[f];t=vv[ff];ff=ff[np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-13];m=mf.Manifold(mf.Mesh64(np.array(vv,dtype=np.float64,order='C'),np.array(ff,dtype=np.uint64,order='C')))
  if m.status()==mf.Error.NoError and m.volume()>0:return m
 return m
def data(n):return np.load(D/rows[n]['file'])
def union(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
def box(lo,hi):return mf.Manifold.cube(np.array(hi)-lo).translate(lo)
for n,row in rows.items():
 m=solid(data(n));ok=m.status()==mf.Error.NoError and m.volume()>0;solids[n]=m;results.append({'name':n,'pass':ok,'status':str(m.status()),'volume_m3':m.volume(),'closed_bodies':len(m.decompose())if ok else 0});print('SOLID',n,ok,flush=True)
gables=['V24_14_Storage_West_Sealed_Gable','V24_14_Storage_East_Sealed_Gable','V24_Kitchen_Gable_Upper_Brick_Infill','V24_03_Kitchen_Rear_Gable_Wall'];wallset=['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry']+gables;walls=union([solids[n]for n in wallset]);positive=[p for p in walls.decompose()if p.volume()>1e-6];ck('New gables and accepted wall form a continuous masonry envelope',len(positive)==1,positive_bodies=len(positive),components=[p.volume()for p in walls.decompose()])
roofn='SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry';tilen='SITE_V14_INNER_STORAGE_INDIVIDUAL_TILE_COURSES_Geometry';rd=data(roofn);tv=data(tilen);tri=tv['v'][tv['f']];norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(norm,axis=1);norm/=np.maximum(area[:,None],1e-15);q=tri.mean(1);mask=(norm[:,2]>.65)&(area>1e-7);gap=q[mask,2]-np.array([roof_z(p[0],p[1])for p in q[mask]])+.022;ck('Visible storage tiles above support sheet, without coplanar pixel competition',len(gap)>100 and gap.min()>.0075,minimum_top_surface_separation_m=float(gap.min()),sampled_faces=len(gap))
v=(solids[roofn]^solids[tilen]).volume();ck('Storage tile coat does not intersect or disappear beneath the carrier',abs(v)<2e-6,overlap_m3=v)
sw=[n for n in rows if n.startswith('V24_15_Storage_')and any(k in n for k in ['Boarding','Rafters','Purlin'])];wood=union([solids[n]for n in sw]);vol=(wood^solids[roofn]).volume();ck('Storage wood deck remains under the separated ceramic roof',abs(vol)<2e-6,overlap_m3=vol)
for side,lo,hi in [('west',[12.8,-16.10,2.4],[13.204,-8.6,6]),('east',[18.686,-16.10,2.4],[19.0,-8.6,6])]:
 vol=(wood^box(lo,hi)).volume();ck('No timber projects through the '+side+' exterior gable',abs(vol)<1e-7,overlap_m3=vol)
for n in ['V24_15_Storage_Continuous_Wood_Boarding','V24_15_Storage_Continuous_Round_Rafters']:
 v=data(n)['v'];overshoot=max(p[1]-north_boundary(p[0])for p in v);ck('Rear timber ends inside curved brick wall / '+n,overshoot<=-.015,maximum_signed_projection_m=float(overshoot))
kw=[n for n in rows if n in ['SITE_KITCHEN_FASCIA_BOARD_Geometry','SITE_KITCHEN_VISIBLE_SHEATHING_BOARDS_Geometry','SITE_KITCHEN_V12_LONGITUDINAL_ROUND_PURLINS_Geometry','SITE_KITCHEN_V12_TRADITIONAL_EXPOSED_TIMBER_FRAMES_Geometry','SITE_KITCHEN_V12_VISIBLE_DENSE_WOOD_RAFTERS_Geometry']];kwood=union([solids[n]for n in kw]);outside=union([box([8.15,-12.4,2.24],[15,-11.941,6]),box([8.15,-2.574,2.24],[15,-2.0,6])]);v=(kwood^outside).volume();ck('Kitchen non-porch roof timber contained behind brick gable ends',abs(v)<1e-7,exterior_overlap_m3=v)
sn=['V24_17_Secondary_Screenwall_Continuous_Tile_Bed','V24_17_Secondary_Screenwall_Continuous_Masonry_Carrier','V24_17_Secondary_Screenwall_Barrel_and_Pan_Tiles','V24_17_Secondary_Screenwall_Eave_Disks','V24_17_Secondary_Screenwall_Level_Ridge','V24_14_Secondary_Screenwall_Volute_End','V24_14_Secondary_Screenwall_Volute_Rim','V24_14_Secondary_Screenwall_Stepped_End_Soffit'];ss=union([solids[n]for n in sn]);pp=[p for p in ss.decompose()if p.volume()>1e-7];ck('Secondary screen carrier tile bed end scroll and tiles physically connected',len(pp)==1,positive_bodies=len(pp),component_volumes=[p.volume()for p in ss.decompose()])
for i in [1,2]:
 post=solids[f'V24_11_Storage_Veranda_Column_{i}'];v=(post^walls).volume();ck('Original veranda post stays outside sealed masonry / '+str(i),abs(v)<1e-7,overlap_m3=v)
good=all(r['pass']for r in results+checks);out={'status':'PASS_INDEPENDENT_SAVED_SOLIDS'if good else'FAIL_INDEPENDENT_SAVED_SOLIDS','model_sha256':idx['model_sha256'],'solids':results,'spatial_checks':checks};(R/'V24_17_Independent_Solid_QA.json').write_text(json.dumps(out,indent=2))
boxes=[('Entry white bay bypass',[12.55,-16.05,-.37],[1.40,.55,2.02]),('Continuous veranda',[13.95,-15.42,-.37],[4.05,.60,2.02]),('Far post bypass',[18.02,-15.35,-.37],[.45,.33,2.02]),('Storage door opening',[15.64,-14.52,-.37],[.60,.45,1.95]),('East portal',[18.47,-15.61,-.37],[.45,.59,2.02])];route=[]
for label,lo,sz in boxes:
 bb=mf.Manifold.cube(sz).translate(lo);hits=[]
 for n,m in solids.items():
  if not rows[n]['obstacle']:continue
  vol=(m^bb).volume()
  if vol>1e-7:hits.append({'object':n,'overlap_m3':vol})
 route.append({'label':label,'origin':lo,'size':sz,'obstructions':hits})
clear=all(not r['obstructions']for r in route);(R/'V24_17_Independent_Clearance_QA.json').write_text(json.dumps({'status':'PASS_INDEPENDENT_CLEARANCE'if clear else'FAIL_INDEPENDENT_CLEARANCE','model_sha256':idx['model_sha256'],'samples':route},indent=2));print('SOLIDS',good,'CLEARANCE',clear,flush=True)
for r in results+checks:
 if not r['pass']:print('FAIL',r,flush=True)
for r in route:
 if r['obstructions']:print('BLOCKED',r,flush=True)
