from v26_2_common import *
import v26_2_common as C
native_cube=cube
def cube(lo,hi):
 return native_cube(np.asarray(lo,np.float32).astype(float),np.asarray(hi,np.float32).astype(float))
B=W/'v26_7_column_audit/candidate_broad';D=W/'v26_7_column_audit/final_candidate';D.mkdir(exist_ok=True);C.D=D
FD=W/'v26_6/Final';J={r['name']:r for r in json.loads((FD/'Geometry_Index.json').read_text('utf8'))};prep=json.loads((B/'Prepared_Geometry.json').read_text('utf8'));HN='V26_3_House_Connected_Walls_And_Stairs';r=next(r for r in prep['objects']if r['name']==HN);a=np.load(B/r['file']);house=tracked(a['v'],a['f'],r['materials'],a['mi'],a['uv'],HN)
old=np.load(FD/J[HN]['file']);before=solid(old['v'],old['f']);PD=W/'v26_1';PI={r['name']:r for r in json.loads((PD/'Geometry_Index.json').read_text('utf8'))};cp=json.loads((W/'v26_3/Prepared_House.json').read_text('utf8'))['proof']['retained_core_components']
beams=[]
for p in cp:
 n=p['name']
 if not n.startswith(('BEAM_','V26_Stair_Frame_')):continue
 lo,hi=np.array(p['bounds_m'])
 if n in PI:
  a=np.load(PD/PI[n]['file']);m=solid(a['v'],a['f'])
 else:m=cube(lo,hi)
 beams.append(before^m)
kept=union(beams);lost=kept-house
print('RESTORE_CURRENT_BEAM_LOSS',lost.volume(),flush=True)
if lost.volume()>1e-10:house+=finish(lost,'M_Wall_Interior','Current native photographed beam downstands retained')
headers=[]
for fl,ztop in[(1,3.32),(2,6.92),(3,10.22)]:
 for k in[1,2,3]:
  n=f'WINDOW_BACK_F{fl}_{k}_Geometry';lo,hi=np.array(J[n]['bounds']);zt=10.02 if fl==3 and k==1 else ztop
  head=cube([lo[0],9.68,hi[2]],[hi[0],9.9002,zt]);add=head-house
  if add.volume()>1e-10:house+=finish(add,'M_Wall_Interior','Thin regular rear window head closure')
  headers.append({'window':n,'closure_volume_m3':add.volume()})
# The generic retained-beam masks also retained the obsolete inward side of
# the synthetic stair-frame beams. Align only those wall-side faces, keeping
# all true cross-room headers, their downstand elevations and walking support.
stair_names=[f'STAIR_F{fl}_FLIGHT{k}_Geometry'for fl in[1,2]for k in[1,2]]+[f'STAIR_LANDING_F{fl}_Geometry'for fl in[1,2]]
sp=[]
for n in stair_names:
 aa=np.load(PD/PI[n]['file']);sp.append(solid(aa['v'],aa['f']))
eastwalk=union([cube([7.7998,7.2799,3.3199],[9.3004,9.8201,3.4502]),cube([7.7998,7.2799,6.9199],[9.3004,9.8201,7.0502])]);walk_protect=union(sp)+eastwalk;sidecuts=[]
for fl,z0,z1 in[(1,-.45,3.4515),(2,3.45,7.0515),(3,7.05,10.22005)]:
 ex=9.0 if fl==1 else 8.98
 for label,lo,hi in[
  ('west',[4.02,7.42,z0+.0001],[4.15,9.68,z1]),
  ('south',[4.02,7.42,z0+.0001],[7.8,7.55,z1]),
  ('north',[4.02,9.55,z0+.0001],[7.8,9.68,z1]),
  ('east',[8.85,7.42,z0+.0001],[ex,9.68,z1])]:
  c=cube(lo,hi)-walk_protect;b=c.to_mesh64();vv0=np.array(b.vert_properties[:,:3]);ff0=np.array(b.tri_verts);tt0=vv0[ff0];nn0=np.cross(tt0[:,1]-tt0[:,0],tt0[:,2]-tt0[:,0]);mi0=(nn0[:,2]>0).astype(np.int32)
  loss=(house^c).volume()
  if loss>1e-10:house-=tracked(vv0,ff0,['M_Wall_Interior','M_V26_3_Neutral_White_Interior_Ceiling'],mi0,name='Normalize inherited stair frame beam wall-side projection')
  sidecuts.append({'floor':fl,'side':label,'bounds_m':[lo,hi],'removed_m3':loss})
