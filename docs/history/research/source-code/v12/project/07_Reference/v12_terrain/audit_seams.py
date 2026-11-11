import sys,json,collections,math,hashlib
from pathlib import Path
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/x) for x in ['np1','geomlibs','libs']]
import numpy as np,shapely
from shapely.geometry import shape,Point,LineString
D=Path(__file__).parent;Domain=shape(json.loads((D/'Terrain_Domain.json').read_text())['domain']);edge=Domain.boundary

def audit(file):
 m=json.loads(file.read_text());tr=[];owner=[];borders=[];names=[]
 for j,e in enumerate(m['add']):
  names.append(e['name']);g=e['parts'][0]['geometry'];v=np.array(g['vertices']);N=len(v)//2;fs=[f for f in g['faces'] if len(f)==3 and max(f)<N];ec=collections.Counter(tuple(sorted((a,b))) for f in fs for a,b in zip(f,f[1:]+f[:1]));tr.extend(v[fs]);owner.extend([j]*len(fs));borders.extend([(j,v[list(ee)]) for ee,n in ec.items() if n==1])
 tr=np.array(tr);owner=np.array(owner);area=np.abs(np.cross(tr[:,1,:2]-tr[:,0,:2],tr[:,2,:2]-tr[:,0,:2]));longest=np.max(np.stack([np.linalg.norm(tr[:,1,:2]-tr[:,0,:2],axis=1),np.linalg.norm(tr[:,2,:2]-tr[:,1,:2],axis=1),np.linalg.norm(tr[:,0,:2]-tr[:,2,:2],axis=1)]),axis=0);stable=area/np.maximum(longest,1e-30)>1e-5;discarded=int((~stable).sum());tr=tr[stable];owner=owner[stable];pg=shapely.polygons(tr[:,:,:2]);tree=shapely.STRtree(pg);footprints=[shapely.union_all(pg[owner==j]) for j in range(len(names))];internal_caps=[];results=[];unmatched=[];rampcases=[];rampid=names.index('SITE_V12_OUTER_GATE_SCORED_CONCRETE_RAMP');tol=2e-6
 def z_at(t,q):
  a,b,c=t;v0=b[:2]-a[:2];v1=c[:2]-a[:2];v2=q-a[:2];den=v0[0]*v1[1]-v1[0]*v0[1]
  u=(v2[0]*v1[1]-v1[0]*v2[1])/den;v=(v0[0]*v2[1]-v2[0]*v0[1])/den;return a[2]*(1-u-v)+b[2]*u+c[2]*v
 for own,seg in borders:
  if footprints[own].boundary.distance(Point(seg[:,:2].mean(0)))>2e-6:
   internal_caps.append({'name':names[own],'segment':seg.tolist()});continue
  length=np.linalg.norm(seg[1,:2]-seg[0,:2]);K=max(1,int(math.ceil(length/.15)))
  for a in np.linspace(0,1,K+1):
   xyz=seg[0]*(1-a)+seg[1]*a;pt=Point(xyz[:2]);ids=tree.query(pt.buffer(tol));ids=ids[owner[ids]!=own]
   if not len(ids):
    if edge.distance(pt)>tol*2:unmatched.append({'name':names[own],'XYZ':xyz.tolist(),'nearest_domain_boundary_m':edge.distance(pt)})
    continue
   distances=shapely.distance(pg[ids],pt);ids=ids[distances<=tol]
   if not len(ids):
    if edge.distance(pt)>tol*2:unmatched.append({'name':names[own],'XYZ':xyz.tolist(),'nearest_domain_boundary_m':edge.distance(pt)})
    continue
   values=np.array([z_at(tr[int(i)],xyz[:2]) for i in ids]);delta=abs(values-xyz[2]);worst=int(delta.argmax());case={'name':names[own],'other':names[int(owner[ids[worst]])],'XYZ':xyz.tolist(),'step_m':float(delta[worst]),'XY_gap_m':float(shapely.distance(pg[ids[worst]],pt))};results.append(case)
   if own==rampid or np.any(owner[ids]==rampid):rampcases.append(case)
 ga=np.array([-14.78814941727704,-8.672411229164949]);gb=np.array([-12.691036702414301,-12.516460251600984]);gd=gb-ga;gw=np.linalg.norm(gd);gd/=gw;gin=np.array([-gd[1],gd[0]]);rampedges={'road_front_v_minus_2m':[],'left_side_u_zero':[],'right_side_u_gatewidth':[],'yard_back_v_plus_0_9m':[]}
 for rr in rampcases:
  xyz=np.array(rr['XYZ']);u=(xyz[:2]-ga)@gd;v=(xyz[:2]-ga)@gin
  for k,yes in [('road_front_v_minus_2m',abs(v+2)<3e-6),('left_side_u_zero',abs(u)<3e-6),('right_side_u_gatewidth',abs(u-gw)<3e-6),('yard_back_v_plus_0_9m',abs(v-.9)<3e-6)]:
   if yes:rampedges[k].append(rr)
 ramp_edge_summary={k:{'samples':len(rows),'maximum_step_m':max((r['step_m'] for r in rows),default=None),'maximum_XY_gap_m':max((r['XY_gap_m'] for r in rows),default=None)} for k,rows in rampedges.items()}
 ordered=sorted(results,key=lambda r:r['step_m'],reverse=True);rordered=sorted(rampcases,key=lambda r:r['step_m'],reverse=True)
 q={'mutation_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'numerically_degenerate_XY_triangles_excluded':discarded,'within_panel_edges_excluded_from_interpanel_seam_audit':len(internal_caps),'within_panel_edge_examples':internal_caps[:8],'sample_spacing_m_max':.15,'seam_evaluated_samples':len(results),'unmatched_internal_boundary_samples':len(unmatched),'maximum_seam_height_step_m':ordered[0]['step_m'] if ordered else None,'maximum_seam_XY_gap_m':max((r['XY_gap_m'] for r in results),default=None),'ramp_seam_evaluated_samples':len(rampcases),'ramp_edge_classified_summary':ramp_edge_summary,'maximum_ramp_boundary_step_m':rordered[0]['step_m'] if rordered else None,'largest_height_mismatches':ordered[:12],'largest_ramp_mismatches':rordered[:12],'unmatched_examples':unmatched[:12]}
 q['status']='PASS' if len(results)>1000 and not unmatched and q['maximum_seam_height_step_m']<.001 and q['maximum_ramp_boundary_step_m']<.001 else 'FAIL';return q
before=audit(D/'Mutation_Before_Seam_Repair.json');print('BEFORE',before['status'],before['maximum_seam_height_step_m'],before['maximum_ramp_boundary_step_m'],flush=True)
after=audit(D/'Mutation.json');print('AFTER',after['status'],after['maximum_seam_height_step_m'],after['maximum_ramp_boundary_step_m'],after['unmatched_internal_boundary_samples'],flush=True)
(D/'Terrain_Seam_Continuity_QA.json').write_text(json.dumps({'status':after['status'],'before':before,'after':after,'method':'Actual top boundary edges sampled <=0.15m, adjacent triangle XY query then independent barycentric z-height comparison. Exclude numerically unstable triangles with projected minimum altitude <=1e-5m (prevents false multi-kilometre interpolation) and distinguish within-panel T-junction caps from actual interpanel boundaries. Check source outer perimeter excluded; all internal boundaries must find opposing terrain top.'},indent=2))
