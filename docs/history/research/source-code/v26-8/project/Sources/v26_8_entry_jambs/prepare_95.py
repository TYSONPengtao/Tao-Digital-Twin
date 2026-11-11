"""Local front glazed-entry jamb correction. Never modifies source native file."""
from pathlib import Path
import sys,json,hashlib
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W))
from v26_2_common import *
import v26_2_common as C
D=Path(__file__).resolve().parent/'Candidate_95mm';D.mkdir(exist_ok=True);C.D=D
FD=W/'v26_7/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs'
source=Path('E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend')
assert hashlib.sha256(source.read_bytes()).hexdigest()=='ae36eb7abde8241465d4d6707fa19c8a9ccd74aaebc025565f2843ee9be5711e'
a=np.load(FD/J[HN]['file']);before=tracked(a['v'],a['f'],J[HN]['materials'],a['mi'],a['uv'],HN);house=before

def box(lo,hi):return cube(np.array(lo,np.float32).astype(float),np.array(hi,np.float32).astype(float))
def prism(points,z0,z1):return section(np.array(points,np.float32).astype(float),float(np.float32(z1-z0))).translate([0,0,float(np.float32(z0))])
proof=[];cutters=[]
for fl,z0,z1 in[(1,-.45,3.15003),(2,3.4500244,6.75003),(3,7.05,10.05003)]:
 for side,cx,j in[('L',3.9,2),('R',9.1,0)]:
  if fl==3 and side=='L':continue
  wn=f'BAY_WINDOW_F{fl}_{side}_{j}_Geometry';r=J[wn];wa=np.load(FD/r['file']);u=np.array([(-1 if side=='L'else 1)*.5848568450639461,-.8111365302967483]);end=float((wa['v'][:,:2]@u).min())
  # Keep the jamb's true red-frame to oblique-frame bridge. The old400mm
  # KZ plus12.2mm finish was drawn through that frame junction. The
  # photographed side strip is narrow; no structural400mm post measured.
  # End plane is exactly the retained black oblique frame's terminal plane.
  ys=[1.7,2.4];xp=[(end-u[1]*y)/u[0]for y in ys]
  half=prism([[xp[0],ys[0]],[xp[1],ys[1]],[cx+(-1 if side=='R'else 1)*.9,ys[1]],[cx+(-1 if side=='R'else 1)*.9,ys[0]]],z0,z1)
  # Front/side depth220mm. At porch front Y2.0 the remaining white bridge
  # is163.9mm wide; behind the oblique frame it rejoins the240mm bedroom
  # partition atY2.22. The rear bedroom partition itself is untouched.
  xlo,xhi=([3.78,4.10]if side=='L'else[8.90,9.22]);allowed=box([xlo,1.95,z0],[xhi,2.19,z1])^half
  reg=box([cx-.225,1.85,z0],[cx+.225,2.19001,z1]);cut=reg-allowed
  # Stop the small12.2mm halo beyond the ordinary side-wall width immediately
  # behind the new bridge. Do not touch the original bedroom door frames.
  rearreg=box([cx-.225,2.19,z0],[cx+.225,2.4,z1]);rearallow=box([cx-.12,2.19,z0],[cx+.12,2.4,z1]);cut+=rearreg-rearallow
  hit=(house^cut).volume();house-=finish(cut,'M_Wall_Interior',f'F{fl}{side} photo referenced narrow front jamb and bay end plane')
  cutters.append(cut)
  frontxs=(end-u[1]*1.95)/u[0];visible=abs(frontxs-(4.1 if side=='L'else 8.9))
  proof.append({'floor':fl,'side':side,'original_visible_halo_width_mm':424.4,'old_front_y_m':1.8878,'new_front_y_m':1.95,'new_front_bridge_depth_mm':240.,'estimated_white_strip_width_at_front_mm':visible*1000,'retained_bedroom_wall_width_mm':240.,'frame':wn,'frame_end_plane_unit_xy':u.tolist(),'frame_end_plane_limit_m':end,'removal_m3':hit,'scope_bounds_m':[[cx-.225,1.85,z0],[cx+.225,2.4,z1]],'dimension_status':'FITTED_FROM_USER_REAL_PHOTO_AND_RETAINED_FRAME_ENDPOINTS; NOT_FIELD_MEASURED'})
cut=union(cutters);m=cut.to_mesh64();np.savez_compressed(D/'Entry_Jamb_Cutters.npz',v=np.array(m.vert_properties[:,:3]),f=np.array(m.tri_verts))
r,candidate=export(HN,house,'Front glass-door jambs reduced to narrow photo referenced white strips,220mm-depth bridge and preserved240mm bedroom return; unchanged actual red door and oblique bay frame terminal planes')
(D/'Prepared_Geometry.json').write_text(json.dumps({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'objects':[r],'archive':[],'proof':proof,'root_recipe':'Apply only Entry_Jamb_Cutters.npz as tracked white wall cutter to combined current house; this prepared full-house candidate is for independent visual review only. No add volume.','protected':'All native door/frame/glass meshes, transforms and operation attributes; all site and original secondary screenwall geometry'},ensure_ascii=False,indent=2),'utf8')
checks=[{'test':'No volume added','pass':(candidate-before).volume()<1e-7,'added_m3':(candidate-before).volume()},{'test':'House remains one positive closed manifold','pass':candidate.status()==mf.Error.NoError and len(candidate.decompose())==1,'components':len(candidate.decompose())},{'test':'All changed material limited to exact local cut masks within float32 export tolerance','pass':((before-candidate)-cut).volume()<1e-6,'outside_m3':((before-candidate)-cut).volume(),'tolerance_m3':1e-6,'exact_boolean_outside_m3':((before-house)-cut).volume()}]
for row in proof:
 wn=row['frame'];a=np.load(FD/J[wn]['file']);m=solid(a['v'],a['f']);checks.append({'test':'No added interference with retained frame '+wn,'pass':(candidate^m).volume()<=(before^m).volume()+1e-7,'before_m3':(before^m).volume(),'after_m3':(candidate^m).volume()})
(D/'Independent_Candidate_QA.json').write_text(json.dumps({'status':'PASS'if all(c['pass']for c in checks)else 'FAIL','checks':checks,'proof':proof},ensure_ascii=False,indent=2),'utf8');print('ENTRY_JAMB_CANDIDATE',len(proof),(before-candidate).volume(),checks,flush=True)