print('FINAL_STAIR_FRAME_SIDE_NORMALIZATION',sum(r['removed_m3']for r in sidecuts),flush=True)
# The old wall / beam sources also leave recessed header corners behind their
# shortened side faces. Close only these above-opening regular wall carriers,
# through the floor joint; never fill any actual door or glass opening.
regular_headers=[]
for fl,soffit,top in[(1,3.05,3.45),(2,6.65,7.05),(3,9.95,10.22)]:
 ex0,ex1=(9.,9.2)if fl==1 else(8.98,9.22)
 carrier=union([cube([3.78,7.42,soffit],[4.02,9.68,top]),cube([4.02,7.18,soffit],[7.8,7.42,top]),cube([4.02,9.68,soffit],[8.98,9.9002,top]),cube([ex0,7.42,soffit],[ex1,9.68,top])])
 for n,wr in J.items():
  if not n.startswith(('WINDOW_','DOOR_')) or f'_F{fl}'not in n:continue
  lo,hi=np.array(wr['bounds'])
  if hi[2]<=soffit or lo[2]>=top:continue
  opening=cube(lo-[.00001,.00001,.00001],hi+[.00001,.00001,.00001]);carrier=carrier-opening
 add=carrier-house
 if add.volume()>1e-10:house+=finish(add,'M_Wall_Interior','Continuous ordinary-thickness wall header at inherited wall/beam/floor junction')
 regular_headers.append({'floor':fl,'added_m3':add.volume(),'wall_widths_m':[.24,.24,.2202,ex1-ex0],'soffit_m':soffit,'top_m':top})
for tol in[0.000001]:
 candidate=house.simplify(tol);row,saved=export(HN,candidate,'Photo referenced ordinary room column faces and stair wall ledges corrected; rear sill/head carriers regular; existing stairs and actual beam downstands retained')
 aa=np.load(D/row['file']);t=aa['v'][aa['f']];area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2
 edges=np.sort(np.concatenate([aa['f'][:,[0,1]],aa['f'][:,[1,2]],aa['f'][:,[2,0]]]),axis=1);_,ct=np.unique(edges,axis=0,return_counts=True)
 duplicates=len(t)-len({tuple(sorted(map(tuple,q)))for q in t})
 print('EXPORT_TRIAL',tol,len(t),float(area.min()),duplicates,int((ct!=2).sum()),flush=True)
 if area.min()>1e-18 and not duplicates and np.all(ct==2):break
# Float32-native export can make very thin Boolean boundary fans collinear.
# Collapse only a shortest zero-face edge, keeping a source vertex where
# possible. No inserted wall, stair level or global remesh is introduced.
vv=aa['v'].copy();ff=aa['f'].copy();mm=aa['mi'].copy();uu=aa['uv'].copy();repairs=[];sourceverts={tuple(p)for p in old['v']}
for step in range(200):
 tt=vv[ff];ar=np.linalg.norm(np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]),axis=1)/2;bad=np.flatnonzero(ar<=1e-18)
 if not len(bad):break
 face=ff[bad[0]];edges0=[(int(face[i]),int(face[(i+1)%3]))for i in range(3)];edges0.sort(key=lambda e:np.linalg.norm(vv[e[0]]-vv[e[1]]))
 picked=None
 for i,j in edges0:
  length=float(np.linalg.norm(vv[i]-vv[j]))
  pure_collinear=False
  if length>.002:
   plane_error=0.
   for src,dst in[(i,j),(j,i)]:
    st=vv[ff[np.any(ff==src,axis=1)]];sn=np.cross(st[:,1]-st[:,0],st[:,2]-st[:,0]);sz=np.linalg.norm(sn,axis=1);good=sz>1e-18
    if good.any():plane_error=max(plane_error,float(np.max(abs(np.einsum('ij,ij->i',sn[good]/sz[good,None],vv[dst]-st[good,0])))))
   pure_collinear=plane_error<1e-8
   if not pure_collinear:continue
  ni=set(ff[np.any(ff==i,axis=1)].ravel())-{i,j};nj=set(ff[np.any(ff==j,axis=1)].ravel())-{i,j}
  if len(ni&nj)!=2:continue
  picked=(i,j,length,pure_collinear);break
 assert picked is not None,('No safe local zero-face edge collapse',step,tt[bad[0]].tolist())
 i,j,length,pure_collinear=picked
 if tuple(vv[j])in sourceverts and tuple(vv[i])not in sourceverts:i,j=j,i
 ff[ff==j]=i;keep=np.array([len(set(q))==3 for q in ff]);ff=ff[keep];mm=mm[keep];uu=uu[keep];repairs.append({'kept_point_m':vv[i].tolist(),'discarded_point_m':vv[j].tolist(),'edge_length_m':length,'plane_preserving_collinear':pure_collinear})
