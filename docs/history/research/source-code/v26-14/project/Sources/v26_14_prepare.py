"""Join the actual L-return faces at four WC entrances, preserving openings."""
from v26_2_common import *
import v26_2_common as C
D=W/'v26_14';C.D=D;J=json.loads((D/'Source_Index.json').read_text('utf8'));r=next(r for r in J['objects']if r['name']=='V26_3_House_Connected_Walls_And_Stairs');a=np.load(D/r['file']);original=tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],r['name']);house=original
assert r['file'].startswith('Source_')and r['file']!=r['name']+'.npz','Source/output geometry must be separate'
floors=[-.44999998807907104,3.450024366378784,7.050000190734863];ceil=[3.319999933242798,6.920000076293945,10.220000267028809];patches=[];heads=[];scope=[]
for fl,side in [(0,'L'),(1,'L'),(1,'R'),(2,'R')]:
 # Values are existing native finished planes. Fit the end of the front
 # crosswall to the exposed face of the perpendicular door partition.
 x0,x1=(2.190000057220459,2.2899999618530273)if side=='L'else(10.710000038146973,10.8100004196167)
 y0,y1=7.179999828338623,7.429999828338623
 patch=finish(cube([x0,y0,floors[fl]],[x1,y1,ceil[fl]]),'M_Wall_Interior','WC front wall end aligns with existing finished door return plane')
 added=(patch-house).volume();house+=patch;scope.append(patch)
 patches.append({'floor':fl+1,'side':side,'bounds_m':[[x0,y0,floors[fl]],[x1,y1,ceil[fl]]],'adjacent_finished_x_m':x1 if side=='L'else x0,'previous_front_end_x_m':2.200000047683716 if side=='L'else 10.800000190734863,'front_wall_y_m':y0,'door_start_y_m':7.649999618530273,'added_m3':added})
 # Previous beam repair restored the crossbeam but left a120mm-long missing
 # partition head behind it. Complete the existing180mm side-wall bearing
 # all the way to its native ceiling; the door top is well below this seat.
 hx0,hx1=(2.109999895095825,2.2899999618530273)if side=='L'else(10.710000038146973,10.890000343322754)
 hz=[3.0399999618530273,6.639999866485596,9.9399995803833][fl]
 seat=finish(cube([hx0,7.419999599456787,hz],[hx1,7.650099754333496,ceil[fl]]),'M_Wall_Interior','Complete existing180mm partition head behind the restored beam; no stepped void')
 added=(seat-house).volume();house+=seat;scope.append(seat);heads.append({'floor':fl+1,'side':side,'bounds_m':[[hx0,7.419999599456787,hz],[hx1,7.650099754333496,ceil[fl]]],'added_m3':added})
row,house=export(r['name'],house,'Align four perpendicular WC front-wall ends with the actual door-wall finish; remove the90mm step by a bonded local solid return')
out=np.load(D/row['file']);v,f=out['v'],out['f'];tr=v[f];area=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1)/2;edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),1);_,counts=np.unique(edges,axis=0,return_counts=True)
assert np.all(counts==2)and area.min()>1e-18 and len(house.decompose())==1,(area.min(),int((counts!=2).sum()),len(house.decompose()))
proof={'cause':'The original L-return ended the front crosswall atX2.20/10.80 but the perpendicular door wall face wasX2.29/10.71. A90mm lateral offset remained after the former column-block trimming. Above the beam soffit, that trimming also left a120mm-long partition-head void betweenY7.43and7.55. The later crossbeam repair did not complete this side-wall bearing. Both are native geometry, not texture or shadow.','patches':patches,'head_seats':heads,'method':'Bonded local wall-end extension and complete existing180mm partition head up to its native ceiling. No overlay planes or global wall movement. Door seats, leaves, floor and ceiling levels unchanged.','outside_added_m3':max(0.,((house-original)-union(scope)).volume()),'outside_removed_m3':max(0.,(original-house).volume()),'connected_shells':len(house.decompose()),'native_edge_two_faces':bool(np.all(counts==2)),'minimum_area_m2':float(area.min()),'source':J['model'],'source_sha256':J['sha256'],'dimensions':'Native model and earlier supplied reference photograph fit; not new field measurements'}
assert proof['outside_added_m3']<1e-8 and proof['outside_removed_m3']<1e-8,proof
(D/'Prepared.json').write_text(json.dumps({'objects':[row],'proof':proof},ensure_ascii=False,indent=2),'utf8');print('PREPARED',len(patches),'ADDED',sum(p['added_m3']for p in patches),'TRIANGLES',len(f),flush=True)
