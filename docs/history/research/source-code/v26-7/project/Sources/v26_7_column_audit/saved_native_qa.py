from pathlib import Path
import sys,json,hashlib
W=Path(__file__).resolve().parents[1];sys.path[:0]=[str(W/'np1'),str(W/'geomlibs'),str(W)]
import numpy as np,manifold3d as mf
from v24_16_common import solid,union,cube
D=W/'v26_7/Final';FD=W/'v26_6/Final';PD=W/'v26_1'
J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))}
prep=json.loads((W/'v26_7_column_audit/final_candidate/Prepared_Geometry.json').read_text('utf8'));N={r['name']:r for r in json.loads((D/'Geometry_Index.json').read_text('utf8'))};HN='V26_3_House_Connected_Walls_And_Stairs'
old=np.load(FD/J[HN]['file']);new=np.load(D/N[HN]['file']);before=solid(old['v'],old['f']);after=solid(new['v'],new['f'])
checks=[]
def ck(n,b,**kw):checks.append({'check':n,'pass':bool(b),**kw});print(n,bool(b),kw if not b else'',flush=True)
ck('Candidate house is one positive closed solid',after.status()==mf.Error.NoError and after.volume()>0 and len(after.decompose())==1,components=len(after.decompose()),volume_m3=after.volume())
v,ix=np.unique(new['v'],axis=0,return_inverse=True);f=ix[new['f']];tr=v[f];ar=np.linalg.norm(np.cross(tr[:,1]-tr[:,0],tr[:,2]-tr[:,0]),axis=1)/2;edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1);_,ct=np.unique(edges,axis=0,return_counts=True)
duplicates=len({tuple(sorted(map(tuple,t)))for t in tr})!=len(tr)
ck('Saved candidate triangles have no zero area duplicate or nonmanifold edge',ar.min()>1e-18 and not duplicates and bool((ct==2).all()),minimum_triangle_area_m2=float(ar.min()),nonmanifold_edges=int((ct!=2).sum()),duplicate_faces=duplicates)
cp=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components']
def inside(m,p):
 p=np.array(p);d=np.array([40.,0,0]);hs=m.ray_cast(p-d,p+d);return sum(h.position[0]<p[0]for h in hs)%2==1
columns=[]
for r in cp:
 n=r['name']
 if not n.startswith('KZ_'):continue
 lo,hi=np.array(r['bounds_m']);cx,cy=(lo+hi)[:2]/2;z=lo[2]+.6;rr=[]
 for sx in[-1,1]:
  for sy in[-1,1]:
   x,y=cx+sx*.16,cy+sy*.16
   if x<.12 or x>12.88 or y<2.22 or y>9.68:continue
   p=[float(x),float(y),float(z)];rr.append({'point_m':p,'before_occupied':inside(before,p),'after_occupied':inside(after,p)})
 columns.append({'name':n,'probes':rr})
bad=[{'name':r['name'],**q}for r in columns for q in r['probes']if q['after_occupied']]
ck('All35 synthetic column ordinary room quadrants are flush to regular wall strips',not bad,columns=len(columns),probe_count=sum(len(r['probes'])for r in columns),failures=bad)
protected=[]
for n in prep['protected_stair_names']:
 a=np.load(PD/PI[n]['file']);m=solid(a['v'],a['f']);loss_before=max(0.,(m-before).volume());loss_after=max(0.,(m-after).volume());protected.append({'name':n,'missing_before_m3':loss_before,'missing_after_m3':loss_after,'increased_loss_m3':loss_after-loss_before})
ck('All four stair flights and both landings including bearing tongues are preserved',all(r['increased_loss_m3']<2e-7 for r in protected),components=protected)
# The build canonicalizes Boolean boxes to native float32. Use those same
# coordinates so a submicrometre boundary strip is not counted as lost beam.
side_allowed=union([cube(np.asarray(r['bounds_m'][0],np.float32).astype(float),np.asarray(r['bounds_m'][1],np.float32).astype(float)) for r in prep['finalize']['stair_frame_wall_side_normalization']])
beam=[]
head_allow=cube([.1998,9.6798,-.4501],[12.8002,9.9004,10.2202])
head_allow+=union([p for soffit,top in[(3.0499,3.4501),(6.6499,7.0501),(9.9499,10.2201)]for p in[cube([3.7799,7.4199,soffit],[4.0201,9.6801,top]),cube([4.0199,7.1799,soffit],[7.8001,7.4201,top]),cube([4.0199,9.6799,soffit],[8.9801,9.9003,top]),cube([8.9799,7.4199,soffit],[9.2201,9.6801,top])]])
for r in cp:
 n=r['name']
 if not n.startswith(('BEAM_','V26_Stair_Frame_')):continue
 lo,hi=np.array(r['bounds_m'])
 if n in PI:
  a=np.load(PD/PI[n]['file']);m=solid(a['v'],a['f'])
 else:m=cube(lo,hi)
 kept=before^m;loss=max(0.,((kept-after)-side_allowed).volume());regrowth=max(0.,(((after^m)-before)-head_allow).volume());beam.append({'name':n,'native_geometry_lost_m3':loss,'new_source_core_regrowth_m3':regrowth})
