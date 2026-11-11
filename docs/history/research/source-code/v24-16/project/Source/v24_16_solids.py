import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,manifold3d as mf
D=W/'v24_16';R=Path('E:/jz/JIA/Rebuild_V24_16/Reports');idx=json.loads((D/'Solid_Export_Index.json').read_text());rows={r['name']:r for r in idx['objects']};results=[];checks=[];solids={}
def solid(d):
 m=mf.Manifold(mf.Mesh64(np.array(d['v'],dtype=np.float64,order='C'),np.array(d['f'],dtype=np.uint64,order='C')))
 if m.status()==mf.Error.NoError and m.volume()>0:return m
 for dec in [9,8,7,6,5]:
  v,ix=np.unique(np.round(d['v'],dec),axis=0,return_inverse=True);f=ix[d['f']];t=v[f];f=f[np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-13];m=mf.Manifold(mf.Mesh64(np.array(v,dtype=np.float64,order='C'),np.array(f,dtype=np.uint64,order='C')))
  if m.status()==mf.Error.NoError and m.volume()>0:return m
 return m
def union(ms):return mf.Manifold.batch_boolean(ms,mf.OpType.Add)
def ck(n,p,**kw):checks.append({'check':n,'pass':bool(p),**kw})
def data(n):return np.load(D/rows[n]['file'])
wallnames=['SITE_PERIMETER_JOINED_RETAINING_WALL_0_Geometry','SITE_V15_PERIMETER_WHITE_INSIDE_FINISH_Geometry']
want={r['name']for r in idx['objects']if r['changed']and r['name']not in wallnames}|{r['name']for r in idx['objects']if r['obstacle']}|{n for n in rows if n.startswith('V24_15_Storage_')}|{'SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry','V24_14_Storage_West_Sealed_Gable','V24_14_Storage_East_Sealed_Gable'}
for n in sorted(want):
 m=solid(data(n));ok=m.status()==mf.Error.NoError and m.volume()>0;solids[n]=m;results.append({'name':n,'pass':ok,'status':str(m.status()),'volume_m3':m.volume(),'closed_bodies':len(m.decompose())if ok else 0});print('SOLID',n,ok,flush=True)
woodnames=[n for n in solids if (n.startswith('V24_15_Storage_')and'Amber_Panes'not in n)or n=='V24_11_Storage_Diagonal_Gallery_Bearing_and_Rafter_Tails'];wood=union([solids[n]for n in woodnames]);roof=solids['SITE_V14_INNER_STORAGE_GABLE_ROOF_Geometry'];v=(wood^roof).volume();ck('Reconnected timber clear of storage roof shell',abs(v)<1e-7,overlap_m3=v)
large=[p for p in wood.decompose()if p.volume()>2e-4];ck('Roof veranda and brackets form a connected structural timber body',len(large)==1,large_body_count=len(large))
for i in [1,2]:
 post=solids[f'V24_11_Storage_Veranda_Column_{i}'];base=solids[f'V24_11_Storage_Veranda_Column_Base_{i}'];ck(f'Column {i} seats on its stone base',(post^base).volume()>1e-6)
 for n in ['SITE_V17_CONNECTED_KITCHEN_STORAGE_MASONRY_Geometry','V24_16_Storage_Entrance_White_Wall_Return']:
  v=(post^solids[n]).volume();ck(f'Column {i} clear of '+n,abs(v)<1e-7,overlap_m3=v)
v=(solids['V24_15_Storage_Upper_Transom_Amber_Panes']^wood).volume();ck('Upper glazing clear of the reconnected timber',abs(v)<1e-7,overlap_m3=v)
screen=['SITE_SOUTH_SCREENWALL_'+s+'_Geometry'for s in ['CURVED_TILE_SHELL','V12_STEPPED_MASONRY_UNDEREAVE','V12_CLOSED_EAVE_FASCIA','CURVED_EAVE_AND_RIDGE_BORDER','V12_HIGH_RIDGE_FINIALS']]+['V24_09_Screenwall_Solid_Fork_and_Ridge_Seats'];s=union([solids[n]for n in screen]);parts=s.decompose();positive=[p for p in parts if p.volume()>1e-7];ck('Screen roof corbel core fork beds and broad horn roots connected',len(positive)==1,connected_positive_volume_bodies=len(positive),enclosed_void_volume_m3=-sum(p.volume()for p in parts if p.volume()<0),component_signed_volumes=[p.volume()for p in parts])
core=solids['SITE_SOUTH_SCREENWALL_V12_STEPPED_MASONRY_UNDEREAVE_Geometry'];shell=solids['SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL_Geometry'];v=(core^shell).volume();ck('Screen roof has real overlap bearing on masonry crown',v>.015,contact_overlap_m3=v)
# Independently measure lower wall faces and compare each saved roof section.
wd=data(wallnames[0]);tri=wd['v'][wd['f']];q=tri[:,:,2]-1.;segs=[]
for t,d in zip(tri[(q.min(1)<0)&(q.max(1)>0)],q[(q.min(1)<0)&(q.max(1)>0)]):
 ps=[]
 for a,b in [(0,1),(1,2),(2,0)]:
  if d[a]*d[b]<0:ps.append(t[a]+(t[b]-t[a])*(-d[a]/(d[b]-d[a])))
 if len(ps)==2:segs.append(ps)
