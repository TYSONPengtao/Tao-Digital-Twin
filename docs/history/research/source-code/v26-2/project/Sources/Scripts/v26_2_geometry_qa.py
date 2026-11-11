from v26_2_common import *
import hashlib,re
O=Path('E:/jz/JIA/Rebuild_V26_2');R=O/'Reports';FD=D/'Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};checks=[]
prepared='--prepared'in sys.argv;PR={r['name']:r for r in json.loads((D/'Prepared_House.json').read_text('utf8'))['objects']}
if prepared:
 for n,r in PR.items():
  a=np.load(D/r['file']);J[n]=dict(r,bounds=[a['v'].min(0).tolist(),a['v'].max(0).tolist()])
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw,flush=True)
def read(n):return np.load((D if prepared and n in PR else FD)/J[n]['file'])
HN='V26_2_House_Flush_Continuous_Finished_Shell';GN='V26_2_Continuous_Ground_And_Perimeter_Shell'
ha=read(HN);prep=json.loads((D/'Prepared_House.json').read_text('utf8'))['proof'];components=prep['components'];first=0;units=[]
for r in components:
 fs=ha['f'][first:first+r['triangles']];unit=solid(ha['v'],fs,r['name']);units.append(unit);first+=r['triangles']
house=units[0];ga=read(GN);ground=solid(ga['v'],ga['f'],GN)
ck('All seven architectural assemblies are closed positive solids',all(m.status()==mf.Error.NoError and m.volume()>0 for m in units),components=len(units),assemblies=components)
ck('Saved ground and perimeter have only the four existing closed assemblies',all(p.volume()>1e-9 for p in ground.decompose())and len(ground.decompose())==4,components=len(ground.decompose()),volume_m3=ground.volume())
old=load('V26_1_House_Continuous_Opaque_Shell');corebad=[];coretests=[];PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))}
for name in [r['name']for r in prep['retained_core_components']if r['name'].startswith(('KZ_','BEAM_'))]:
 a=np.load(PD/PI[name]['file']);core=solid(a['v'],a['f'],name);loss=max(0,(core-house).volume());coretests.append({'name':name,'difference_m3':loss})
 if loss>.0001:corebad.append(coretests[-1])
ck('All original column and beam cores remain in the finished body',not corebad,checked=len(coretests),invalid=corebad)
t=ha['v'][ha['f']];nn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);area=np.linalg.norm(nn,axis=1)/2;no=nn/np.maximum(area[:,None]*2,1e-30);c=t.mean(1)
ck('No zero-area or duplicate triangle exists in the repaired house',bool((area>1e-12).all())and len({tuple(sorted(map(tuple,np.round(tr,7))))for tr in t})==len(t),minimum_triangle_area_m2=float(area.min()),triangles=len(t))
sam=[];bad=[]
# Audit the explicit opaque zones next to the real saved window frames, using
# actual surface rays rather than assuming a successful Boolean means a flat wall.
for r in prep['actual_window_opaque_zones']:
 if 'window'not in r:continue
 name=r['window'];lo,hi=np.array(r['bounds_m']);axis=0 if name.startswith(('WINDOW_LEFT_','WINDOW_RIGHT_'))else 1;sgn=1 if name.startswith('WINDOW_LEFT_')or name.startswith('WINDOW_FRONT_')else-1;plane=hi[axis]if sgn>0 else lo[axis];other=1-axis
 for u in np.linspace(lo[other]+.025,hi[other]-.025,5):
  for z in np.linspace(lo[2]+.015,hi[2]-.015,3):
   p=(lo+hi)/2;p[axis]=plane;p[other]=u;p[2]=z;n=np.eye(3)[axis]*sgn;hits=house.ray_cast(p+n*.035,p-n*.035);enter=[h for h in hits if np.dot(h.normal,n)>.9];error=min((abs(h.position[axis]-plane)for h in enter),default=999.);q={'window':name,'zone':r['zone'],'point_m':p.tolist(),'surface_error_m':error};sam.append(q)
   if error>.0005:
    outside=house.ray_cast(p+n*.035,p+n*30);buried=bool(outside and np.dot(outside[0].normal,n)>0);q['buried_in_existing_roof_or_joint']=buried
    if not buried:bad.append(q)
ck('Every sampled sill and head opaque zone has a flat continuous finish',not bad,samples=len(sam),invalid=bad[:30])
# Retain all actual glazing apertures, including the four inset corners.
windows=[];windowbad=[]
for name,r in I.items():
 if not name.startswith(('WINDOW_LEFT_','WINDOW_RIGHT_','WINDOW_BACK_','WINDOW_FRONT_CENTER_F3')):continue
 lo,hi=np.array(r['bounds']);axis=0 if name.startswith(('WINDOW_LEFT_','WINDOW_RIGHT_'))else 1;other=1-axis;p=(lo+hi)/2
 for a,b in [(.5,.5),(.12,.12),(.12,.88),(.88,.12),(.88,.88)]:
  q=p.copy();q[other]=lo[other]+a*(hi[other]-lo[other]);q[2]=lo[2]+b*(hi[2]-lo[2]);a0=q.copy();a1=q.copy();a0[axis]-=.4;a1[axis]+=.4;hits=house.ray_cast(a0,a1);rec={'window':name,'point_m':q.tolist(),'opaque_hits':len(hits)};windows.append(rec)
  if hits:windowbad.append(rec)
ck('The finish repair does not cover any sampled actual window opening',not windowbad,samples=len(windows),invalid=windowbad)
# The third-floor front guard remains exposed. Its open stairwell is not
# converted into a solid partition by the lower-floor wall repairs.
guardbad=[];guards=[]
for x in [4.5,5.5,6.5,7.3]:
 for z in [7.35,7.8,8.15]:
  p=np.array([x,7.215,z]);probe=cube(p-.015,p+.015);vol=(house^probe).volume();guards.append({'point_m':p.tolist(),'opaque_volume_m3':vol})
  if vol>1e-8:guardbad.append(guards[-1])
