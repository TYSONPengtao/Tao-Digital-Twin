from v26_2_common import *
from shapely.geometry import Point
import hashlib
D=W/'v26_7';FD=D/'Final';O=Path('E:/jz/JIA/Rebuild_V26_7');R=O/'Reports';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};oldD=W/'v26_3/Final';oldJ={r['name']:r for r in json.loads((oldD/'Geometry_Index.json').read_text('utf8'))};checks=[]
def ck(n,yes,**kw):checks.append({'check':n,'pass':bool(yes),**kw});print('CHECK',n,bool(yes),kw if not yes else'',flush=True)
def get(n):
 a=np.load(FD/J[n]['file']);return a,solid(a['v'],a['f'],n)
HN='V26_3_House_Connected_Walls_And_Stairs';ha,house=get(HN);tr=ha['v'][ha['f']];norm=np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]);area=np.linalg.norm(norm,axis=1)/2;norm/=np.maximum(2*area[:,None],1e-30)
def material_at(point, hit_normal):
 # Manifold face_id denotes a merged source face, not Blender triangle order.
 # Match the actual saved triangle geometrically before reading its material.
 q=np.array(point);d=abs(np.einsum('ij,ij->i',norm,q-tr[:,0]));ids=np.flatnonzero((d<.000003)&(norm@np.asarray(hit_normal)>.999))
 for i in ids:
  a,b=tr[i,1]-tr[i,0],tr[i,2]-tr[i,0];p=q-tr[i,0];det=(a@a)*(b@b)-(a@b)**2
  if det<1e-20:continue
  s=((b@b)*(a@p)-(a@b)*(b@p))/det;t=((a@a)*(b@p)-(a@b)*(a@p))/det
  if min(s,t)>-.00001 and s+t<1.00001:return J[HN]['materials'][int(ha['mi'][i])]
 return 'NO_SAVED_SURFACE_MATCH'
ck('Saved house has one connected closed positive shell',len(house.decompose())==1 and house.volume()>0,components=len(house.decompose()),volume_m3=house.volume())
exact_keys={tuple(sorted(map(tuple,t)))for t in tr};rounded_keys={tuple(sorted(map(tuple,np.round(t,7))))for t in tr};edges=np.sort(np.vstack([ha['f'][:,[0,1]],ha['f'][:,[1,2]],ha['f'][:,[2,0]]]),axis=1);_,edge_counts=np.unique(edges,axis=0,return_counts=True)
# Exact duplicates must use the actual saved coordinates. Rounding a valid
# subpixel triangle can collapse two vertices and produce a false [A,A,B]
# key. Separate edge incidence and coplanar-area checks still guard topology.
ck('No zero-area or exactly duplicated house triangle; every edge has two incident faces',area.min()>1e-18 and len(exact_keys)==len(tr) and np.all(edge_counts==2),minimum_area_m2=float(area.min()),exact_duplicate_triangles=len(tr)-len(exact_keys),rounding_collision_diagnostic=len(tr)-len(rounded_keys),nonmanifold_edges=int(np.count_nonzero(edge_counts!=2)))
core=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components'];samples=[];bad=[]
for fl,floor in [(1,-.45),(2,3.45),(3,7.05)]:
 for dz in [.7,1.5,2.5]:
  z=floor+dz
  for axis,axes,span in [(0,[0.,3.9,9.1,13.],np.arange(2.6,9.55,.19)),(1,[2.1,7.3,9.8],np.arange(.4,12.7,.19))]:
   for center in axes:
    for u in span:
     # Perpendicular wall intersections are the explicit corner exception.
     if min(abs(u-b)for b in ([2.1,7.3,9.8]if axis==0 else[0.,2.2,3.9,9.1,10.65,10.8,13.]))<.235:continue
     p=np.array([center,u,z])if axis==0 else np.array([u,center,z]);iscore=False
     for c in core:
      if not c['name'].startswith(('KZ_','BEAM_')):continue
      lo,hi=np.array(c['bounds_m'])
      if np.all(p>lo-.001)and np.all(p<hi+.001):iscore=True;break
     if iscore:continue
     delta=np.eye(3)[axis]*.54;hits=sorted(house.ray_cast(p-delta,p+delta),key=lambda h:h.position[axis]);found=[]
     for h0,h1 in zip(hits,hits[1:]):
      if h0.normal[axis]<-.8 and h1.normal[axis]>.8 and h0.position[axis]<=center+.001 and h1.position[axis]>=center-.001:found.append(float(h1.position[axis]-h0.position[axis]))
     if not found:continue
     q={'floor':fl,'axis':axis,'point_m':p.tolist(),'thickness_m':max(found)};samples.append(q)
     if max(found)>.24001:bad.append(q)
