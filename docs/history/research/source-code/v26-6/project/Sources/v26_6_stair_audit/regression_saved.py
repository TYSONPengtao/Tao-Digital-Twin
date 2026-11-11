from pathlib import Path
import sys,json,hashlib
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/p)for p in ['np1','geomlibs','libs']]+[str(W)]
import numpy as np,manifold3d as mf
from v24_16_common import solid,cube,union
OD=W/'v26_5/Final';ND=W/'v26_6/Final';OI={r['name']:r for r in json.loads((OD/'Geometry_Index.json').read_text('utf8'))};NI={r['name']:r for r in json.loads((ND/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs';P=Path('E:/jz/JIA/Rebuild_V26_6/Blender/Architecture_Complete_V26_6.blend');sha=hashlib.sha256(P.read_bytes()).hexdigest();expected=sys.argv[1]if len(sys.argv)>1 else sha
report={'model':str(P),'model_sha256':sha,'basis':'Independent fresh saved native mesh comparison against V26.5. Riser lower limits measured from original adjacent tread ray hits, not component bounds.','checks':[],'failures':[]}
def ck(name,value,**extra):
 r={'name':name,'pass':bool(value),**extra};report['checks'].append(r)
 if not value:report['failures'].append(r)
 print('CHECK',name,bool(value),flush=True)
def arr(D,I,n):return np.load(D/I[n]['file'])
a=arr(OD,OI,HN);b=arr(ND,NI,HN);OH=solid(a['v'],a['f'],'native old house');NH=solid(b['v'],b['f'],'native new house');ot=a['v'][a['f']];nt=b['v'][b['f']];on=np.cross(ot[:,1]-ot[:,0],ot[:,2]-ot[:,0]);nn=np.cross(nt[:,1]-nt[:,0],nt[:,2]-nt[:,0]);oa=np.linalg.norm(on,axis=1);na=np.linalg.norm(nn,axis=1);on/=np.maximum(oa[:,None],1e-30);nn/=np.maximum(na[:,None],1e-30)
def material_at(q,normal=None):
 q=np.asarray(q);dd=abs(np.einsum('ij,ij->i',nn,q-nt[:,0]));valid=dd<.000003
 if normal is not None:valid&=(nn@np.asarray(normal)>.999)
 for i in np.flatnonzero(valid):
  A=nt[i,1]-nt[i,0];B=nt[i,2]-nt[i,0];V=q-nt[i,0];aa=A@A;bb=B@B;ab=A@B;det=aa*bb-ab*ab
  if det<1e-26:continue
  aq=A@V;bq=B@V;u=(bb*aq-ab*bq)/det;v=(aa*bq-ab*aq)/det
  if min(u,v)>=-1e-6 and u+v<=1.000001:return NI[HN]['materials'][int(b['mi'][i])]
 return 'NO_MATCHING_NATIVE_SURFACE'
def top(m,x,y,lo,hi):
 hits=[h for h in m.ray_cast([x,y,hi],[x,y,lo])if h.normal[2]>.9]
 return max((float(h.position[2])for h in hits),default=None)
GRAY='M_V24_31_Stair_Gray_Marble';WHITE=['M_Wall_Interior','M_V26_3_Neutral_White_Interior_Ceiling']
ck('Saved delivery hash matches exact tested version',sha==expected)
# Direct native topology, no prepared intermediates.
edges=np.sort(np.vstack([b['f'][:,[0,1]],b['f'][:,[1,2]],b['f'][:,[2,0]]]),axis=1);_,counts=np.unique(edges,axis=0,return_counts=True);ck('Saved house is one closed solid without zero-area triangles',NH.status()==mf.Error.NoError and len(NH.decompose())==1 and bool((counts==2).all())and bool((na>0).all()),components=len(NH.decompose()),zero_area_triangles=int((na==0).sum()),nonmanifold_edges=int((counts!=2).sum()))
# Allow only the independently specified F3 west alcove physical changes.
allowed=cube([-.1001,6.9999,7.0499],[3.7101,9.9003,10.0801]);lost=OH-NH;added=NH-OH;outside_lost=(lost-allowed).volume();outside_added=(added-allowed).volume();ck('Geometry outside F3 west alcove unchanged; riser correction adds no physical layer',abs(outside_lost)<1e-7 and abs(outside_added)<1e-7,removed_outside_allowed_m3=outside_lost,added_outside_allowed_m3=outside_added,allowed_region=[[-.1001,6.9999,7.0499],[3.7101,9.9003,10.0801]])
stair_region=cube([3.74,7.15,-.7],[9.35,9.95,7.051]);stair_lost=(lost^stair_region).volume();stair_added=(added^stair_region).volume();ck('All existing stair and landing solid geometry unchanged',abs(stair_lost)<1e-7 and abs(stair_added)<1e-7,stair_removed_m3=stair_lost,stair_added_m3=stair_added)
# Wood geometry, material slots and UVs are exact native originals.
wood='V26_1_Photo_Referenced_Continuous_Wood_Railing';wa=arr(OD,OI,wood);wb=arr(ND,NI,wood);same={k:bool(np.array_equal(wa[k],wb[k]))for k in['v','f','mi','uv']};ck('Photographed red timber handrail entirely unchanged',all(same.values())and OI[wood]['materials']==NI[wood]['materials'],arrays_exact=same,materials_exact=OI[wood]['materials']==NI[wood]['materials'])
# Actual last tread: probe both sides of x5.3 to rule out an extra bearing lip.
profiles=[]
for fl,lo,hi in[(1,1.2,1.6),(2,4.95,5.35)]:
 for y in[8.6,8.9,9.05,9.3,9.49]:
  for x in[5.19,5.21,5.25,5.299,5.301,5.31,5.4,5.45]:
   before=top(OH,x,y,lo,hi);after=top(NH,x,y,lo,hi);profiles.append({'floor':fl,'x':x,'y':y,'before_z':before,'after_z':after})
 bad=[r for r in profiles if r['before_z']is None or r['after_z']is None or abs(r['before_z']-r['after_z'])>1e-6]
 ck('Actual final tread and midlanding levels unchanged F'+str(fl),not bad,samples=sum(r['floor']==fl for r in profiles),invalid=bad)
 flat=[r['after_z']for r in profiles if r['floor']==fl and r['x']>5.2];ck('No added raised lip across bearing X5.3 F'+str(fl),max(flat)-min(flat)<1e-6,actual_last_tread_z_m=flat[0],range_m=max(flat)-min(flat),expected_level_note='F1 1.3227050304 m; F2 5.0863771439 m measured native source geometry')
# All four tread flights, including horizontal walking surfaces and arrivals.
treads=[]
for fl,z0,z1 in[(1,-.45,3.45),(2,3.45,7.05)]:
 for flight,y in[(1,9.05),(2,8.0)]:
  local=[]
  for x in np.arange(5.215,8.205,.071):
   before=top(OH,float(x),y,z0-.05,z1+.05)
   if before is None:continue
   after=top(NH,float(x),y,before-.01,before+.01);local.append({'x':float(x),'y':y,'before_z':before,'after_z':after})
  bad=[r for r in local if r['after_z']is None or abs(r['after_z']-r['before_z'])>1e-6];ck(f'Complete flight tread elevations retained F{fl} flight{flight}',not bad,samples=len(local),invalid=bad);treads+=local
# Visible front bands are tested from the actual tread level all the way to landing.
band_samples=[]
for fl,lo,hi in[(1,1.2,1.6),(2,4.95,5.35)]:
 sample=[]
 for y in[8.545,8.555,8.59,8.8,9.05,9.3,9.49]:
  bottom=top(OH,5.25,y,lo,hi);upper=top(OH,5.19,y,lo,hi)
  for f in[.01,.035,.08,.15,.3,.5,.7,.9,.99]:
   z=bottom+(upper-bottom)*f;hits=[h for h in NH.ray_cast([5.24,y,z],[5.16,y,z])if h.normal[0]>.9]
   if not hits:sample.append({'y':y,'z':z,'actual_tread_z':bottom,'material':'NO_FRONT_HIT'});continue
   h=hits[0];mat=material_at(h.position,h.normal);sample.append({'y':y,'z':z,'actual_tread_z':bottom,'hit':list(h.position),'material':mat})
 bad=[r for r in sample if r['material']!=GRAY];ck('Full exposed midlanding riser gray down to actual tread F'+str(fl),not bad,samples=len(sample),invalid=bad);band_samples+=sample
for fl,z0,z1,ymax in[(1,3.32,3.45,8.50),(2,6.92,7.05,8.50)]:
 sample=[]
 for y in[7.6,7.75,7.95,8.2,ymax]:
  for f in[.01,.05,.2,.5,.8,.99]:
   z=z0+(z1-z0)*f;hits=[h for h in NH.ray_cast([7.76,y,z],[7.85,y,z])if h.normal[0]<-.9];mat=material_at(hits[0].position,hits[0].normal)if hits else'NO_FRONT_HIT';sample.append({'y':y,'z':z,'material':mat})
 bad=[r for r in sample if r['material']!=GRAY];ck('Upper floor arrival gray walking front F'+str(fl),not bad,samples=len(sample),invalid=bad);band_samples+=sample
# Source white downward-facing stair/floor undersides remain white; no global gray paint.
centres=ot.mean(1);sel=(on[:,2]<-.25)&(centres[:,0]>3.8)&(centres[:,0]<9.3)&(centres[:,1]>7.25)&(centres[:,1]<9.7)&(centres[:,2]>-.7)&(centres[:,2]<7.05)&(oa>1e-9);unders=[]
for i in np.flatnonzero(sel):
 oldmat=OI[HN]['materials'][int(a['mi'][i])]
 if oldmat not in WHITE:continue
 mat=material_at(centres[i],on[i]);unders.append({'source_triangle':int(i),'point_m':centres[i].tolist(),'before_material':oldmat,'after_material':mat})
bad=[r for r in unders if r['before_material']!=r['after_material']];ck('Original white stair and slab undersides retain exact material ownership',bool(unders)and not bad,samples=len(unders),invalid=bad)
# Traceability of real-image evidence; copy integrity is checked without generating new reference images.
refdir=Path(__file__).parent/'References';refs=json.loads((refdir/'Reference_Index.json').read_text('utf8'));rbad=[]
for r in refs['references']:
 fn=refdir/r['file'];got=hashlib.sha256(fn.read_bytes()).hexdigest()
 if got!=r['sha256']:rbad.append({'file':str(fn),'hash_mismatch':True})
ck('Six actual image references and extracted video times traceable and intact',len(refs['references'])==6 and not rbad,count=len(refs['references']),video=refs['video'],invalid=rbad,finish_basis='Gray patterned walking faces supported by real images; geological stone species not inferred; white soffits remain white')
report['native_last_tread_profiles']=profiles;report['walking_front_samples']=band_samples;report['white_underside_samples']=unders;report['status']='PASS'if not report['failures']else'FAIL';report['check_count']=len(report['checks']);out=Path('E:/jz/JIA/Rebuild_V26_6/Reports/V26_6_Stair_Finish_Regression_QA.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print('STAIR_FINISH_REGRESSION',report['status'],report['check_count'],len(report['failures']),flush=True)
