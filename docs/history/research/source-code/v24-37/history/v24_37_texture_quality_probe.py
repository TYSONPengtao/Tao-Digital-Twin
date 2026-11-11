from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np
D=W/'v24_37';b=json.loads((D/'Before_Snapshot.json').read_text());rows=json.loads((D/'Final_Scan_Index.json').read_text());stats={};details=[]
def texture_size(mat):
 ns=b['materials'][mat]['shader']['nodes'];ims=[n['image']['name']for n in ns if 'image'in n and n['image']]
 return b['images'][ims[0]]['size']if ims else[0,0]
def density(t,uv,size):
 u=(uv[:,1]-uv[:,0])*size;w=(uv[:,2]-uv[:,0])*size;det=u[:,0]*w[:,1]-u[:,1]*w[:,0];den=np.where(abs(det)>1e-10,det,1);x=t[:,1]-t[:,0];y=t[:,2]-t[:,0];ax=(x*w[:,1,None]-y*u[:,1,None])/den[:,None];ay=(y*u[:,0,None]-x*w[:,0,None])/den[:,None];g00=(ax*ax).sum(1);g11=(ay*ay).sum(1);g01=(ax*ay).sum(1);eig=(g00+g11+np.sqrt((g00-g11)**2+4*g01*g01))/2;d=1/np.sqrt(np.maximum(eig,1e-20));d[abs(det)<1e-10]=0;return d
for j,r in enumerate(rows):
 a=np.load(D/r['file']);t=a['v'][a['f']];uv=a['uv'];ds=np.zeros(len(t))
 for mi,mat in enumerate(r['materials']):
  sel=a['mi']==mi;sz=texture_size(mat)
  if sel.any():ds[sel]=density(t[sel],uv[sel],np.array(sz))
 cat='PTJIA6'if r['name'].startswith('V24_36')else'MB7'if r['name'].startswith('V24_34')else'Original';stats.setdefault(cat,[]).extend(ds[::10]);details.append({'name':r['name'],'dmin':float(ds.min()),'median':float(np.median(ds)),'below2':int((ds<2).sum()),'below4':int((ds<4).sum()),'faces':len(t),'density_file':'TEX_'+str(j).zfill(4)+'.npz'});np.savez_compressed(D/details[-1]['density_file'],density=ds.astype(np.float32))
 if j%500==0:print('TEXTURE_DENSITY',j,len(rows),flush=True)
out={'sample_density_percentiles_px_per_m':{k:np.percentile(v,[0,.1,1,5,10,25,50,75,90,99,100]).tolist()for k,v in stats.items()},'rows':details};(D/'Texture_Quality_Probe.json').write_text(json.dumps(out,indent=2));print('TEXTURE_STATS',out['sample_density_percentiles_px_per_m'],flush=True)