ck('Cross-room beam downstands stay intact outside authorized wall-side face normalization',all(r['native_geometry_lost_m3']<2e-7 for r in beam)and all(r['new_source_core_regrowth_m3']<2e-7 for r in beam),components=beam)
# Actual tread tops and landing planes are checked independently of source-solid containment.
walk=[];bad=[]
for fl,z0 in[(1,-.45),(2,3.45)]:
 for y in[8.0,9.05]:
  for x in np.arange(5.265,7.8,.13):
   hs=[h for h in before.ray_cast([float(x),y,z0+3.94],[float(x),y,z0-.3])if h.normal[2]>.9]
   # Ceiling and upper slab are above3.45 and7.05; choose first actual stair top below it.
   hs=[h for h in hs if h.position[2]<z0+3.89]
   if not hs:continue
   top=max(h.position[2]for h in hs);newhits=[h for h in after.ray_cast([float(x),y,top+.03],[float(x),y,top-.03])if h.normal[2]>.9];got=max((h.position[2]for h in newhits),default=-999.)
   r={'floor':fl,'x_m':float(x),'y_m':y,'before_top_m':float(top),'after_top_m':float(got)};walk.append(r)
   if abs(top-got)>.0001:bad.append(r)
 for z,yspan in[(1.5 if fl==1 else 5.25,[7.7,8.3,9.25])]:
  for y in yspan:
   x=4.6;hs=[h for h in after.ray_cast([x,y,z+.03],[x,y,z-.03])if h.normal[2]>.9];got=max((h.position[2]for h in hs),default=-999.);r={'floor':fl,'landing':True,'x_m':x,'y_m':y,'expected_m':z,'actual_m':got};walk.append(r)
   if abs(z-got)>.0001:bad.append(r)
ck('Actual stair and landing walking surfaces have no new trench or changed elevation',not bad,samples=len(walk),failures=bad)
east=[]
for lo,hi in[([7.8001,7.42,3.3201],[9.22,9.6799,3.4499]),([7.8001,7.42,6.9201],[9.22,9.6799,7.0499])]:
 m=cube(lo,hi);lost=max(0.,((before^m)-after).volume());east.append({'bounds_m':[lo,hi],'lost_m3':lost})
ck('East upper arrival walking floor is intact',all(r['lost_m3']<2e-7 for r in east),regions=east)
rear=[];bad=[]
for fl,base in[(1,-.45),(2,3.45),(3,7.05)]:
 for x in[.6,1.4,2.35,3.55,8.6,9.55,10.2,10.95,12.4]:
  z=base+.3;hs=sorted(after.ray_cast([x,9.45,z],[x,10.15,z]),key=lambda h:h.position[1]);ent=[h for h in hs if h.normal[1]<-.9]
  got=float(ent[0].position[1])if ent else None;r={'floor':fl,'x_m':x,'z_m':z,'inner_y_m':got};rear.append(r)
  if got is None or abs(got-9.68)>.00004:bad.append(r)
ck('All ordinary audited rear underwindow panels have flatY9.68 inner face',not bad,samples=rear,failures=bad)
headers=[]
for fl,ztop in[(1,3.32),(2,6.92),(3,10.22)]:
 for k in[1,2,3]:
  wn=f'WINDOW_BACK_F{fl}_{k}_Geometry';lo,hi=np.array(J[wn]['bounds']);zt=10.02 if fl==3 and k==1 else ztop
  expected=cube([lo[0]+.006,9.70,hi[2]+.002],[hi[0]-.006,9.88,zt-.002]);miss=max(0.,(expected-after).volume());headers.append({'window':wn,'missing_solid_m3':miss})
ck('All rear window heads remain continuously closed to existing ceiling',all(r['missing_solid_m3']<1e-7 for r in headers),windows=headers)
glass=[]
for n,r in J.items():
 if not n.startswith('WINDOW_BACK_'):continue
 a=np.load(FD/r['file']);m=solid(a['v'],a['f']);oldover=max(0.,(m^before).volume());newov=max(0.,(m^after).volume());glass.append({'name':n,'before_overlap_m3':oldover,'after_overlap_m3':newov,'increased_overlap_m3':newov-oldover})
