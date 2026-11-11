"""Only close the actual 150 mm void beneath F1 bay under-window walls.

Reuses downward horizontal source faces at Z=-.45; no invented XY footprint.
Does not install or save a Blender model.
"""
from pathlib import Path
import sys,json
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W))
from v26_2_common import *
import v26_2_common as C
BASE=W/'v26_8_windows';D=BASE/'Foot_Closure';D.mkdir(exist_ok=True);C.D=D
FD=W/'v26_7/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';a=np.load(FD/J[HN]['file']);house=solid(a['v'],a['f'])
t=a['v'][a['f']];n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ln=np.linalg.norm(n,axis=1);c=t.mean(1);floor=-.44999998807907104;court=-.6000000238418579
sel=(n[:,2]<-.999999*ln)&(np.ptp(t[:,:,2],axis=1)<1e-8)&(abs(c[:,2]-floor)<1e-7)&(c[:,1]>.78)&(c[:,1]<2.215)&((c[:,0]<4.14)|(c[:,0]>8.86))
faces=[];parts=[]
for tr in t[sel]:
 q=tr.copy();q[:,2]=floor+.0001
 m=extrude_tri(q,2,court)
 if m is not None:parts.append(m);faces.append(tr.tolist())
assert parts
closure=union(parts).simplify(1e-6);row,closure=export('V26_8_F1_Bay_Underwall_Foot_Closure',finish(closure,'M_Stone','Original stone underwindow wall foot closure'),'Only original downward bay wall face footprint extended 150 mm to inherited courtyard datum; local model gap closure, not new site measurement')
# Exclude any occupied original volume. Retain a small 0.1 mm mating overlap
# to fuse robustly with the main house during parent preparation.
new=closure-house
out={'source_sha256':'ae36eb7abde8241465d4d6707fa19c8a9ccd74aaebc025565f2843ee9be5711e','operation':'optional_boolean_add_to_main_house','row':row,'source_downward_faces':faces,'source_face_count':len(faces),'source_bottom_world_z_m':floor,'court_top_world_z_m':court,'nominal_depth_m':floor-court,'mating_overlap_m':.0001,'added_empty_volume_m3':new.volume(),'bounds_m':list(closure.bounding_box()),'evidence':{'geometry':'Native source house ray X2,Y1.0/1.1/1.17 has wall bottom -.45; ground ray Y.95 has courtyard top -.60; ground under Y1.1/1.17 removed by the building footprint. Inner room slab Y1.23 spans -.60..-.45.','photograph_status':'Supplied real entrance image does not show the complete foot. This closes a demonstrated model void using existing floor levels, without claiming surveyed footing dimensions.','protected':'All XY footprints, 30 cm sill above room floor, all glass, gate/ramp and other site masonry unchanged.'}}
(BASE/'Foot_Closure_Recipe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
print('F1_FOOT_CLOSURE',len(faces),row['triangles'],row['volume_m3'],row['closed_components'],flush=True)
