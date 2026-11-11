"""Record the final images manually reviewed in the root task, with artifact hashes."""
import json,hashlib
from pathlib import Path
O=Path(r'E:\jz\JIA\Rebuild_V12')
def read(p):return json.loads(p.read_text(encoding='utf8'))
N=read(O/'06_Report/Native_Assembly_QA.json');X=read(O/'06_Report/Modeled_Exchange_QA.json');J=read(O/'07_Reference/v12_terrain/Terrain_Seam_Continuity_QA.json');assert N['status']==X['status']==J['status']=='PASS'
observations={
 'V12_Whole_Site':'Rebuilt ground is continuous; artificial raised panel-edge shadows eliminated; no source photogrammetric floating skins visible.',
 'V12_Architecture':'Architectural masses and roof overlaps retained; modeled enclosure complete in this view; western marked clearance zone retains ground only.',
 'V12_Top_Roofs':'Roof positions and asymmetric kitchen roof retained; pavilion roof remains inside courtyard enclosure; western clearance zone has no sheds.',
 'V12_Kitchen_Timber':'Paired-octagonal window lattice, narrow transoms and mirrored door-leaf molding visible; no coplanar lattice patches.',
 'V12_Kitchen_Truss':'Exposed cross beams, round longitudinal purlins, dense rafters and three-blade fan visible; actual complete roof retained.',
 'V12_Kitchen_Interior_Front':'Separate wide upper fret band and narrow lower transoms, central conduit and exposed timber visible.',
 'V12_Entrance_Ramp':'Entrance scored apron joins the approach road; raised earth wedge and tiny earth triangle removed; geometry seam QA verifies all four edges.',
 'V12_Screenwall':'Upturned ends, ridge ornaments and visible lotus tile-end disks present; original wall and roof footprints retained.'
}
rows=[]
for name,note in observations.items():
 p=O/'06_Report'/(name+'.png');rows.append(dict(file=p.relative_to(O).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),observation=note,manual_review='Root task viewed final PNG with view_image'))
Q=dict(status='PASS',primary_sha256=N['sha256'],glb_sha256=X['glb_sha256'],fbx_sha256=X['fbx_sha256'],images=rows,terrain_seams=J['after'],photogrammetry_in_primary=0,appearance='Photo-referenced modeled PBR microtextures; calibrated weathering and physical surface capture remain unmeasured',limits='Visual and geometry checks confirm this modeled revision. Site dimensions and hidden portions are reference-fitted; this is not field survey or construction certification, and UE5 interactions have not been playtested.')
(O/'06_Report/Visual_Review_V12.json').write_text(json.dumps(Q,ensure_ascii=False,indent=2),encoding='utf8');print('Final visual review recorded',len(rows),'images',flush=True)
