from pathlib import Path
import sys,json,time
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,cv2,shapely
from shapely.geometry import Polygon,mapping,shape
D=W/'v24_37';rows=json.loads((D/'Source_Scan_Index.json').read_text());support=np.load(D/'Quality_Raster.npz');lo=support['lo'];hi=support['hi'];raw=support['raw'];density=np.zeros(raw.shape,np.float32);stats={};sample={};badcount={}
for j,r in enumerate(rows):
 a=np.load(D/r['file']);t=a['v'][a['f']];e=np.max(np.linalg.norm(t-np.roll(t,1,axis=1),axis=2),axis=1);cross=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1);aspect=e**2/np.maximum(cross,1e-15);good=(e<3)&(aspect<50)&(cross>1e-7);q=t.mean(1)[:,:2];xy=np.rint(q).astype(int)-lo;inside=(xy[:,0]>=0)&(xy[:,1]>=0)&(xy[:,0]<raw.shape[1])&(xy[:,1]<raw.shape[0]);sel=inside&good;np.add.at(density,(xy[sel,1],xy[sel,0]),1)
 cat='PTJIA6'if r['name'].startswith('V24_36')else'MB7'if r['name'].startswith('V24_34')else'Original'
 sample.setdefault(cat,[]).extend(e[::10]);badcount[cat]=badcount.get(cat,0)+int((~good).sum())
 if j%500==0:print('DENSITY',j,len(rows),flush=True)
smooth=cv2.boxFilter(density,-1,(5,5),normalize=False);dense=(smooth>=30).astype(np.uint8)
# Supported geometry is necessary but not sufficient: large extrapolated sheets
# have almost no small reliable triangles and are removed by local density.
candidate=dense&cv2.morphologyEx(raw,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8));candidate=cv2.morphologyEx(candidate,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
n,lab,cc,cents=cv2.connectedComponentsWithStats(candidate,8);order=np.argsort(cc[1:,4])[::-1]+1;keep=(lab==order[0]).astype(np.uint8)
# Keep complete original reconstructed architectural coverage, which is an
# intentional low-triangle native model rather than a photogrammetric skirt.
core=shape(json.loads((W/'v14/Merge_Boundary_LOCAL.json').read_text()))
for p in ([core]if core.geom_type=='Polygon'else core.geoms):
 xy=np.rint(np.array(p.exterior.coords)-lo).astype(np.int32);cv2.fillPoly(keep,[xy],1)
contours,_=cv2.findContours(keep,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);cv2.drawContours(keep,contours,-1,1,cv2.FILLED)
expanded=cv2.dilate(keep,np.ones((5,5),np.uint8));contours,_=cv2.findContours(expanded,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);polys=[]
for co in contours:
 xy=co[:,0,:].astype(float)+lo
 if len(xy)>2:polys.append(Polygon(xy).buffer(0))
g=shapely.union_all(polys).buffer(.6).simplify(.22,preserve_topology=True)
(D/'Complete_Scan_Retention.geojson').write_text(json.dumps(mapping(g)));np.savez_compressed(D/'Final_Quality_Raster.npz',lo=lo,hi=hi,density=density,smooth=smooth,raw=raw,dense=dense,keep=expanded)
report={'method':'One coherent supported and locally detailed block; 1m cells; >=30 reliable triangle centroids in 5x5m; reliable max edge <3m and aspect <50; 1m seam closing; no erosion; keep native architectural core; 2.6m feature margin; no invented fill geometry','quality_edge_sample_percentiles':{k:np.percentile(v,[0,25,50,75,90,95,99,99.9,100]).tolist()for k,v in sample.items()},'low_quality_triangles_by_source':badcount,'candidate_components':n-1,'candidate_largest_areas_m2':[int(cc[i,4])for i in order[:10]],'kept_plan_area_m2':g.area,'core_area_m2':core.area,'preserve_native_architecture':True}
(D/'Quality_Plan.json').write_text(json.dumps(report,indent=2));print('FINAL_RETENTION',report,flush=True)
