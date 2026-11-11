from pathlib import Path
import sys,json
W=Path(__file__).parent;sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W/'libs')]
import numpy as np,cv2,shapely
from shapely.geometry import Polygon,LineString,shape,mapping
D=W/'v24_37';a=np.load(D/'Final_Quality_Raster.npz');raw=a['raw'];lo=a['lo'];dense=a['dense'];fraction=cv2.boxFilter(raw.astype(np.float32),-1,(11,11),normalize=True)
backup=D/'Retention_Before_Refine.geojson'
if not backup.exists():backup.write_bytes((D/'Final_Scan_Retention.geojson').read_bytes())
previous=shape(json.loads(backup.read_text()));base=np.zeros(raw.shape,np.uint8)
for p in ([previous]if previous.geom_type=='Polygon'else previous.geoms):cv2.fillPoly(base,[np.rint(np.array(p.exterior.coords)-lo).astype(np.int32)],1)
distance=cv2.distanceTransform(base,cv2.DIST_L2,5)
# Assess completeness only at the outside fringe, preserving interior forest,
# buildings and field evidence even where a human cannot stand on tree sides.
candidate=((base>0)&((distance>=10)|((fraction>=.78)&(dense>0)))).astype(np.uint8);candidate=cv2.morphologyEx(candidate,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8));candidate=cv2.morphologyEx(candidate,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
# Preserve all surveyed road corridors and original architecture even where
# their useful continuous width is smaller than the fringe-cleaning kernel.
for directory in ['v24_34','v24_36']:
 for route in json.loads((W/directory/'Planned_Routes.json').read_text()):
  p=LineString([q[:2]for q in route['points']]).buffer(3.)
  cv2.fillPoly(candidate,[np.rint(np.array(p.exterior.coords)-lo).astype(np.int32)],1)
core=shape(json.loads((W/'v14/Merge_Boundary_LOCAL.json').read_text()))
for p in ([core]if core.geom_type=='Polygon'else core.geoms):cv2.fillPoly(candidate,[np.rint(np.array(p.exterior.coords)-lo).astype(np.int32)],1)
n,lab,stats,cents=cv2.connectedComponentsWithStats(candidate,8);largest=1+np.argmax(stats[1:,4]);candidate=(lab==largest).astype(np.uint8);contours,_=cv2.findContours(candidate,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);cv2.drawContours(candidate,contours,-1,1,cv2.FILLED);candidate=cv2.dilate(candidate,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)));contours,_=cv2.findContours(candidate,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);polys=[]
for co in contours:
 xy=co[:,0,:].astype(float)+lo
 if len(xy)>2:polys.append(Polygon(xy).buffer(0))
mask=shapely.union_all(polys).buffer(.6).simplify(.22,preserve_topology=True);mask=mask.intersection(previous);(D/'Complete_Scan_Retention.geojson').write_text(json.dumps(mapping(mask)));report=json.loads((D/'Quality_Plan.json').read_text());report.update(border_refinement={'outer_fringe_depth_m':10,'support_fraction_in_11m_window':.78,'fringe_minimum_width_m':9,'all_tested_road_corridors_protected_m':3.,'original_architectural_core_protected':True,'new_plan_area_m2':mask.area,'no_geometry_filled':True});(D/'Quality_Plan.json').write_text(json.dumps(report,indent=2));print('REFINED_BORDER',mask.geom_type,mask.area,'previous',previous.area,flush=True)
