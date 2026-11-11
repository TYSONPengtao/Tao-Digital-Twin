"""Frozen V11 west corner solids audit. All baseline files stay read-only."""
import sys,json,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
import export_v5 as ex
O=Path(__file__).parent
SP=Path(r'E:/jz/JIA/Rebuild_V10_Hybrid/08_Editable_Source/05_Intermediate/Architecture_Scene.json')
srcbytes=SP.read_bytes();S=json.loads(srcbytes);E={e['name']:e for e in S['elements']}
P=O/'Mutation.json';mutbytes=P.read_bytes();M=json.loads(mutbytes);N={e['name']:e for e in M['replace']+M['add']}
checks=[]
def check(name,ok,**kw):
    checks.append(dict(name=name,passed=bool(ok),**kw))
    if not ok:raise AssertionError((name,kw))
def body(g):
    v,fs,_,_=ex.solid_data(g);tr=[]
    for f in fs:tr.extend([f] if len(f)==3 else [[f[i] for i in t] for t in ex.triangulate(v[f])])
    sol=mf.Manifold(mf.Mesh64(v.astype(np.float64),np.asarray(tr,np.uint64)))
    assert sol.status()==mf.Error.NoError and sol.volume()>1e-12
    return sol,v
check('baseline_sha_matches',M['source_scene_sha256']==hashlib.sha256(srcbytes).hexdigest())
check('exactly_only_21_requested_west_wall_nodes',len(N)==21 and all(n.startswith('SITE_COURTYARD_WEST') or n.startswith('SITE_WEST_TILE_WALL_PANEL_') for n in N))
for n in N:check('old_node_fingerprint_'+n,M['old_node_sha256'][n]==hashlib.sha256(json.dumps(E[n],sort_keys=True,separators=(',',':')).encode()).hexdigest())
route=np.array(M['new_route_local_m']);u=np.diff(route,axis=0);u/=np.linalg.norm(u,axis=1)[:,None]
check('user_required_corner_angle_90deg',abs(float(u[0]@u[1]))<1e-12)
check('building_and_gate_jamb_endpoints_unchanged',route[0].tolist()==M['old_route_local_m'][0] and route[-1].tolist()==M['old_route_local_m'][-1])
query=[];plans=[];gate=mf.Manifold.cube([2.6,.5,2.49]).translate([5.3,-11.95,-.45]);opening=[]
for n,e in N.items():
    for i,p in enumerate(e['parts']):
        sol,v=body(p['geometry']);lo=v.min(0);hi=v.max(0);query.append((n,i,sol,lo,hi))
        if n=='SITE_COURTYARD_WEST_TILE_WALL':plans.append(Polygon(v[:,:2]).convex_hull)
        if hi[0]>5.3 and lo[0]<7.9 and hi[1]>-11.95 and lo[1]<-11.45 and (sol^gate).volume()>1e-10:opening.append((n,i))
check('doorway_2_6m_not_entered',not opening,occupied=opening)
core=unary_union(plans)
expected=LineString(route).buffer(.125,cap_style=2,join_style=2)
check('complete_250mm_core_footprint_without_corner_gap',core.symmetric_difference(expected).area<1e-9,residual_m2=core.symmetric_difference(expected).area)
# Shared level collar top/bottom is exact at the 45 degree common face.
corner=[0,-11.7]
for n in ['SITE_COURTYARD_WEST_TILE_WALL','SITE_COURTYARD_WEST_TILE_WALL_TILE_COPING','SITE_COURTYARD_WEST_TILE_WALL_V10_OPEN_FLOWER_BRICKS','SITE_COURTYARD_WEST_TILE_WALL_V10_RIDGE_SEAT_AND_CAP','SITE_COURTYARD_WEST_WHITE_INSIDE']:
    qq=[r for r in query if r[0]==n and r[4][0]>=-.251 and r[3][0]<=.251 and r[4][1]>=-11.951 and r[3][1]<=-11.449]
    overlaps=[]
    for k,a in enumerate(qq):
        for b in qq[k+1:]:
            if np.any(np.minimum(a[4],b[4])-np.maximum(a[3],b[3])<=1e-10):continue
            vol=(a[2]^b[2]).volume()
            if vol>1e-10:overlaps.append(dict(a=a[1],b=b[1],volume_m3=vol))
    check('no_duplicate_overlapping_corner_bodies_'+n,not overlaps,positive=overlaps)
# Every frozen floral aperture is drilled through all new parts and retained jamb.
for host in ['SITE_INNER_STONE_GATEHOUSE','KZ_1_1_F1']:
    for i,p in enumerate(E[host]['parts'] if 'parts' in E[host] else S['definitions'][E[host]['definition']]['parts']):
        v,fs=ex.world_part(p,E[host]);g=dict(type='polyhedron',vertices=v.tolist(),faces=fs);sol,v=body(g);query.append((host,i,sol,v.min(0),v.max(0)))
lo=np.array([r[3] for r in query]);hi=np.array([r[4] for r in query])
HP=O/'All_Actual_Hole_Probes.json';H=json.loads(HP.read_bytes());bad=[]
check('aperture_registry_matches_frozen_mutation',H['mutation_sha256']==hashlib.sha256(mutbytes).hexdigest())
for h in H['all_holes']:
    c=np.array(h['point_local_m']);normal=np.array(h['normal_local']);z=np.array([0,0,1]);tangent=np.cross(normal,z)
    drill=mf.Manifold.cylinder(.10,.006,.006,24).transform(np.column_stack([tangent,z,normal,c-.05*normal]))
    dmin=c-.054;dmax=c+.054;ids=np.flatnonzero(np.all(np.minimum(hi,dmax)-np.maximum(lo,dmin)>1e-10,axis=1))
    for j in ids:
        r=query[j];volume=(r[2]^drill).volume()
        if volume>1e-12:bad.append(dict(hole=h['point_local_m'],host=r[0],part=r[1],volume_m3=volume))
check('all_146_actual_apertures_clear_full_100mm_normal_depth',len(H['all_holes'])==146 and not bad,holes=len(H['all_holes']),blockers=bad)
check('baseline_and_frozen_mutation_stay_unchanged',SP.read_bytes()==srcbytes and P.read_bytes()==mutbytes)
result=dict(status='PASS',checks=checks,checks_count=len(checks),changed_nodes=len(N),closed_parts=sum(len(e['parts']) for e in N.values()),actual_apertures_tested=len(H['all_holes']),old_route_local_m=M['old_route_local_m'],new_route_local_m=M['new_route_local_m'],source_sha256=M['source_scene_sha256'],mutation_sha256=hashlib.sha256(mutbytes).hexdigest(),hole_blockers=bad,not_field_survey=True)
(O/'Frozen_Corner_Connection_QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False))