else:raise RuntimeError('Too many collapsed boundary edges')
vv,vi=np.unique(vv,axis=0,return_inverse=True);ff=vi[ff]
from collections import defaultdict
groups=defaultdict(list)
for i,face in enumerate(ff):groups[tuple(sorted(face))].append(i)
keep=np.ones(len(ff),bool);internal_removed=[]
for ids in groups.values():
 if len(ids)==1:continue
 assert len(ids)==2
 t0,t1=vv[ff[ids[0]]],vv[ff[ids[1]]];n0=np.cross(t0[1]-t0[0],t0[2]-t0[0]);n1=np.cross(t1[1]-t1[0],t1[2]-t1[0]);assert n0@n1<0,('Same-facing repeated surface',ids)
 keep[ids]=False;internal_removed+=ids
ff=ff[keep];mm=mm[keep];uu=uu[keep]
used,rev=np.unique(ff.ravel(),return_inverse=True);vv=vv[used];ff=rev.reshape(-1,3);ss=solid(vv,ff,'Final exact local edge collapse');tt=vv[ff];nn=np.cross(tt[:,1]-tt[:,0],tt[:,2]-tt[:,0]);ar=np.linalg.norm(nn,axis=1)/2;ed=np.sort(np.concatenate([ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]]),axis=1);_,ct=np.unique(ed,axis=0,return_counts=True)
assert ar.min()>1e-18 and np.all(ct==2) and len({tuple(sorted(q))for q in ff})==len(ff)
white_index=row['materials'].index('M_Wall_Interior');ceiling_index=row['materials'].index('M_V26_3_Neutral_White_Interior_Ceiling');down=(nn[:,2]/(2*ar)<-.7)&(tt.mean(1)[:,2]>-.4)&(mm==white_index);mm[down]=ceiling_index
np.savez_compressed(D/row['file'],v=vv,f=ff,mi=mm,uv=uu);row.update(triangles=len(ff),volume_m3=ss.volume(),closed_components=len(ss.decompose()));saved=ss
print('LOCAL_ZERO_FACE_REPAIR',len(repairs),'maximum_edge_m',max((q['edge_length_m']for q in repairs),default=0.),flush=True)
import shutil
for rr in prep['objects']:
 if rr['name']!=HN:shutil.copy2(B/rr['file'],D/rr['file'])
prep['objects']=[row if rr['name']==HN else rr for rr in prep['objects']];prep['finalize']={'beam_loss_restored_before_side_normalization_m3':lost.volume(),'window_heads':headers,'stair_frame_wall_side_normalization':sidecuts,'regular_wall_header_closure':regular_headers,'walking_sources_protected':stair_names,'simplification_tolerance_m':tol,'saved_geometry_checked':True,'local_float32_zero_face_repairs':repairs,'opposite_internal_duplicate_triangles_removed':internal_removed,'new_downward_plaster_faces_assigned_original_white_ceiling_material':int(down.sum())}
(D/'Prepared_Geometry.json').write_text(json.dumps(prep,ensure_ascii=False,indent=2),'utf8')
print('FINAL_HOUSE_PREPARED',row['triangles'],'volume',saved.volume(),flush=True)
