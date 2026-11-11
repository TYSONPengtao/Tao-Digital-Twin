import sys,json
from pathlib import Path
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'libs'),str(W/'geomlibs')]
import numpy as np
D=W/'v24_10';d=np.load(D/'AsBuilt_All_LOCAL.npz');v=d['v'].astype(float);t=v[d['f']];p=t.mean(1);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);a=np.linalg.norm(n,axis=1)/2;n/=np.maximum(a*2,1e-20)[:,None];n[n[:,2]<0]*=-1
out={}
for side,sign in [('south',1),('north',-1)]:
 mask=(p[:,0]>13.7)&(p[:,0]<18.5)&(p[:,1]>-16.0)&(p[:,1]<-9.4)&(p[:,2]>2.6)&(p[:,2]<5.4)&(n[:,1]*sign<-.24)&(n[:,2]>.60)&(abs(n[:,0])<.32)
 pp=p[mask];aa=a[mask];xy=np.c_[pp[:,:2],np.ones(len(pp))];co=np.linalg.lstsq(xy*np.sqrt(aa[:,None]),pp[:,2]*np.sqrt(aa),rcond=None)[0]
 for _ in range(15):
  res=pp[:,2]-xy@co;ok=abs(res)<min(.18,max(.05,float(np.quantile(abs(res),.75))));co=np.linalg.lstsq(xy[ok]*np.sqrt(aa[ok,None]),pp[ok,2]*np.sqrt(aa[ok]),rcond=None)[0]
 out[side]={'plane_z_ax_by_c':co.tolist(),'samples':len(pp),'inliers':int(ok.sum()),'weighted_rms_m':float(np.sqrt(np.average(res[ok]**2,weights=aa[ok]))),'area_m2':float(aa[ok].sum())}
for label,xx,yy in [('gallery',[13.5,18.5],[-16.0,-14.0]),('inner_room',[13.8,18.4],[-14.5,-10.0]),('entry',[11.5,14],[-16.8,-14.8])]:
 ma=(p[:,0]>xx[0])&(p[:,0]<xx[1])&(p[:,1]>yy[0])&(p[:,1]<yy[1])&(p[:,2]>-.8)&(p[:,2]<.8)&(n[:,2]>.92)
 hh,bins=np.histogram(p[ma,2],bins=np.arange(-.8,.81,.05),weights=a[ma]);ii=np.argsort(hh)[-7:][::-1]
 out[label+'_floor_modes']=[{'z':float((bins[i]+bins[i+1])/2),'area_m2':float(hh[i])}for i in ii]
for x in [11.8,12.4,13.0,13.3]:
 ma=(abs(v[:,0]-x)<.16)&(v[:,1]>-17.25)&(v[:,1]<-16.15)&(v[:,2]>1)&(v[:,2]<4)
 out['wall_tip_at_'+str(x)]={'vertices':int(ma.sum()),'z_q':np.quantile(v[ma,2],[.1,.5,.9,.99,1]).tolist()if ma.any()else[]}
out['ridge_intersection_y']={str(x):float(-(np.array(out['north']['plane_z_ax_by_c'])-np.array(out['south']['plane_z_ax_by_c']))[[0,2]]@[x,1]/(np.array(out['north']['plane_z_ax_by_c'])-np.array(out['south']['plane_z_ax_by_c']))[1])for x in[13.35,18.7]}
(D/'AsBuilt_Fit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out,ensure_ascii=False),flush=True)
