from pathlib import Path
import sys,json,time
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,cv2
from PIL import Image,ImageDraw
D=W/'v24_37';rows=json.loads((W/'v24_36/Final_Exterior_Index.json').read_text());meta=json.loads((W/'v24_36/Top_Projection.json').read_text());c=meta['center'];width=850.;res=(1700,1134);sx=res[0]/width
counts=np.zeros((res[1],res[0]),np.float32);badcounts=counts.copy();triangles=0;edgehist=[];badtri=[];start=time.perf_counter()
for j,r in enumerate(rows):
 a=np.load(W/'v24_36'/r['file']);t=a['v'][a['f']].astype(float);edge=np.max(np.linalg.norm(t-np.roll(t,1,axis=1),axis=2),axis=1);cross=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1);aspect=edge**2/np.maximum(cross,1e-15);good=(edge<3)&(aspect<50)&(cross>1e-7);q=t.mean(1);px=np.floor((q[:,0]-c[0])*sx+res[0]/2).astype(int);py=np.floor((c[1]-q[:,1])*sx+res[1]/2).astype(int);inside=(px>=0)&(py>=0)&(px<res[0])&(py<res[1]);np.add.at(counts,(py[inside&good],px[inside&good]),1);np.add.at(badcounts,(py[inside&~good],px[inside&~good]),1);edgehist.extend(edge[::10].tolist());triangles+=len(t)
 if not good.all():badtri.append({'name':r['name'],'triangles':len(t),'bad':int((~good).sum()),'bounds':np.array([q[~good].min(0),q[~good].max(0)]).tolist()})
 if j%500==0:print('QUALITY',j,len(rows),'seconds',time.perf_counter()-start,flush=True)
im=Image.open('E:/jz/JIA/Rebuild_V24_36/Reports/V24_36_Context_Top.png').convert('RGB').resize(res);rgb=np.array(im);smooth=cv2.boxFilter(counts,-1,(5,5),normalize=False);sel=smooth<12;rgb[sel]=(rgb[sel]*.35+np.array([120,0,0])*.65).astype(np.uint8);Image.fromarray(rgb).save(D/'Triangle_Density_Review.png');np.savez_compressed(D/'Triangle_Density.npz',good=counts,bad=badcounts,smooth=smooth);out={'triangles':triangles,'sample_edge_percentiles':np.percentile(edgehist,[0,25,50,75,90,95,99,99.9,100]).tolist(),'bad_geometry_sources':badtri};(D/'Triangle_Quality_Analysis.json').write_text(json.dumps(out,indent=2));print('QUALITY_STATS',triangles,out['sample_edge_percentiles'],flush=True)