ck('No rear native glass or frame gains wall obstruction',all(r['increased_overlap_m3']<2e-7 for r in glass),windows=glass)
sills=[]
for n,r in N.items():
 if not n.startswith('CONSTRUCTION_SILL_WINDOW_BACK_'):continue
 wn=n.replace('CONSTRUCTION_SILL_','');a=np.load(D/r['file']);lo,hi=np.array(J[wn]['bounds']);slo=a['v'].min(0);shi=a['v'].max(0);sills.append({'name':n,'pass':bool(slo[0]>=lo[0]-2e-6 and shi[0]<=hi[0]+2e-6),'actual_x_m':[float(slo[0]),float(shi[0])],'window_x_m':[float(lo[0]),float(hi[0])]})
ck('Upper rear sill and head ends stay within original window jambs',all(r['pass']for r in sills),components=sills)
ck('No native door frame leaf or glazing object is replaced',not any(r['name'].startswith(('DOOR_','WINDOW_','BAY_WINDOW_'))for r in prep['objects']),replacement_names=[r['name'] for r in prep['objects']])
added=after-before
stairwell=union([cube([4.0201,7.4201,-.4499],[8.9799,9.6799,3.32]),cube([4.0201,7.4201,3.4501],[8.9799,9.6799,6.92]),cube([4.0201,7.4201,7.0501],[8.9799,9.6799,10.02])]);fill=max(0.,(added^stairwell).volume())
ck('No new stairwell volume was blanket filled',fill<2e-6,added_inside_stairwell_m3=fill)
# Verify actual added volumes remain within the requested220.2mm rear carrier.
allowed=union([cube([.1999,9.6799,-.4501],[12.8001,9.9003,3.3201]),cube([.1999,9.6799,3.4500],[12.8001,9.9003,6.9201]),cube([.1999,9.6799,7.0500],[12.8001,9.9003,10.2201])]);allowed+=union([p for soffit,top in[(3.0499,3.4501),(6.6499,7.0501),(9.9499,10.2201)]for p in[cube([3.7799,7.4199,soffit],[4.0201,9.6801,top]),cube([4.0199,7.1799,soffit],[7.8001,7.4201,top]),cube([4.0199,9.6799,soffit],[8.9801,9.9003,top]),cube([8.9799,7.4199,soffit],[9.2201,9.6801,top])]]);outside=max(0.,(added-allowed).volume())
ck('New closure volume stays in thin wall and header carriers',outside<2e-6,outside_added_volume_m3=outside,total_added_volume_m3=added.volume())

profiles=[]
for fl,base,top in[(1,-.45,3.32),(2,3.45,6.92),(3,7.05,10.02)]:
 for z in[base+.6,base+2.0,top-.10]:
  for side,start,end,axis,expected in[
   ('west',[4.3,8.4,z],[3.6,8.4,z],0,4.02),
   ('south',[4.3,7.7,z],[4.3,7.0,z],1,7.42),
   ('north',[6.5,9.60,z],[6.5,10.05,z],1,9.68),
   ('east',[8.7,9.3,z],[9.4,9.3,z],0,9.0 if fl==1 else 8.98)]:
   oldhits=before.ray_cast(start,end);hs=after.ray_cast(start,end);hit=hs[0]if hs else None;got=float(hit.position[axis])if hit else None;opening=not oldhits;profiles.append({'floor':fl,'side':side,'z_m':z,'source_aperture':opening,'expected_plane_m':None if opening else expected,'actual_plane_m':got,'pass':got is None if opening else got is not None and abs(got-expected)<.00005})
ck('Full-height hall wall planes have no obsolete beam-end tabs',all(r['pass']for r in profiles),samples=profiles)

fail=[r for r in checks if not r['pass']]
with(D/N[HN]['file']).open('rb')as f:ch=hashlib.file_digest(f,'sha256').hexdigest()
out={'status':'PASS'if not fail else'FAIL','source_model_sha256':prep['source_sha256'],'model_sha256':hashlib.sha256(Path('E:/jz/JIA/Rebuild_V26_7/Blender/Architecture_Complete_V26_7.blend').read_bytes()).hexdigest(),'candidate_house_npz_sha256':ch,'checks':checks,'failures':fail,'columns':columns,'actual_section_dimension_evidence':{'verified_original400mm_column_sections':[],'note':'400mmKZsizes are synthetic source model assumptions. Photographs support ordinary plain room wall faces, small conduits/outlets and actual stair/beam underside forms; exterior and front bay-facing source silhouettes were retained, not certified as measured structure.'},'basis':'Independent source/candidate native triangles, outside-bounds containment rays, closed-solid differences, actual walking elevations, original frame obstruction and explicit added-volume locality checks.'}
(Path('E:/jz/JIA/Rebuild_V26_7/Reports')/'V26_7_Column_Projection_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=lambda v:bool(v)if isinstance(v,np.bool_)else float(v)),encoding='utf8');print('CANDIDATE_QA_DONE',len(checks),'FAIL',len(fail),flush=True)