ck('Every audited ordinary wall span is at most 240 mm',not bad,samples=len(samples),maximum_m=max(q['thickness_m']for q in samples),invalid=bad[:30])
# Room relations are checked separately from thickness.
separation=[]
for axis,pairs in [(0,[(10.35,y,1.)for y in [7.8,8.3,9.1]]),(1,[(x,6.9,1.)for x in [9.55,9.9,10.3]])]:
 for p in pairs:
  p=np.array(p);end=p+np.eye(3)[axis]*.65;hs=house.ray_cast(p,end);separation.append({'axis':axis,'point':p.tolist(),'hits':len(hs),'thickness':float(np.linalg.norm(np.array(hs[-1].position)-hs[0].position))if len(hs)==2 else None})
ck('F1 bedroom is separated from stair-facing WC and the WC zones remain divided',all(r['hits']==2 for r in separation),samples=separation)
ck('F1 WC divider remains 100 mm',all(abs(r['thickness']-.1)<.0005 for r in separation if r['axis']==0),samples=separation[:3])
doors=[]
for n in ['DOOR_KITCHEN_F1__FRAME_Geometry','DOOR_BATH_F1_R__FRAME_Geometry']:
 a=np.load(FD/J[n]['file']);lo=a['v'].min(0);hi=a['v'].max(0);ax=int(np.argmin((hi-lo)[:2]));p=(lo+hi)/2;p[2]=.6;hs=house.ray_cast(p-np.eye(3)[ax]*.4,p+np.eye(3)[ax]*.4);doors.append({'door':n,'opaque_hits':len(hs),'frame_depth_m':float(hi[ax]-lo[ax])})
ck('Both independent F1 WC doorway centres remain open with thin linings',all(r['opaque_hits']==0 and r['frame_depth_m']<=.24001 for r in doors),doors=doors)
front=[]
for fl,z0 in [(1,-.45),(2,3.45),(3,7.05)]:
 for x in [.5,1.2,1.9,11.,11.8,12.4]:
  for dz in [.8,1.6,2.7]:
   if fl==1 and x==11. and dz<2.1:continue
   hs=house.ray_cast([x,7.0,z0+dz],[x,7.6,z0+dz]);expect_open=fl==3 and x<3.9;front.append({'floor':fl,'x':x,'z':z0+dz,'photo_supported_F3_terrace_opening':expect_open,'closed':len(hs)==0 if expect_open else len(hs)==2})
for x in [10.695,10.699,10.701,10.705,10.71,11.1,11.4]:
 for z in [1.7,2.2,2.8]:
  hs=house.ray_cast([x,7.0,z],[x,7.38,z]);front.append({'floor':1,'x':x,'z':z,'closed':bool(hs)})
ck('WC front walls and F1 door head remain closed; photographed F3 west terrace span is open',all(q['closed']for q in front),samples=len(front),invalid=[q for q in front if not q['closed']])
ceil=[];cbad=[]
for x in np.arange(4.4,12.7,.55):
 for y in np.arange(2.6,9.5,.55):
  start=[float(x),float(y),8.8];hs=house.ray_cast(start,[float(x),float(y),12.])
  if not hs:cbad.append({'xy':start[:2],'reason':'no ceiling'});continue
  h=hs[0]
  if h.normal[2]>-.5:continue # ray begins in a wall/column, not clear room
  mat=material_at(h.position,h.normal);q={'xy':start[:2],'z_m':float(h.position[2]),'material':mat};ceil.append(q)
  if h.position[2]>10.2201 or mat!='M_V26_3_Neutral_White_Interior_Ceiling':cbad.append(q)
