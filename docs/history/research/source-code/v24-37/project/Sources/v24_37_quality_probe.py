from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,cv2,shapely
from shapely.geometry import shape,mapping,Polygon
D=W/'v24_37';D.mkdir(exist_ok=True);p=np.load(W/'v24_36/Roam_Ground_Grid.npz')['p'];lo=np.floor(p[:,:2].min(0)).astype(int)-5;hi=np.ceil(p[:,:2].max(0)).astype(int)+5;mask=np.zeros((hi[1]-lo[1]+1,hi[0]-lo[0]+1),np.uint8);xy=np.rint(p[:,:2]).astype(int)-lo;mask[xy[:,1],xy[:,0]]=1;close=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8));n,lab,stats,cents=cv2.connectedComponentsWithStats(close,8);areas=stats[1:,cv2.CC_STAT_AREA];order=np.argsort(areas)[::-1]+1;print('COMPONENTS',n-1,'LARGEST',[(int(i),int(stats[i,4]))for i in order[:12]],flush=True)
# Keep coherent measured surface blocks. Narrow roads remain because no opening
# or erosion is applied. Filled holes define retention bounds only, no geometry
# is invented. Two metres retain real side walls and vegetation features.
keep=np.zeros_like(mask)
for i in order:
 if stats[i,4]<150:continue
 part=(lab==i).astype(np.uint8);contours,hierarchy=cv2.findContours(part,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);cv2.drawContours(keep,contours,-1,1,cv2.FILLED)
expanded=cv2.dilate(keep,np.ones((5,5),np.uint8));contours,_=cv2.findContours(expanded,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);polys=[]
for c in contours:
 xy=c[:,0,:].astype(float)+lo
 if len(xy)>=3:
  pp=Polygon(xy).buffer(0)
  if not pp.is_empty:polys.append(pp)
g=shapely.union_all(polys).buffer(.6);(D/'Complete_Scan_Retention.geojson').write_text(json.dumps(mapping(g)));np.savez_compressed(D/'Quality_Raster.npz',lo=lo,hi=hi,raw=mask,closed=close,keep=expanded);report={'method':'Coherent supported surface footprints, 1m grid, 1m seam closing, no erosion of narrow roads; keep blocks >=150m2, retain adjacent real geometry within 2.6m; no fill geometry','support_points':len(p),'components':n-1,'kept_components':int((areas>=150).sum()),'kept_plan_area_m2':g.area,'largest_component_pixels':int(areas.max()),'preserve_native_architecture':True};(D/'Quality_Plan.json').write_text(json.dumps(report,indent=2));print('QUALITY_KEEP',report,flush=True)
# Coordinates for an image overlay are saved for the independent review plot.
