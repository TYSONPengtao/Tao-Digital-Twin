"""Frozen-geometry hole registry; does not regenerate or write Mutation.json."""
import sys,json,hashlib,math
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
import export_v5 as ex
O=Path(__file__).parent;P=O/'Mutation.json';M=json.loads(P.read_text(encoding='utf8'))
E={e['name']:e for e in M['replace']+M['add']}
chains={'SITE_COURTYARD_WEST_TILE_WALL':[[0,1.9],[0,-10.7],[4.9,-11.7]],'SITE_GATE_EAST_FLANK':[[8.3,-11.7],[M['kitchen_gable_ornament_stop_x'],-11.7]]}
def body(g):
    v,fs,_,_=ex.solid_data(g);tr=[]
    for f in fs:
        tr += [f] if len(f)==3 else [[f[i] for i in t] for t in ex.triangulate(v[f])]
    a=mf.Manifold(mf.Mesh64(v.astype(np.float64),np.asarray(tr,dtype=np.uint64)));assert a.status()==mf.Error.NoError;return a
probes=[]
for r in M['layer_dimensions']:
    chain=r['chain'];j=r['segment'];p=np.array(chains[chain]);a=p[j];b=p[j+1];L=float(np.linalg.norm(b-a));u=(b-a)/L;n=np.array([-u[1],u[0]])
    name=chain+'_V10_OPEN_FLOWER_BRICKS';node=mf.Manifold.batch_boolean([body(pp['geometry']) for pp in E[name]['parts']],mf.OpType.Add)
    for start in np.arange(0,L-.08,.5):
        end=min(float(start+.5),L)
        for s in np.arange(start+.0625,end-.04,.125):
            if s-.0525<start+.008 or s+.0525>end-.008:continue
            z=r['crown_start_m']+(r['crown_end_m']-r['crown_start_m'])*s/L+.2425
            pt=np.r_[a+u*s,z];n3=np.r_[n,0];drill=mf.Manifold.cylinder(.10,.006,.006,32)
            R=np.column_stack([np.r_[u,0],[0,0,-1],n3]);T=np.column_stack([R,pt-.05*n3]);drill=drill.transform(T)
            iv=(node^drill).volume()
            assert iv<1e-12,(name,j,s,iv)
            probes.append(dict(node=name,segment=j,station_local_m=float(s),segment_length_m=L,point_local_m=pt.tolist(),normal_local=n3.tolist(),hole_width_m=.105,hole_height_m=.105,through_depth_m=.068,actual_frozen_flower_node_drill_intersection_volume_m3=iv,drill_diameter_m=.012,drill_depth_m=.10,distance_to_segment_start_m=float(s),distance_to_segment_end_m=float(L-s)))
selected=[]
for chain,pts in chains.items():
    for j in range(len(pts)-1):
        qq=[p for p in probes if p['node']==chain+'_V10_OPEN_FLOWER_BRICKS' and p['segment']==j]
        for p in qq[:2]+qq[-2:]:
            if p not in selected:selected.append(p)
doc=dict(status='PASS',mutation_sha256=hashlib.sha256(P.read_bytes()).hexdigest(),count=len(probes),geometry_unchanged=True,nominal_hole_width_height_m=.105,probe_diameter_m=.012,probe_depth_m=.10,all_actual_frozen_flower_node_center_drills_clear=True,all_holes=probes,nearest_junctions=selected,notes=['Every listed hole passes a12mm-diameter100mm-long Boolean drill through the actual frozen flower lattice node.','Neighborcap/miter/preservedpost occlusion is for the independent reference agent; these probes do not claim that separate test.'])
(O/'All_Actual_Hole_Probes.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf8')
print('actualflowerholes',len(probes),'PASS')