ck('F3 clear room samples have continuous flat white ceiling or existing white beam drops',not cbad,samples=len(ceil),invalid=cbad[:20])
treads=[];tbad=[];PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))}
for fl,z in [(1,-.45),(2,3.45)]:
 for flight,y in [(1,9.05),(2,8.)]:
  a=np.load(PD/PI[f'STAIR_F{fl}_FLIGHT{flight}_Geometry']['file']);original=solid(a['v'],a['f'])
  for x in np.arange(5.265,7.8,.13):
   hs=[h for h in original.ray_cast([x,y,z+3.9],[x,y,z-.3])if h.normal[2]>.8]
   if not hs:continue
   zz=max(h.position[2]for h in hs);hs=[h for h in house.ray_cast([x,y,zz+.1],[x,y,zz-.025])if h.normal[2]>.8];got=max((h.position[2]for h in hs),default=-999.);q={'floor':fl,'flight':flight,'x':float(x),'before_z':zz,'after_z':got};treads.append(q)
   if abs(zz-got)>.0005:tbad.append(q)
ck('Original stair tread elevations are retained',not tbad,samples=len(treads),invalid=tbad)
# Unsupported synthetic column projections are intentionally corrected.
# Current beam and stair retention is checked by the dedicated native column QA.
motion=json.loads((FD/'Door_Motion.json').read_text('utf8'));dbad=[]
for n,r in motion.items():
 a=np.load(FD/r['file']);leaf=solid(a['v'],a['f'],n);_,frame=get(n.replace('__LEAF_Geometry','__FRAME_Geometry'))
 for fr,matrix in r['matrices'].items():
  m=leaf.transform(np.array(matrix)[:3]);overlap=max((m^house).volume(),(m^frame).volume())
  if overlap>2e-7:dbad.append({'door':n,'frame':fr,'overlap_m3':overlap})
ck('All evaluated hinged leaves clear the corrected walls and frames',not dbad,poses=sum(len(r['matrices'])for r in motion.values()),invalid=dbad[:30])
glass=[]
for fl in [1,2]:
 for n in [f'DOOR_FRONT_CENTER_F{fl}__FIXED_Geometry',f'HOUSE_V22_FRONT_TRANSOM_F{fl}_Geometry']:
  a,m=get(n);ids=[i for i,s in enumerate(J[n]['materials'])if 'Glass'in s];sel=np.isin(a['mi'],ids);glass.append({'name':n,'glass_triangles':int(sel.sum()),'glass_area_m2':float((np.linalg.norm(np.cross(a['v'][a['f']][:,1]-a['v'][a['f']][:,0],a['v'][a['f']][:,2]-a['v'][a['f']][:,0]),axis=1)/2)[sel].sum())})
ck('Both sliding door fixed panels and transoms retain real glazing',all(q['glass_area_m2']>.1 for q in glass),glass=glass)
P=O/'Blender/Architecture_Complete_V26_7.blend'
with P.open('rb')as f:h=hashlib.file_digest(f,'sha256').hexdigest()
fail=[q for q in checks if not q['pass']];(R/'V26_7_Geometry_QA.json').write_text(json.dumps({'model_sha256':h,'status':'PASS'if not fail else'FAIL','checks':checks,'failures':fail,'wall_thickness_samples':samples,'f3_ceiling_samples':ceil,'tread_samples':treads,'basis':'Freshly reopened saved native model; geometric fit and topology only, not structural engineering certification'},ensure_ascii=False,indent=2),encoding='utf8');print('GEOMETRY_DONE',len(checks),'FAIL',len(fail),flush=True)