ck('Third-floor front guard and stairwell remain open',not guardbad,samples=len(guards),invalid=guardbad)
# Compare every actual tread with the unmodified V26.1 source. The closure
# fills are confined to opaque walls and do not change the walk surfaces.
treadbad=[];treads=[]
for fl,z in [(1,-.45),(2,3.45)]:
 for k,y in [(2,8.0),(1,9.05)]:
  src=np.load(PD/PI[f'STAIR_F{fl}_FLIGHT{k}_Geometry']['file']);original=solid(src['v'],src['f'],'original stair')
  for x in np.arange(5.265,7.8,.13):
   h=original.ray_cast([float(x),y,z+3.9],[float(x),y,z-.3]);tops=[q for q in h if q.normal[2]>.8]
   if not tops:continue
   # Sample locally at the exact old tread, avoiding a higher floor slab.
   zz=max(q.position[2]for q in tops);h=[q for m in units for q in m.ray_cast([float(x),y,zz+.10],[float(x),y,zz-.025])];tops=[q for q in h if q.normal[2]>.8];got=max((q.position[2]for q in tops),default=-999.);rec={'floor':fl,'xy':[float(x),y],'before_z_m':zz,'after_z_m':got};treads.append(rec)
   if abs(zz-got)>.0003:treadbad.append(rec)
ck('Stair tread elevations are unchanged',not treadbad,samples=len(treads),invalid=treadbad)
# Evaluate the actual animated leaf matrices at 15 saved poses. Test against
# both the opaque house and the complete jamb/head frame solids.
motion=json.loads((FD/'Door_Motion.json').read_text('utf8'));doorbad=[];doorstats=[]
for name,r in motion.items():
 a=np.load(FD/r['file']);leaf=solid(a['v'],a['f'],name);leaf=union(leaf.decompose());frame_name=name.replace('__LEAF_Geometry','__FRAME_Geometry');a=read(frame_name);frame=solid(a['v'],a['f'],frame_name);maximum=0.;badposes=[]
 for fr,mat in r['matrices'].items():
  moved=leaf.transform(np.array(mat)[:3]);overlap=sum(max(0,(moved^m).volume())for m in units);frame_overlap=(moved^frame).volume();maximum=max(maximum,overlap,frame_overlap)
  if max(overlap,frame_overlap)>2e-7:badposes.append({'frame':int(fr),'house_overlap_m3':overlap,'frame_overlap_m3':frame_overlap})
 row={'door':name,'evaluated_poses':len(r['matrices']),'maximum_intersection_m3':maximum,'invalid_poses':badposes};doorstats.append(row)
 if badposes:doorbad.append(row)
ck('Every audited animated interior leaf clears its wall and complete frame',not doorbad,doors=len(doorstats),poses=sum(r['evaluated_poses']for r in doorstats),invalid=doorbad)
lo,hi=np.array(J['DOOR_BATH_F1_R__FRAME_Geometry']['bounds']);ll,hh=np.array(J['DOOR_BATH_F1_R__LEAF_Geometry']['bounds']);ck('Corrected first-floor glazed frame matches the actual floor and head',abs(lo[2]+.45)<3e-5 and abs(hi[2]-1.6499755)<3e-5 and abs(ll[2]+.44)<3e-5 and hh[2]<hi[2],frame_z_m=[lo[2],hi[2]],leaf_z_m=[ll[2],hh[2]])
# Ground/perimeter surfaces use one material branch across their union and
# contain no blue-brick or low-frieze material on the gallery base.
gmat=J[GN]['materials'];gt=ga['v'][ga['f']];gc=gt.mean(1);gi=ga['mi'];m=gc[:,0]>13.;m&=gc[:,1]<-8.2;m&=gc[:,2]<-.375
wrong=[int(i)for i in np.flatnonzero(m)if gmat[int(gi[i])]=='M_V24_20_Continuous_AsBuilt_Perimeter'];ck('Obsolete per-vertex brick division is absent from the repaired exterior shell',not wrong,old_attribute_shader_faces=len(wrong))
ck('Both continuous photo strata shaders are present on the actual saved shell',all(s in gmat for s in ['M_V26_2_Continuous_Exterior_Strata','M_V26_2_Continuous_Gallery_Base']))
obad=[]
for n in [s for s in J if s.startswith('V24_21_Exterior_')]:
 a=read(n);tr=a['v'][a['f']];hit=(tr[:,:,0].min(1)>12.85001)&(tr[:,:,0].max(1)<21.99999)&(tr[:,:,1].min(1)>-17.24999)&(tr[:,:,1].max(1)<-8.20001)&(tr[:,:,2].max(1)<-.36501)
 if hit.any():obad.append([n,int(hit.sum())])
ck('No obsolete low white frieze or frame remains under the gallery',not obad,invalid=obad)
P=O/'Blender/Architecture_Complete_V26_2.blend'
with P.open('rb')as fp:h=hashlib.file_digest(fp,'sha256').hexdigest()
fail=[q for q in checks if not q['pass']];out={'model_sha256':h,'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail,'window_finish_samples':sam,'glazing_aperture_samples':windows,'protected_guard_samples':guards,'tread_samples':treads,'door_sweep':doorstats,'basis':'Freshly reopened saved mesh and evaluated native animation matrices. Geometric fit only; no structural capacity certification.'};((D/'Prepared_Geometry_QA.json')if prepared else(R/'V26_2_Saved_Geometry_QA.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('GEOMETRY_QA',len(checks),'FAIL',len(fail),flush=True)