def wc(x):
 ys=[]
 for p in segs:
  if min(p[0][0],p[1][0])-1e-6<=x<=max(p[0][0],p[1][0])+1e-6 and abs(p[1][0]-p[0][0])>1e-7:
   y=p[0][1]+(p[1][1]-p[0][1])*(x-p[0][0])/(p[1][0]-p[0][0])
   if -17.6<y<-16.3:ys.append(y)
 return (min(ys)+max(ys))/2
for n,label in [('SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL_Geometry','roof'),('SITE_SOUTH_SCREENWALL_V12_STEPPED_MASONRY_UNDEREAVE_Geometry','bearing'),('V24_11_Screenwall_Continuous_Stepped_Stone_Plinth','plinth')]:
 v=data(n)['v'];errors=[]
 for x in np.unique(np.round(v[:,0],5)):
  if not 3.3<x<10.75:continue
  p=v[abs(v[:,0]-x)<1e-5];errors.append(abs((p[:,1].min()+p[:,1].max())/2-wc(float(x))))
 ck('Saved '+label+' centred on actual lower wall',bool(errors)and max(errors)<.004,section_count=len(errors),maximum_offset_m=max(errors))
for x in [3.25,10.80]:
 v=data('V24_09_Screenwall_White_End_Inset_Panels')['v'];p=v[abs(v[:,0]-x)<.02];err=abs((p[:,1].min()+p[:,1].max())/2-wc(x));ck('End white inset centred at X='+str(x),err<.003,offset_m=err)
rv=data('SITE_SOUTH_SCREENWALL_CURVED_TILE_SHELL_Geometry')['v'];xs=np.unique(np.round(rv[:,0],5))
for target in [3.15,3.45,3.65,10.40,10.60,10.90]:
 x=float(xs[np.argmin(abs(xs-target))]);vv=rv[abs(rv[:,0]-x)<1e-5];cy=(vv[:,1].min()+vv[:,1].max())/2;yy=np.unique(np.round(vv[:,1],5));zz=np.array([vv[abs(vv[:,1]-y)<1e-5,2].max()for y in yy]);t=(3.85-x)/.9 if x<3.85 else(x-10.20)/.9;zc=zz[np.argmin(abs(yy-cy))];branch=max(zz[np.argmin(abs(yy-(cy+s*.66*t)))]for s in [-1,1]);ck('Saved end hip fan has no deep central valley at X='+str(x),zc>=branch-.025,central_top_z=float(zc),branch_level_z=float(branch))
allgood=all(r['pass']for r in results+checks);(R/'V24_16_Independent_Solid_QA.json').write_text(json.dumps({'status':'PASS_INDEPENDENT_SAVED_SOLIDS'if allgood else'FAIL_INDEPENDENT_SAVED_SOLIDS','model_sha256':idx['model_sha256'],'solids':results,'spatial_checks':checks},indent=2))
boxes=[('Entry around corrected wall return',[12.55,-16.05,-.37],[1.40,.55,2.02]),('Continuous veranda',[13.95,-15.42,-.37],[4.05,.60,2.02]),('Far post bypass',[18.02,-15.35,-.37],[.45,.33,2.02]),('Storage door opening',[15.64,-14.52,-.37],[.60,.45,1.95]),('East end portal',[18.47,-15.61,-.37],[.45,.59,2.02])];routes=[]
for label,lo,sz in boxes:
 box=mf.Manifold.cube(sz).translate(lo);hits=[]
 for n,m in solids.items():
  if not(rows[n]['obstacle']or n.startswith('V24_15_Storage_')):continue
  v=(m^box).volume()
  if v>1e-7:hits.append({'object':n,'overlap_m3':v})
 routes.append({'label':label,'origin':lo,'size':sz,'obstructions':hits})
good=all(not r['obstructions']for r in routes);(R/'V24_16_Independent_Clearance_QA.json').write_text(json.dumps({'status':'PASS_INDEPENDENT_CLEARANCE'if good else'FAIL_INDEPENDENT_CLEARANCE','model_sha256':idx['model_sha256'],'samples':routes},indent=2));print('SOLIDS',allgood,'CLEARANCE',good,flush=True)
for r in results+checks:
 if not r['pass']:print('FAIL',r,flush=True)
for r in routes:
 if r['obstructions']:print('BLOCKED',r,flush=True)
