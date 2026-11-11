"""Independent V20 saved-cache check; never writes native model or delivery caches."""
import sys,json,math
from pathlib import Path
W=Path(__file__).parent.parent;D=Path(__file__).parent
sys.path[:0]=[str(W/p) for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
B=Path('E:/jz/JIA/Rebuild_V20');I={r['name']:r for r in json.loads((B/'02_Data/Native_Readback_Index_V20.json').read_text(encoding='utf8'))}
dd={}
def dat(n):
 if n not in dd:
  z=np.load(B/'02_Data'/I[n]['file']);dd[n]={k:z[k] for k in z.files}
 return dd[n]
def sol(n):
 d=dat(n);v=d['vertices'];f=d['faces'];vv,ii=np.unique(np.round(v,10),axis=0,return_inverse=True);a=mf.Manifold(mf.Mesh64(vv,ii[f].astype(np.uint64)));assert a.status()==mf.Error.NoError,(n,a.status());return a
def heights(n,p):
 d=dat(n);t=d['vertices'][d['faces']];xy=t[:,:,:2];p=np.array(p);mask=(xy.min(1)<=p+1e-8).all(1)&(xy.max(1)>=p-1e-8).all(1)
 t=t[mask];vals=[]
 if not len(t):return vals
 aa=t[:,0,:2];u=t[:,1,:2]-aa;v=t[:,2,:2]-aa;det=u[:,0]*v[:,1]-u[:,1]*v[:,0];ids=np.flatnonzero(abs(det)>1e-11)
 for j in ids:
  q=p-aa[j];s=(q[0]*v[j,1]-q[1]*v[j,0])/det[j];r=(u[j,0]*q[1]-u[j,1]*q[0])/det[j]
  if s>=-1e-7 and r>=-1e-7 and s+r<=1+1e-7:vals.append(float(t[j,0,2]+s*(t[j,1,2]-t[j,0,2])+r*(t[j,2,2]-t[j,0,2])))
 return vals
old='SITE_V16_SEALED_OUTER_WALL_DRAIN_AND_ROAD_TIE';new='SITE_V20_STORAGE_FRONT_GUTTER_AND_ROAD_SHOULDER';scans=[n for n in I if n.startswith('SITE_V14_ORIGINAL_EXTERIOR')]
report={'geometry_source':'Saved V20 native readback cache','status':'REVIEW_IN_PROGRESS','station_tests':[]}
for x in np.arange(13.55,20.10,.45):
 for d in [.11,.21,.32,.43,1.05,1.075]:
  p=[float(x),-17.04-d];hh=heights(new,p);zh=max(hh) if hh else None
  oldh=[z for z in heights(old,p) if -5.0<z<-2.0]
  sourceh={n:[z for z in heights(n,p) if -5.0<z<-2.0] for n in scans};sourceh={n:zs for n,zs in sourceh.items() if zs}
  report['station_tests'].append({'xy':p,'offset_from_new_stone_m':d,'new_surface_z':zh,'retained_old_tie_z':oldh,'retained_scan_z':sourceh})
tie=sol(old);channeltests=[]
for x in [13.8,15.0,16.5,18.0,19.0,20.0]:
 zz=heights(new,[x,-17.2]);floor=max(zz);cu=mf.Manifold.cube([.30,.20,.235]).translate([x-.15,-17.37,floor+.012]);a=tie^cu
 channeltests.append({'x':x,'cavity_box_volume_m3':cu.volume(),'old_tie_intrusion_m3':a.volume()})
report['channel_cavity_intersections']=channeltests
report['retained_scan_channel_obstructions']=[r for r in report['station_tests'] if .10<r['offset_from_new_stone_m']<.34 and r['new_surface_z'] is not None and any(z>r['new_surface_z']+.04 for hh in r['retained_scan_z'].values() for z in hh)]
report['road_outer_seam_vertical_steps']=[{**r,'max_z_difference_m':max([abs(z-r['new_surface_z']) for hh in r['retained_scan_z'].values() for z in hh],default=None)} for r in report['station_tests'] if abs(r['offset_from_new_stone_m']-1.05)<1e-6 and r['new_surface_z'] is not None]
if any(r['old_tie_intrusion_m3']>1e-6 for r in channeltests) or report['retained_scan_channel_obstructions']:report['status']='MAJOR_CHANNEL_CAVITY_OCCUPIED_BY_RETAINED_TIE_OR_SCAN'
else:report['status']='PASS_NO_CHANNEL_OBSTRUCTION_FOUND'
(D/'Saved_V20_Seam_Audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(report['status'],flush=True);print(json.dumps(channeltests),flush=True);print('scan obstruction stations',len(report['retained_scan_channel_obstructions']),flush=True);print('seam steps',[(r['xy'][0],r['max_z_difference_m']) for r in report['road_outer_seam_vertical_steps']],flush=True)
